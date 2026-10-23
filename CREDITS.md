# Credits and source provenance

- **Meshtastic contributors**: firmware, radio/power handling, nRF52840 support, and the original Seeed XIAO kit variant. Source: https://github.com/meshtastic/firmware . The checked-in variant and original UF2 derive from commit `8e6a88d06f44cad26f1e8d7cd402939ccacb9b4c` (v2.8.1.8e6a88d).
- **ascendr**: published Spicy E22P hardware recipe, https://github.com/ascendr/firmware/tree/spicy-e22p , commit `cb718ee5ff294739232a5efefd4b53c8f6720af8`. Credit for D5 module enable, gain compensation 8 dB, and chip maximum 22 dBm belongs to that source.
- **Seeed Studio**: XIAO nRF52840 hardware and kit pinout.
- **EBYTE**: E22P radio module hardware.
- **RadioLib contributors, Adafruit nRF52 Arduino contributors, PlatformIO, and other upstream dependencies**: radio driver, framework, and build tools. Their respective copyright notices and licenses remain applicable.
- **KF7R**: repository maintenance and distribution of this custom build. Porting, build scripts and documentation were prepared with OpenAI Codex assistance.

This is a community custom build; no endorsement by the projects or manufacturers above is implied. E22P and E22-900M33S 2W are distinct configurations.

## License and corresponding source

Meshtastic's GNU GPL version 3 license is included in LICENSE. Existing upstream notices are retained in the derived source files; dependency licenses are not replaced by this file. Repository-specific build scripts and documentation are provided under GPL-3.0-or-later.

For the original distributed binary, obtain official firmware commit `8e6a88d06f44cad26f1e8d7cd402939ccacb9b4c`, initialize its recursive submodules, and overlay this repository's `variants/nrf52840/spicy_e22p_i2c/` directory. Run `pio run -e spicy_e22p_i2c`. The source archive of that exact upstream revision is https://github.com/meshtastic/firmware/archive/8e6a88d06f44cad26f1e8d7cd402939ccacb9b4c.tar.gz ; use the Git checkout for recursive submodules and retain upstream dependency definitions.

Manual workflow builds record the exact upstream commit in verification.json and include the generated variant source with their artifacts. They may not reproduce the original UF2 byte-for-byte.
