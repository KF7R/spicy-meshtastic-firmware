import hashlib
import json
import pathlib
import shutil
import struct
import subprocess
import sys
import zipfile

root = pathlib.Path(sys.argv[1])
build = root / '.pio/build/spicy_e22p_i2c'
files = list(build.glob('firmware-*.uf2'))
assert len(files) == 1, 'Expected exactly one application UF2'
uf2 = files[0]
data = uf2.read_bytes()
assert len(data) % 512 == 0
seen = set()
addresses = set()
payloads = []
for offset in range(0, len(data), 512):
    b = data[offset:offset+512]
    m0,m1,flags,addr,size,num,total,family = struct.unpack_from('<8I',b)
    assert (m0,m1) == (0x0A324655,0x9E5D5157)
    assert struct.unpack_from('<I',b,508)[0] == 0x0AB16F30
    assert flags & 0x2000 and not flags & 1
    assert family == 0xADA52840 and size == 256
    assert total == len(data)//512 and num not in seen and addr not in addresses
    assert 0x27000 <= addr and addr+size <= 0xEA000
    seen.add(num)
    addresses.add(addr)
    payloads.append((addr,b[32:32+size]))
assert seen == set(range(len(seen)))
raw = b''.join(p for _,p in sorted(payloads))
assert b'spicy_e22p_i2c\0' in raw
# Upstream's nRF build may name the DFU package .zip or -ota.zip.
candidates = [p for p in (uf2.with_suffix('.zip'), uf2.with_name(uf2.stem+'-ota.zip')) if p.exists()]
assert len(candidates) == 1, 'Expected one upstream-generated Nordic DFU package'
ota = candidates[0]
with zipfile.ZipFile(ota) as archive:
    assert archive.testzip() is None
    manifest = json.loads(archive.read('manifest.json'))['manifest']
    assert set(manifest) <= {'application', 'dfu_version'}
    app = manifest['application']
    firmware = archive.read(app['bin_file'])
    init_packet = archive.read(app['dat_file'])
    assert init_packet and firmware
    assert sorted(addresses) == list(range(min(addresses), max(addresses)+256, 256))
    assert firmware == raw[:len(firmware)] and len(raw)-len(firmware) < 256, 'DFU payload differs from UF2'
ota_name = uf2.stem+'-ota.zip'
out = pathlib.Path('output')
out.mkdir()
for ext in ('uf2','elf','hex'):
    file = uf2.with_suffix('.'+ext)
    assert file.exists()
    shutil.copy2(file,out/file.name)
shutil.copy2(ota,out/ota_name)
shutil.copytree(root/'variants/nrf52840/spicy_e22p_i2c',out/'spicy_e22p_i2c')
commit = subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
report = {'upstream_commit':commit,'uf2':uf2.name,'sha256':hashlib.sha256(data).hexdigest(),'family':'nRF52840','blocks':len(seen),'environment':'spicy_e22p_i2c','ota_zip':ota_name,'ota_sha256':hashlib.sha256(ota.read_bytes()).hexdigest(),'ota_payload_matches_uf2':True,'hardware_tested':False,'developer_recipe':'ascendr/firmware cb718ee5ff294739232a5efefd4b53c8f6720af8'}
(out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
(out/'READ-ME.txt').write_text('E22P hardware only; not E22-900M33S 2W. Build verification does not establish hardware operation. Back up configuration. Flash application UF2 without factory erase. Review upstream radio/power changes before use.\n')
print(json.dumps(report,indent=2))
