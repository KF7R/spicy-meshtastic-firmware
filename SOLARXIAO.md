# SolarXiao+ Advanced E22P — Meshtastic 2.8.1

This branch contains the build workflow for the SolarXiao+ Advanced board with an E22P-915M30S radio. The repository's root README and existing Spicy binaries describe a different board configuration.

The workflow checks out official Meshtastic commit `8e6a88d06f44cad26f1e8d7cd402939ccacb9b4c` (v2.8.1.8e6a88d), creates an isolated board variant, and builds `solarxiao_advanced_1w`.

## Download

Open [the SolarXiao build](https://github.com/KF7R/spicy-meshtastic-firmware/actions/runs/37192846348). After a successful run, download the artifact **SolarXiao-Advanced-E22P-GPS-I2C-2.8.1**. It includes the UF2, linked ELF/HEX, board sources, build log, and UF2 validation record.

## Wiring

Based on the designer's Advanced Plus schematic dated 2026-10-03:

| Function | XIAO assignment |
| --- | --- |
| Radio CS / IRQ | D4 / D1 |
| Radio RESET / BUSY | D2 / D3 |
| Radio SPI SCK / MISO / MOSI | D8 / D9 / D10 |
| GPS module RX / TX | D6 / D7 |
| I2C SDA / SCL | logical 30 / 31, NFC1 / NFC2 |
| D0 | unassigned |

Radio EN is tied to 3.3 V on the carrier; D5 is not used. DIO2 controls T/RCTRL; DIO3 supplies the 1.8 V TCXO reference. NFC GPIO configuration is enabled. UART GPS starts at 9600 baud with no L76K-specific default or D0 standby control.

U17 GPS connector schematic numbering: 1 D0 (unused), 2 GPS RX (MCU D6), 3 GPS TX (MCU D7), 4 GND, 5 3.3 V. Verify the chosen GPS breakout's supply requirements before using pin 5; connector numbering is not a physical viewing-order diagram.

U14 I2C connector numbering: 1 GND, 2 3.3 V, 3 SDA, 4 SCL.

## Power and limitations

The designer recommends 18 dBm chip drive for approximately 30 dBm RF output. This build caps chip drive at 18 dBm and applies an estimated 12 dB PA gain correction in normal mode. **Set requested transmit power to 30 dBm for the full-power operating point in normal mode**; requested 18 maps to chip drive 6. Licensed mode bypasses gain correction but retains the 18 dBm cap.

Lower power settings are not calibrated. The solar charger's status outputs are not connected to the MCU; the inherited XIAO charge detector cannot reliably indicate solar charging. Battery ADC settings remain inherited from the XIAO kit.

A successful build and UF2 checks establish compilation and file structure, not on-device performance. No device has been flashed or tested.

## Flash

Extract the artifact ZIP. Double-tap the XIAO reset button to enter its UF2 bootloader and copy only the SolarXiao `.uf2` to the bootloader drive. Reconnect after it restarts, select the appropriate region, enable GPS, and inspect GPS/I2C detection.

## References

- [Designer hardware](https://github.com/wehooper4/Meshtastic-Hardware/tree/main/XaioSeries/SolarXaio)
- [Advanced Plus schematic](https://github.com/wehooper4/Meshtastic-Hardware/blob/main/XaioSeries/SolarXaio/Advanced/Plus/Schematic_SolarXaio_ADV%2B_2026-10-03.pdf)
- [XIAO I2C/GPS upstream PR](https://github.com/meshtastic/firmware/pull/8866)
