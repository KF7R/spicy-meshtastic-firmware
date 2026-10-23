"""Port the developer's E22P recipe; stop if upstream layout changes."""
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
src = root / 'variants/nrf52840/seeed_xiao_nrf52840_kit'
dst = root / 'variants/nrf52840/spicy_e22p_i2c'
dst.mkdir(exist_ok=False)
header = (src / 'variant.h').read_text()
old = '#define SX126X_RESET D2\n#define SX126X_RXEN D5'
assert header.count(old) == 1, 'Upstream radio pins changed: review required'
header = header.replace(old, '#define SX126X_RESET D2\n#define PIN_E22P_EN D5\n#define SX126X_MAX_POWER 22\n#define TX_GAIN_LORA 8')
cpp = (src / 'variant.cpp').read_text()
old = '    pinMode(PIN_LED3, OUTPUT);\n    ledOff(PIN_LED3);'
assert cpp.count(old) == 1, 'Upstream initialization changed: review required'
cpp = cpp.replace(old, old + '\n\n    pinMode(PIN_E22P_EN, OUTPUT);\n    digitalWrite(PIN_E22P_EN, HIGH);')
(dst / 'variant.h').write_text(header)
(dst / 'variant.cpp').write_text(cpp)
ini = (src / 'platformio.ini').read_text().split('; Seeed Xiao BLE but with GPS')[0]
ini = ini.replace('seeed_xiao_nrf52840_kit', 'spicy_e22p_i2c')
ini = ini.replace('-DSEEED_XIAO_NRF_KIT_DEFAULT', '-DSEEED_XIAO_NRF_KIT_I2C')
assert '[env:spicy_e22p_i2c]' in ini and '-DSEEED_XIAO_NRF_KIT_I2C' in ini
(dst / 'platformio.ini').write_text(ini)
print('Applied E22P: D5 HIGH, gain8, chip max22, I2C kit variant.')
