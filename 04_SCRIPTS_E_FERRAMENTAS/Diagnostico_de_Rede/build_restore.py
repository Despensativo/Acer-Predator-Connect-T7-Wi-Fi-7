import subprocess

# Create 32 KB padding
with open('/tmp/pad.bin', 'wb') as f:
    f.write(b'\x00' * 32768)

with open('/tmp/restore_cmd.txt', 'w') as f:
    f.write('echo Restoring Stock Acer Firmware...\nsetenv bootcmd bootipq\nsaveenv\nbootipq\n')

its_content = """/dts-v1/;

/ {
\tdescription = "Flash Restore Stock";
\t#address-cells = <1>;

\timages {
\t\tscript {
\t\t\tdescription = "Restore Stock Bootcmd";
\t\t\tdata = /incbin/("/tmp/restore_cmd.txt");
\t\t\ttype = "script";
\t\t\tcompression = "none";
\t\t\thash@1 {
\t\t\t\talgo = "crc32";
\t\t\t};
\t\t};
\t\tpadding {
\t\t\tdescription = "Padding for minimum 10KB size";
\t\t\tdata = /incbin/("/tmp/pad.bin");
\t\t\ttype = "ramdisk";
\t\t\tcompression = "none";
\t\t};
\t};

\tconfigurations {
\t\tdefault = "config@1";
\t\tconfig@1 {
\t\t\tdescription = "Restore Stock Config";
\t\t};
\t};
};
"""

with open('/tmp/restore.its', 'w') as f:
    f.write(its_content)

res = subprocess.run(['/home/builder/openwrt/staging_dir/host/bin/mkimage', '-f', '/tmp/restore.its', '/tmp/restaurar_acer.itb'], capture_output=True, text=True)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
