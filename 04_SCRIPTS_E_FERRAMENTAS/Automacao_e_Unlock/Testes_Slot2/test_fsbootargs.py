import telnetlib, time

tn = telnetlib.Telnet('192.168.73.2', 23, timeout=5)
tn.read_until(b'login: ', 3)
tn.write(b'root\n')
tn.read_until(b'Password: ', 3)
tn.write(b'admin0100\n')
time.sleep(0.5)
tn.read_very_eager()

cmd = 'fw_setenv fsbootargs "ubi.mtd=rootfs_1 root=mtd:ubi_rootfs rootfstype=squashfs"\n'
tn.write(cmd.encode('ascii'))
time.sleep(0.5)

tn.write(b'fw_printenv fsbootargs\n')
time.sleep(0.5)
out = tn.read_very_eager().decode()
print("OUTPUT:")
print(out)
tn.close()
