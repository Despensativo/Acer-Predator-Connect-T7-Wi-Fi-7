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
    "network_interfaces.txt": "ip addr; echo '=== ROUTE ==='; ip route",
    "loaded_modules.txt": "lsmod"
}

tn = telnetlib.Telnet('192.168.73.2', 23, timeout=3)
time.sleep(0.5)

for filename, cmd in commands.items():
    print(f"Running '{cmd}' -> {filename}")
    tn.write(f"echo '___BEGIN___'; {cmd}; echo '___END___'\n".encode('ascii'))
    time.sleep(1)
    buf = ""
    start_time = time.time()
    while time.time() - start_time < 3:
        chunk = tn.read_very_eager().decode('utf-8', errors='ignore')
        buf += chunk
        if "___END___" in buf:
            break
        time.sleep(0.2)
    
    if "___BEGIN___" in buf and "___END___" in buf:
        content = buf.split("___BEGIN___")[1].split("___END___")[0].strip()
        filepath = os.path.join(dest_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content + "\n")
        print(f"  Saved {filename} ({len(content)} chars)")
    else:
        print(f"  Warning: markers not found for {filename}")

tn.close()
print("Done collecting system data.")
