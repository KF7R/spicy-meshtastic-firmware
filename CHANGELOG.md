# Changes

## 2026-11-04

- Added standard E22P/I2C alpha v2.8.2.d5f1619, upstream d5f16191ca28b01b5024f590f04a67f25d66f1b1; retained all 2.8.1 downloads.
- Standard build [41800952073](https://github.com/KF7R/spicy-meshtastic-firmware/actions/runs/41800952073) passed compilation and UF2/OTA checks.
- Added a separately named experimental environment spicy_e22p_i2c_pr10531 with USERPREFS_MQTT_UPLINK_ALL_SEEN=1, adapted from ianmcorvidae PR10531 head40ac9fb. Added a pinned manual workflow, port script, focused C++ regression tests and detailed scope/credits.
- Unlike the older PR, normal dispatch and opaque-PKI uplinking remain unchanged. Only authenticated decoded duplicates and hop-upgrade copies are additionally submitted to existing MQTT policy checks. Non-success decode states, ignored/pre-hop/policy-rejected input and MQTT-loop input are not added.
- Experimental build [41802323525](https://github.com/KF7R/spicy-meshtastic-firmware/actions/runs/41802323525) passed host helper regressions, full nRF52840 compilation and UF2/OTA payload validation. ELF inspection confirms the duplicate helper is compiled in.
- E22P hardware settings retained (D5 HIGH, gain8, chip max22, I2C6/7). Binary/source packages, checksums and corresponding adapted source published separately.
- No hardware flashed. Live duplicate MQTT analytics, radio/sensor behavior, and recovery from the previous BLE verification timeout remain untested. This experimental build is for bench testing before mast deployment.

## 2026-10-24

- Hosted baseline build [run #1](https://github.com/KF7R/spicy-meshtastic-firmware/actions/runs/40077960007) succeeded through compilation, collector checks and both firmware/OTA artifact uploads.

- Added application-only Nordic DFU OTA ZIP for the existing verified E22P 2.8.1.8e6a88d firmware; no firmware or hardware-definition changes.
- Generated with PlatformIO bundled Adafruit nRF utility, upstream device type0x0052 and SoftDevice0x0123, DFU0.5 format.
- Verified ZIP integrity, manifest and application-only contents; BIN payload exactly matches original UF2.
- Updated workflow collector to include upstream-generated DFU ZIP, check payload agreement and record checksum; added separate OTA artifact.
- Documented Android selection, artifact-wrapper extraction and untested app/bootloader compatibility. Credits in CREDITS.md remain applicable.

## 2026-10-23

- Added a manual GitHub Actions workflow, **Build E22P I2C firmware**, with an explicit official Meshtastic tag or commit input. Default remains the previously tested v2.8.1.8e6a88d; it does not silently select the newest alpha.
- Added scripts to copy the selected upstream Seeed kit variant into an isolated E22P environment, apply the published recipe, and collect UF2/ELF/HEX, variant source, SHA256 and upstream commit provenance.
- Preparation stops when expected upstream radio pin or initialization anchors change. This is a drift check, not a guarantee of compatibility with every future release.
- Artifacts are retained for 90 days; no firmware release is published and no device is flashed automatically. The workflow token has read-only repository permissions.
- Published the portable variant source, upstream license, credits and build instructions.
- Local checks: Python syntax passed; generated variant header matched the previously built E22P header. Initial local validation was followed by a successful end-to-end hosted build on October 24, 2026 (run40077960007).

## Original custom build

- Upstream base: Meshtastic v2.8.1.8e6a88d.
- Developer recipe: ascendr/firmware cb718ee5.
- Replaced MCU RXEN D5 with E22P module enable D5, initialized OUTPUT/HIGH.
- Applied TX_GAIN_LORA=8 and SX126X_MAX_POWER=22.
- Selected I2C kit configuration (SDA D6, SCL D7; GPS moved to NFC pins).
- Kept modifications in a separate variant; no upstream radio implementation changes.
- Original UF2 and verification remain unchanged. No hardware runtime validation was performed.
