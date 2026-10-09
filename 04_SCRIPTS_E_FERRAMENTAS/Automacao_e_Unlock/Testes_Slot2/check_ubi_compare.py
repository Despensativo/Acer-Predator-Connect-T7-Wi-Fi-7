import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.73.2', 22, 'root', 'admin0100', timeout=5, look_for_keys=False, allow_agent=False)

def run(cmd):
    _, out, err = ssh.exec_command(cmd)
    o = out.read().decode('latin1', errors='ignore').strip()
    return o

print("=== VOLUMES EM UBI1 ===")
print(run("""
for v in /sys/class/ubi/ubi1_*; do
    if [ -d "$v" ]; then
        echo "$(basename $v): name=$(cat $v/name) data_bytes=$(cat $v/data_bytes 2>/dev/null || echo N/A)"
    fi
done
"""))

print("\n=== UBI0 VS UBI1 KERNEL & ROOTFS ===")
print("ubi0_1 (kernel slot 1):", run("cat /sys/class/ubi/ubi0_1/data_bytes 2>/dev/null"))
print("ubi1_1 (kernel slot 2):", run("cat /sys/class/ubi/ubi1_1/data_bytes 2>/dev/null"))
print("ubi0_2 (rootfs slot 1):", run("cat /sys/class/ubi/ubi0_2/data_bytes 2>/dev/null"))
print("ubi1_2 (rootfs slot 2):", run("cat /sys/class/ubi/ubi1_2/data_bytes 2>/dev/null"))

ssh.close()
