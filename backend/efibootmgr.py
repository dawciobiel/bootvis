# cmd = ['pkexec', '/usr/sbin/efibootmgr']
import subprocess

def get_boot_entries():
    """
    Uruchamia pkexec efibootmgr, parsuje output i zwraca:
    {
      'entries': [ {'id': '0000', 'active': True, 'description': 'opis'}, ... ],
      'current_boot': '0000'  # BootCurrent
    }
    """
    cmd = ['pkexec', '/usr/sbin/efibootmgr']
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"efibootmgr error: {result.stderr.strip()}")

    entries = []
    current_boot = None

    for line in result.stdout.splitlines():
        line = line.strip()
        # Szukamy BootCurrent:
        if line.startswith("BootCurrent:"):
            # BootCurrent: 0000
            current_boot = line.split()[1].lower()
            continue
        # Linia z boot entries np:
        # Boot0000* opensuse-secureboot
        # Boot0001  Windows Boot Manager
        if line.startswith("Boot"):
            # rozbij na ID i opis
            # ID to np "Boot0000*" lub "Boot0001 "
            parts = line.split(maxsplit=1)
            if len(parts) < 2:
                continue
            raw_id = parts[0]  # np. "Boot0000*" lub "Boot0001"
            desc = parts[1]

            # Sprawdź czy aktywny (czyli ma '*')
            active = raw_id.endswith('*')
            # Usuń 'Boot' prefix i gwiazdkę
            boot_id = raw_id.replace('Boot', '').replace('*', '').lower()

            entries.append({
                'id': boot_id,
                'active': active,
                'description': desc
            })

    if current_boot is None:
        raise RuntimeError("Cannot find BootCurrent entry in efibootmgr output")

    return {
        'entries': entries,
        'current_boot': current_boot
    }


def set_boot_order(order):
    """
    Ustawia kolejność bootowania, order to lista stringów z id, np ['0000', '0001', '0003']
    Wywołuje: pkexec efibootmgr -o 0000,0001,0003
    """
    order_str = ",".join(order)
    cmd = ['pkexec', 'efibootmgr', '-o', order_str]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to set boot order: {result.stderr.strip()}")
