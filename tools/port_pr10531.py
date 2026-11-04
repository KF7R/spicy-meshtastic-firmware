"""Conservative duplicate-uplink port of ianmcorvidae's PR10531 (40ac9fb).

Pinned to v2.8.2.d5f1619. Normal dispatch and opaque-PKI handling stay upstream.
"""
import pathlib
import subprocess
import sys

root = pathlib.Path(sys.argv[1])
base = 'd5f16191ca28b01b5024f590f04a67f25d66f1b1'
assert subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip() == base

def edit(path, old, new):
    p = root / path
    text = p.read_text()
    assert text.count(old) == 1, f'Upstream anchor changed: {path}'
    p.write_text(text.replace(old, new))

edit('src/configuration.h', '// Use polynomial approximations', '''// Experimental PR10531 adaptation: private MQTT analytics only.
#ifndef USERPREFS_MQTT_UPLINK_ALL_SEEN
#define USERPREFS_MQTT_UPLINK_ALL_SEEN 0
#endif

// Use polynomial approximations''')
edit('src/mesh/Router.h', '    friend class RoutingModule;', '''    friend class RoutingModule;
#if USERPREFS_MQTT_UPLINK_ALL_SEEN && !MESHTASTIC_EXCLUDE_MQTT
    void publishDuplicateToMqtt(const meshtastic_MeshPacket *p);
#endif''')

# Keep dispatchReceived() and perhapsUplinkOpaquePki() byte-for-byte upstream.
helper = r'''
#if USERPREFS_MQTT_UPLINK_ALL_SEEN && !MESHTASTIC_EXCLUDE_MQTT
// Adapted from ianmcorvidae PR10531. Called only from authenticated duplicate
// filters. Decode a pool-owned copy; never mutate/re-dispatch the routing packet.
// Unknown-channel/opaque PKI duplicates retain upstream dedup and are not added.
void Router::publishDuplicateToMqtt(const meshtastic_MeshPacket *p)
{
    if (!mqtt || !moduleConfig.mqtt.enabled || p->via_mqtt || p->id == 0)
        return;
    auto *decoded = packetPool.allocCopy(*p);
    if (!decoded)
        return;
    const auto state = perhapsDecode(decoded);
    bool eligible = state == DecodeState::DECODE_SUCCESS;
#if MESHTASTIC_PREHOP_DROP
    eligible = eligible && !shouldSkipHandleForPostDecodeHop(*decoded);
#endif
    if (eligible && decoded->decoded.portnum == meshtastic_PortNum_NEIGHBORINFO_APP &&
        (!moduleConfig.has_neighbor_info || !moduleConfig.neighbor_info.enabled))
        eligible = false;
#if !MESHTASTIC_EXCLUDE_BEACON
    if (eligible && decoded->decoded.portnum == meshtastic_PortNum_MESH_BEACON_APP &&
        (!moduleConfig.has_mesh_beacon ||
         !(moduleConfig.mesh_beacon.flags & meshtastic_ModuleConfig_MeshBeaconConfig_Flags_FLAG_LISTEN_ENABLED)))
        eligible = false;
#endif
    bool coreOnly = config.device.rebroadcast_mode == meshtastic_Config_DeviceConfig_RebroadcastMode_CORE_PORTNUMS_ONLY;
#if USERPREFS_EVENT_MODE
    coreOnly = true;
#endif
    if (eligible && coreOnly &&
        !IS_ONE_OF(decoded->decoded.portnum, meshtastic_PortNum_TEXT_MESSAGE_APP,
                   meshtastic_PortNum_TEXT_MESSAGE_COMPRESSED_APP, meshtastic_PortNum_POSITION_APP,
                   meshtastic_PortNum_NODEINFO_APP, meshtastic_PortNum_ROUTING_APP, meshtastic_PortNum_TELEMETRY_APP,
                   meshtastic_PortNum_ADMIN_APP, meshtastic_PortNum_ALERT_APP, meshtastic_PortNum_KEY_VERIFICATION_APP,
                   meshtastic_PortNum_WAYPOINT_APP, meshtastic_PortNum_STORE_FORWARD_APP,
                   meshtastic_PortNum_TRACEROUTE_APP, meshtastic_PortNum_STORE_FORWARD_PLUSPLUS_APP))
        eligible = false;
#if USERPREFS_BLOCK_POSITION_ON_EVENT_CHANNEL
    eligible = eligible && !isBlockedEventCoordinatePacket(decoded);
#endif
    if (eligible) {
        auto *wire = packetPool.allocCopy(*p);
        if (wire) {
            stampRxTime(decoded);
            wire->rx_time = decoded->rx_time;
            wire->has_rx_time = decoded->has_rx_time;
            // MQTT::onSend keeps its channel, precision and encryption controls.
            mqtt->onSend(*wire, *decoded, decoded->channel);
            packetPool.release(wire);
        }
    }
    packetPool.release(decoded);
}
#endif

'''
edit('src/mesh/Router.cpp', 'void Router::perhapsUplinkOpaquePki(', helper + 'void Router::perhapsUplinkOpaquePki(')

for filename, cls in [('FloodingRouter.cpp', 'FloodingRouter'), ('NextHopRouter.cpp', 'NextHopRouter')]:
    p = root / 'src/mesh' / filename
    text = p.read_text()
    start = text.index(f'bool {cls}::shouldFilterReceived(')
    end = text.index(f'    return Router::shouldFilterReceived(p);', start)
    body = text[start:end]
    # Exactly the hop-upgrade and duplicate early returns, leaving other functions intact.
    assert body.count('return true;') == 2
    body = body.replace('return true;', '''#if USERPREFS_MQTT_UPLINK_ALL_SEEN && !MESHTASTIC_EXCLUDE_MQTT
        publishDuplicateToMqtt(p);
#endif
        return true;''')
    p.write_text(text[:start] + body + text[end:])

variant = root / 'variants/nrf52840/spicy_e22p_i2c'
experiment = root / 'variants/nrf52840/spicy_e22p_i2c_pr10531'
experiment.mkdir()
for name in ('variant.h', 'variant.cpp', 'platformio.ini'):
    text = (variant / name).read_text()
    if name == 'platformio.ini':
        text = text.replace('spicy_e22p_i2c', 'spicy_e22p_i2c_pr10531')
        text = text.replace('-DSEEED_XIAO_NRF_KIT_I2C', '-DSEEED_XIAO_NRF_KIT_I2C\n  -DUSERPREFS_MQTT_UPLINK_ALL_SEEN=1')
    (experiment / name).write_text(text)
print('PR10531 adaptation applied; authenticated decoded duplicates only; opaque path unchanged.')
