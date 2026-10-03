import telnetlib
import time
import os

dest_dir = r"H:\FEITOS COM IA\Acer-Predator-Connect-T7\Engenharia_Reversa_OpenWrt"
os.makedirs(dest_dir, exist_ok=True)

commands = {
    "board.json": "cat /etc/board.json",
    "gpio_table.txt": "cat /sys/kernel/debug/gpio",
    "switch_config.txt": "swconfig dev switch1 show",
    "ledd_config.txt": "cat /etc/config/ledd_config",
    "buttons_config.txt": "cat /etc/config/buttons",
    "network_interfaces.txt": "ip addr; ip route",
    "loaded_modules.txt": "lsmod"
}

tn = telnetlib.Telnet('192.168.73.2', 23, timeout=5)
time.sleep(0.5)
# consume initial prompt
tn.read_very_eager()

for filename, cmd in commands.items():
    print(f"Executing: {cmd}...")
    tn.write((cmd + "\n").encode('ascii'))
    time.sleep(0.5)
    raw = tn.read_until(b"/ # ", timeout=5).decode('utf-8', errors='ignore')
    
    # Strip command echo and prompt
    lines = raw.splitlines()
    if len(lines) > 2:
        content = "\n".join(lines[1:-1]).strip()
    else:
        content = raw.strip()
        
    filepath = os.path.join(dest_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content + "\n")
    print(f"  -> Saved {filename} ({len(content)} chars)")

tn.close()
print("All tables successfully dumped!")
