# SeedSigner Architecture Flow

## Boot And Runtime Flow

```mermaid
flowchart TD
    A["Power on / python src/main.py"] --> B["src/main.py"]
    B --> C["seedsigner.controller"]
    C --> D["Initialize shared app state"]
    D --> E["Hardware layer"]
    D --> F["GUI renderer"]
    D --> G["Settings / storage"]
    C --> H["Root view / menu"]
    H --> I["views/*.py"]
    I --> J["gui/screens/*.py"]
    J --> F
    F --> K["hardware/displays/*"]
    I --> L["models/*.py"]
    L --> M["helpers/*.py"]
    I --> E
    E --> N["buttons, camera, microSD, battery, RNG"]
```

## Mental Model

SeedSigner is arranged like a small hardware application with a clear split:

| Layer       | Files                                                     | Job                                                                                                            |
| ----------- | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Entry point | `src/main.py`                                             | Starts the app and hands control to the controller.                                                            |
| Controller  | `src/seedsigner/controller.py`                            | Central navigation and runtime coordinator.                                                                    |
| Views       | `src/seedsigner/views/*.py`                               | High-level user flows: scan, seed, PSBT, settings, tools, smartcard, warnings.                                 |
| Screens     | `src/seedsigner/gui/screens/*.py`                         | Concrete UI screens and drawing logic for each flow.                                                           |
| GUI core    | `components.py`, `renderer.py`, `keyboard.py`, `toast.py` | Shared UI widgets, display rendering, text entry, status/toast messages.                                       |
| Hardware    | `hardware/*.py`, `hardware/displays/*.py`                 | Buttons, camera, display drivers, microSD, battery, IO config, RNG monitoring.                                 |
| Models      | `models/*.py`                                             | Bitcoin/domain state: seed, settings, QR decoding/encoding, PSBT parsing, encryption, WIF, BIP38.              |
| Helpers     | `helpers/*.py`, `helpers/ur2/*.py`                        | Lower-level utilities: QR formats, mnemonic generation, BIP85, Base43, smartcard helpers, UR2 encoding.        |
| Resources   | `resources/*`                                             | Fonts, icons, images, translations, diceware wordlists.                                                        |
| Tests       | `tests/test_*.py`                                         | Unit and flow tests covering controller, models, views, settings, PSBT, seed QR, smartcard, hardware profiles. |

## Main Interaction Loop

The controller is the traffic cop. It owns the app loop, sends the user into a View, waits for that View to finish, then receives a destination for the next View.

```mermaid
flowchart TD
    A["Controller loop"] --> B["Current View.run()"]
    B --> C["View shows one or more Screens"]
    C --> D["Screen reads buttons / camera / input"]
    D --> E["View updates model state"]
    E --> F["View returns Destination"]
    F --> A
```

## QR Scan Flow

```mermaid
flowchart TD
    A["Scan selected"] --> B["scan_views.py"]
    B --> C["scan_screens.py"]
    C --> D["hardware/camera.py"]
    D --> E["models/decode_qr.py"]
    E --> F["models/qr_type.py"]
    F --> G["Seed flow"]
    F --> H["PSBT flow"]
    F --> I["Settings flow"]
    F --> J["Address / message / tool flow"]
```

## PSBT Signing Flow

```mermaid
flowchart TD
    A["Scan PSBT QR"] --> B["decode_qr.py"]
    B --> C["psbt_parser.py"]
    C --> D["psbt_views.py"]
    D --> E["Review transaction details"]
    E --> F["Select signer"]
    F --> G["seed.py / smartcard signer"]
    G --> H["encode_qr.py"]
    H --> I["Display signed PSBT QR"]
```

## Seed Flow

```mermaid
flowchart TD
    A["Seed tools"] --> B["seed_views.py"]
    B --> C["seed_screens.py"]
    C --> D["mnemonic_generation.py"]
    D --> E["models/seed.py"]
    E --> F["seed_storage.py"]
    F --> G["xpub / address / SeedQR export"]
```

## Hardware Flow

```mermaid
flowchart TD
    A["io_config.json / io_config.py"] --> B["Select hardware profile"]
    B --> C["buttons.py"]
    B --> D["camera.py"]
    B --> E["displays/display_driver.py"]
    E --> F["ST7789 / ST7735 / ILI9341 / desktop_display"]
    B --> G["microsd.py / battery_hat.py / rng_monitor.py"]
```

## Where To Look First When Refactoring

| Goal                        | Start here                            | Then inspect                                                                          |
| --------------------------- | ------------------------------------- | ------------------------------------------------------------------------------------- |
| App startup / boot behavior | `src/main.py`                         | `controller.py`, `models/settings.py`, `hardware/io_config.py`                        |
| Navigation bugs             | `controller.py`                       | `views/view.py`, `tests/test_controller.py`, `tests/test_flows*.py`                   |
| Screen rendering/layout     | `gui/screens/screen.py`               | `gui/components.py`, `gui/renderer.py`, flow-specific screen file                     |
| Camera/QR scanning          | `views/scan_views.py`                 | `gui/screens/scan_screens.py`, `hardware/camera.py`, `models/decode_qr.py`            |
| PSBT parsing/signing        | `views/psbt_views.py`                 | `models/psbt_parser.py`, `models/seed.py`, smartcard helpers                          |
| Seed generation/storage     | `views/seed_views.py`                 | `models/seed.py`, `models/seed_storage.py`, `helpers/mnemonic_generation.py`          |
| Display driver work         | `hardware/displays/display_driver.py` | `ST7789.py`, `st7789_mpy.py`, `ST7735.py`, `ili9341.py`, `desktop_display.py`         |
| Smartcard/Satochip work     | `views/smartcard_views.py`            | `helpers/satochip_signer.py`, `helpers/seedkeeper_utils.py`, `helpers/keycard_*`      |
| Settings behavior           | `models/settings.py`                  | `models/settings_definition.py`, `views/settings_views.py`, `tests/test_settings*.py` |

## Practical Architecture Notes

- `views/` should stay focused on user intent and navigation.
- `gui/screens/` should stay focused on pixels, layout, and button prompts.
- `models/` should own domain logic that can be tested without hardware.
- `helpers/` should hold reusable protocol/crypto/encoding helpers.
- `hardware/` should isolate real device IO from the rest of the app.
- `tests/test_flows*.py` are the best warning system when cleaning up navigation.
- `tests/test_*qr*.py`, `test_psbt*.py`, and `test_seed*.py` matter most before touching signing or seed logic.
