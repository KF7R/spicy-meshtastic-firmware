"""Host regression harness for the actual added C++ helper, with mocked firmware services."""
import pathlib
import subprocess
import sys
import tempfile

root = pathlib.Path(sys.argv[1])
source = (root/'src/mesh/Router.cpp').read_text()
begin = source.index('void Router::publishDuplicateToMqtt(')
end = source.index('\n#endif\n\nvoid Router::perhapsUplinkOpaquePki', begin)
function = source[begin:end]
upstream = subprocess.check_output(['git','-C',str(root),'show','HEAD:src/mesh/Router.cpp'], text=True)
for start, stop in [('void Router::dispatchReceived(', 'void Router::publishDuplicateToMqtt('),
                    ('void Router::perhapsUplinkOpaquePki(', 'void Router::perhapsHandleReceived(')]:
    original_start = upstream.index(start)
    original_stop = upstream.index('void Router::perhapsUplinkOpaquePki(',original_start+1) if 'dispatchReceived' in start else upstream.index(stop,original_start+1)
    old = upstream[original_start:original_stop].strip()
    new = source[source.index(start):source.index(stop,source.index(start)+1)]
    if 'dispatchReceived' in start:
        new = new[:new.index('#if USERPREFS_MQTT_UPLINK_ALL_SEEN')].strip()
    assert old == new.strip(), 'Existing dispatch/opaque behavior changed'
assert source.index('passesRoutingAuthGate(p);',source.index('void Router::perhapsHandleReceived')) < source.index('if (shouldFilterReceived(p))',source.index('void Router::perhapsHandleReceived'))

ports = ['TEXT_MESSAGE_APP','TEXT_MESSAGE_COMPRESSED_APP','POSITION_APP','NODEINFO_APP','ROUTING_APP','TELEMETRY_APP','ADMIN_APP','ALERT_APP','KEY_VERIFICATION_APP','WAYPOINT_APP','STORE_FORWARD_APP','TRACEROUTE_APP','STORE_FORWARD_PLUSPLUS_APP','NEIGHBORINFO_APP','MESH_BEACON_APP']
preamble = r'''
#include <cassert>
#include <cstring>
#include <iostream>
#define MESHTASTIC_PREHOP_DROP 1
#define MESHTASTIC_EXCLUDE_BEACON 0
#define USERPREFS_EVENT_MODE 0
#define USERPREFS_BLOCK_POSITION_ON_EVENT_CHANNEL 1
enum DecodeState { DECODE_SUCCESS, DECODE_FAILURE, DECODE_OPAQUE, DECODE_FATAL, DECODE_POLICY_REJECT };
struct meshtastic_MeshPacket {
    bool via_mqtt=false; unsigned id=42; int channel=1; unsigned rx_time=0; bool has_rx_time=false;
    struct { int portnum=0; } decoded;
};
struct Pool {
    int calls=0,fail=0,live=0;
    meshtastic_MeshPacket *allocCopy(const meshtastic_MeshPacket &p) { if (++calls==fail) return nullptr; ++live; return new meshtastic_MeshPacket(p); }
    void release(meshtastic_MeshPacket *p) { if(p){--live;delete p;} }
} packetPool;
struct ModuleConfig {
    struct {bool enabled=true;} mqtt;
    bool has_neighbor_info=false; struct {bool enabled=false;} neighbor_info;
    bool has_mesh_beacon=false; struct {int flags=0;} mesh_beacon;
} moduleConfig;
struct {struct {int rebroadcast_mode=0;} device;} config;
constexpr int meshtastic_Config_DeviceConfig_RebroadcastMode_CORE_PORTNUMS_ONLY=1;
constexpr int meshtastic_ModuleConfig_MeshBeaconConfig_Flags_FLAG_LISTEN_ENABLED=1;
template<class... Ts> bool oneOf(int p,Ts... values){return ((p==values)||...);}
#define IS_ONE_OF(...) oneOf(__VA_ARGS__)
DecodeState nextState=DECODE_SUCCESS;
bool badHop=false,blocked=false;
DecodeState perhapsDecode(meshtastic_MeshPacket *p){p->channel=3;return nextState;}
bool shouldSkipHandleForPostDecodeHop(const meshtastic_MeshPacket &){return badHop;}
bool isBlockedEventCoordinatePacket(const meshtastic_MeshPacket *){return blocked;}
void stampRxTime(meshtastic_MeshPacket *p){p->rx_time=123;p->has_rx_time=true;}
struct Mqtt {
 int calls=0; void onSend(const meshtastic_MeshPacket &wire,const meshtastic_MeshPacket &decoded,int ch){++calls; assert(ch==3);assert(wire.channel==1);assert(wire.rx_time==123&&decoded.rx_time==123);}
} sink;
Mqtt *mqtt=&sink;
class Router {public:void publishDuplicateToMqtt(const meshtastic_MeshPacket *);};
'''
preamble += '\nenum {' + ','.join('meshtastic_PortNum_'+p for p in ports) + '};\n'
tests = r'''
int main(){
 Router r; meshtastic_MeshPacket p; auto original=p;
 auto reset=[](){assert(packetPool.live==0);packetPool.calls=0;packetPool.fail=0;sink.calls=0;moduleConfig=ModuleConfig{};config.device.rebroadcast_mode=0;nextState=DECODE_SUCCESS;badHop=blocked=false;mqtt=&sink;};
 reset();r.publishDuplicateToMqtt(&p);assert(sink.calls==1);assert(std::memcmp(&p,&original,sizeof(p))==0);assert(packetPool.live==0);
 for(auto state:{DECODE_FAILURE,DECODE_OPAQUE,DECODE_FATAL,DECODE_POLICY_REJECT}){reset();nextState=state;r.publishDuplicateToMqtt(&p);assert(sink.calls==0&&packetPool.live==0);}
 for(int failure:{1,2}){reset();packetPool.fail=failure;r.publishDuplicateToMqtt(&p);assert(sink.calls==0&&packetPool.live==0);}
 reset();p.via_mqtt=true;r.publishDuplicateToMqtt(&p);assert(packetPool.calls==0);p=original;
 reset();p.id=0;r.publishDuplicateToMqtt(&p);assert(packetPool.calls==0);p=original;
 reset();mqtt=nullptr;r.publishDuplicateToMqtt(&p);assert(packetPool.calls==0);
 reset();moduleConfig.mqtt.enabled=false;r.publishDuplicateToMqtt(&p);assert(packetPool.calls==0);
 reset();badHop=true;r.publishDuplicateToMqtt(&p);assert(sink.calls==0&&packetPool.live==0);
 reset();blocked=true;r.publishDuplicateToMqtt(&p);assert(sink.calls==0&&packetPool.live==0);
 reset();p.decoded.portnum=meshtastic_PortNum_NEIGHBORINFO_APP;r.publishDuplicateToMqtt(&p);assert(sink.calls==0);moduleConfig.has_neighbor_info=moduleConfig.neighbor_info.enabled=true;r.publishDuplicateToMqtt(&p);assert(sink.calls==1);p=original;
 reset();p.decoded.portnum=meshtastic_PortNum_MESH_BEACON_APP;r.publishDuplicateToMqtt(&p);assert(sink.calls==0);moduleConfig.has_mesh_beacon=true;moduleConfig.mesh_beacon.flags=1;r.publishDuplicateToMqtt(&p);assert(sink.calls==1);p=original;
 reset();config.device.rebroadcast_mode=1;p.decoded.portnum=999;r.publishDuplicateToMqtt(&p);assert(sink.calls==0);p.decoded.portnum=meshtastic_PortNum_TRACEROUTE_APP;r.publishDuplicateToMqtt(&p);assert(sink.calls==1&&packetPool.live==0);
 std::cout<<"Duplicate MQTT helper regressions passed; packet ownership, decode rejection and policy gates checked.\n";
}
'''
with tempfile.TemporaryDirectory() as directory:
    path=pathlib.Path(directory)
    (path/'test.cpp').write_text(preamble+function+tests)
    subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror',str(path/'test.cpp'),'-o',str(path/'test')],check=True)
    subprocess.run([str(path/'test')],check=True)
print('Existing dispatch and opaque-PKI function text unchanged; ingress auth gate still precedes filters.')
