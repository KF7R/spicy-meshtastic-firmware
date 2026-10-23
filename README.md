# XXtra Spicy E22P / I2C alpha build

This build ports the published E22P changes from [ascendr/firmware cb718ee5](https://github.com/ascendr/firmware/commit/cb718ee5ff294739232a5efefd4b53c8f6720af8) to [official Meshtastic v2.8.1.8e6a88d](https://github.com/meshtastic/firmware/releases/tag/v2.8.1.8e6a88d). GitHub's releases API identified this as the latest published alpha during this task on October 1, 2026 (America/Phoenix).

It uses a new isolated variant, `spicy_e22p_i2c`. No tracked upstream source files were modified. This is a port of the published E22P recipe, not an exact reconstruction of the separately distributed `spicy_2w_i2c-2.8.1.d4482a2` binary.

## Hardware configuration

| Setting | Value |
|---|---|
| PlatformIO environment | `spicy_e22p_i2c` |
| Board | `xiao_ble_sense`, nRF52840 |
| Meshtastic hardware model | 88, XIAO_NRF52_KIT |
| Radio | SX1262 |
| CS / DIO1 / BUSY / RESET | D4 / D1 / D3 / D2 |
| SPI SCK / MISO / MOSI | D8 / D9 / D10 |
| E22P module enable | D5, OUTPUT and HIGH in `initVariant()` |
| MCU RXEN | undefined in variant, defaults to RadioLib NC |
| MCU TXEN | RadioLib NC |
| TX RF switching | radio DIO2, unchanged from published E22P recipe |
| TCXO | radio DIO3, 1.8 V |
| SX1262 chip power maximum | 22 dBm |
| PA gain compensation | `TX_GAIN_LORA = 8` dB, as published by the author |
| I2C SDA / SCL | D6 / D7 (P1.11 / P1.12) |
| Button | D0 |
| GPS TX / RX | 30 / 31 (NFC pins P0.09 / P0.10); GPS remains enabled |

The PA gain is the author's configured value, not a measurement of this user's module. Upstream power handling, including region limits and its licensed-mode behavior, is unchanged. The build does not force a new radio-power setting or erase configuration.

## Reproduction

1. Check out official firmware commit `8e6a88d06f44cad26f1e8d7cd402939ccacb9b4c`.
2. Copy the supplied `spicy_e22p_i2c` directory to `variants/nrf52840/`.
3. Run `pio run -e spicy_e22p_i2c`.

The custom variant is a copy of the upstream kit variant, with the author's three E22P defines and D5 initialization applied, and the I2C environment selected. The configuration uses the upstream Nordic platform 11.0.0 and ARM GCC package `1.90301.200702`.

For the local Windows build, the framework was retrieved in shallow checkouts to avoid a slow full-history download. A local PlatformIO package override pointed to that checkout. Its commit is the exact upstream-pinned `0fd295f13203e93df19d578073646ec32f2bf45a`; its TinyUSB and nRFCrypto dependencies were checked out at `d6294767525fa16eaa4e29e118dcb6a7420a4da7` and `2be11062ac56cf75a9a8b8ed087ad495421403f4`. The supplied portable configuration uses upstream's normal package definition instead of the machine-specific override.

## Verification records

The build completed successfully. Flash usage is 692,652 / 815,104 bytes (85.0%); static RAM usage is 96,540 / 248,832 bytes (38.8%). Upstream's warm-region, interrupt-handler, and variant-linkage guards passed. The UF2 contains 2,706 blocks, starts at `0x27000`, and ends at `0xD0200` including block padding. Its embedded version and environment are `2.8.1.8e6a88d` and `spicy_e22p_i2c`. Linked disassembly at `0x9D1B2` through `0x9D1C6` confirms calls equivalent to `pinMode(5, 1)` and `digitalWrite(5, 1)`.

UF2 SHA256: `2660f2a7e093ff6dc94269fa1759b96a0ff59e40f26eefcb5e3069be3007ad6f`.

The build log, effective preprocessor definitions, UF2 validation result, and linked `initVariant()` disassembly accompany the delivered build. UF2 checks cover block magic, family, payload size, block counts, duplicate addresses, application address bounds, and embedded target/version strings. Build success and those checks do not establish on-device radio or sensor performance. No hardware was flashed or tested.

## Flashing

Use this firmware on the XXtra Spicy nRF52840 E22P hardware with the wiring above. Save a configuration backup first if desired. Double-tap reset to enter its UF2 bootloader, then copy the supplied `.uf2` to the bootloader drive. Wait for the copy to finish and the device to restart. Reconnect and check that version `2.8.1.8e6a88d` is reported. Do not use an erase or factory-reset image for this update. An ordinary UF2 application update is intended to retain configuration, although preservation has not been tested on the user's hardware.

## Build another version with GitHub Actions

1. Open [Actions → Build E22P I2C firmware](https://github.com/KF7R/spicy-meshtastic-firmware/actions/workflows/build-e22p.yml).
2. Choose **Run workflow** and enter an official `meshtastic/firmware` release tag or full commit SHA. The default is the previously built `v2.8.1.8e6a88d`; choose a newer tag explicitly.
3. After a successful run, download the `spicy-e22p-i2c-<run number>` artifact. It includes the UF2, ELF/HEX, generated variant source and verification report. Artifacts expire after 90 days.
4. Review upstream radio/power changes and test the device before relying on a new version. Automatic UF2 checks establish file structure and target, not RF performance.

The workflow is manual only. It does not flash hardware, publish releases, or overwrite the original firmware. A changed upstream layout stops preparation for review. Hosted workflow execution has not yet been verified end to end.

See [CHANGELOG.md](CHANGELOG.md) for changes and [CREDITS.md](CREDITS.md) for developer attribution, licensing and corresponding-source instructions. Portable source is in [variants/nrf52840/spicy_e22p_i2c](variants/nrf52840/spicy_e22p_i2c).
