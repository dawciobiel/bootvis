import re
import subprocess

HEX_ID_PATTERN = re.compile(r"^[0-9A-Fa-f]{4}$")
CMD_EFIBOOTMGR = '/usr/sbin/efibootmgr'


def get_boot_entries():
    """
    Retrieve boot entries using efibootmgr.
    """
    cmd = ['pkexec', CMD_EFIBOOTMGR]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"efibootmgr error: {result.stderr.strip()}")

    entries = []
    default_boot = None

    for line in result.stdout.splitlines():
        if line.startswith("BootCurrent:"):
            default_boot = line.split()[1]
        elif line.startswith("BootOrder:"):
            boot_order = line.split()[1].split(',')  # TODO: use boot_order in GUI to show current order
        elif line.startswith("Boot"):
            parts = line.split(maxsplit=1)
            if len(parts) > 1:
                bootnum = parts[0].replace("Boot", "").replace("*", "")
                desc = parts[1].strip()
                active = '*' in parts[0]
                entries.append({'id': bootnum.upper(), 'description': desc, 'active': active})

    # Mark default boot entry
    for entry in entries:
        entry['default'] = (entry['id'].upper() == default_boot.upper()) if default_boot else False

    return entries


def set_boot_order(order):
    """
    Set new boot order using efibootmgr.
    """
    # Validate IDs (must be 4-digit hex)
    for boot_id in order:
        if not HEX_ID_PATTERN.match(boot_id):
            raise ValueError(f"Invalid boot ID format: {boot_id} (must be 4 hex digits)")

    order_str = ",".join(order)
    cmd = ['pkexec', CMD_EFIBOOTMGR, '-o', order_str]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to set boot order:\n{result.stderr.strip()}")
