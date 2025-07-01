# bootviz

A simple Linux desktop GUI for managing EFI boot entries using efibootmgr.

## Features
- View existing EFI boot entries (Boot0000, Boot0001, etc.)
- Set default boot entry (BootOrder)
- Add new boot entries
- Edit or delete existing entries
- Designed for desktop Linux (PySide6 / Qt GUI)
- Planned support for detecting Secure Boot status and EFI partitions

## Built with
- Python 3.13
- PySide6 (Qt for Python)
- `subprocess` to interface with `efibootmgr`

## Getting Started
1. Clone this repository:
    ```bash
    git clone https://github.com/dawciobiel/bootviz.git
    cd bootviz
    ```
2. Install dependencies (example with pip):
    ```bash
    pip install -r requirements.txt
    ```
3. Run the application:
    ```bash
    python main.py
    ```

> ⚠ Note: Some features require `sudo` to call `efibootmgr`.

## License
This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0).  
See [LICENSE](LICENSE) and [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) for details.

---

## Roadmap / Ideas
- CLI-only mode
- Import / export boot entries configuration
- Better error handling and polkit integration
- Multi-language support

---

## Author
Created by Dawid Bielecki.
