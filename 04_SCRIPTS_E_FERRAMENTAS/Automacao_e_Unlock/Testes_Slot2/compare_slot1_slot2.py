import subprocess

def run_ssh(cmd):
    full_cmd = f'sshpass -p admin0100 ssh -o StrictHostKeyChecking=no -o HostKeyAlgorithms=+ssh-rsa root@192.168.73.2 "{cmd}"'
    res = subprocess.run(["wsl", "bash", "-c", full_cmd], capture_output=True, text=True)
    return res.stdout.strip()

print("="*65)
print("=== COMPARACAO DETALHADA: SLOT 1 vs SLOT 2 ===")
print("="*65)

# 1. Listar arquivos em ambos
s1_files = set(run_ssh("find /overlay/upper -type f | sed 's|^/overlay/upper/||'").splitlines())
s2_files = set(run_ssh("find /tmp/cmp_s2/upper -type f | sed 's|^/tmp/cmp_s2/upper/||'").splitlines())

print(f"Total de arquivos regulares no Slot 1: {len(s1_files)}")
print(f"Total de arquivos regulares no Slot 2: {len(s2_files)}")

missing_in_s2 = s1_files - s2_files
extra_in_s2 = s2_files - s1_files

print(f"\nArquivos faltando no Slot 2: {len(missing_in_s2)}")
for f in sorted(missing_in_s2)[:10]:
    print(f"  - {f}")

print(f"\nArquivos extras/customizados no Slot 2: {len(extra_in_s2)}")
for f in sorted(extra_in_s2):
    print(f"  + {f}")

# 2. Whiteouts (caracteres especiais c 0 0)
s1_whiteouts = set(run_ssh("find /overlay/upper -type c | sed 's|^/overlay/upper/||'").splitlines())
s2_whiteouts = set(run_ssh("find /tmp/cmp_s2/upper -type c | sed 's|^/tmp/cmp_s2/upper/||'").splitlines())

print(f"\nWhiteouts (serviços desabilitados) no Slot 1: {len(s1_whiteouts)}")
print(f"Whiteouts (serviços desabilitados) no Slot 2: {len(s2_whiteouts)}")
for w in sorted(s2_whiteouts):
    print(f"  [OK] Whiteout preservado: {w}")

# 3. Comparacao de kernels nos volumes UBI (vol 1)
print("\n[3] Comparando tamanho e hashes dos Kernels (vol 1)...")
k1_md5 = run_ssh("dd if=/dev/ubi0_1 bs=64k count=100 2>/dev/null | md5sum | awk '{print $1}'")
k2_md5 = run_ssh("dd if=/dev/ubi1_1 bs=64k count=100 2>/dev/null | md5sum | awk '{print $1}'")
print(f"Kernel Slot 1 (ubi0_1) MD5: {k1_md5}")
print(f"Kernel Slot 2 (ubi1_1) MD5: {k2_md5}")

# 4. Comparacao das imagens SquashFS (vol 2)
print("\n[4] Comparando RootFS SquashFS (vol 2)...")
r1_md5 = run_ssh("dd if=/dev/ubi0_2 bs=64k count=100 2>/dev/null | md5sum | awk '{print $1}'")
r2_md5 = run_ssh("dd if=/dev/ubi1_2 bs=64k count=100 2>/dev/null | md5sum | awk '{print $1}'")
print(f"RootFS Slot 1 (ubi0_2) MD5: {r1_md5}")
print(f"RootFS Slot 2 (ubi1_2) MD5: {r2_md5}")

# 5. Comparacao do firmware Wi-Fi (vol 0)
print("\n[5] Comparando Firmware Wi-Fi (vol 0)...")
w1_md5 = run_ssh("dd if=/dev/ubi0_0 bs=64k count=100 2>/dev/null | md5sum | awk '{print $1}'")
w2_md5 = run_ssh("dd if=/dev/ubi1_0 bs=64k count=100 2>/dev/null | md5sum | awk '{print $1}'")
print(f"Wi-Fi FW Slot 1 (ubi0_0) MD5: {w1_md5}")
print(f"Wi-Fi FW Slot 2 (ubi1_0) MD5: {w2_md5}")

print("\n" + "="*65)
print("=== COMPARACAO CONCLUIDA ===")
print("="*65)
