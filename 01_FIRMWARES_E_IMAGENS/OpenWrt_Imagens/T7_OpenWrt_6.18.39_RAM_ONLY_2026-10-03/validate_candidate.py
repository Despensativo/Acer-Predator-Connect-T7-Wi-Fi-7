#!/usr/bin/env python3
"""Read-only structural checks for the T7 RAM prototype FIT."""

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zlib


if len(sys.argv) != 2:
    raise SystemExit('usage: validate_candidate.py /absolute/path/to/initramfs.itb')

image = Path(sys.argv[1]).resolve(strict=True)
if not image.is_file():
    raise SystemExit('image is not a regular file')

def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout.strip()

listing = run('dumpimage', '-l', str(image))
records = {}
current = None
algorithm = None
for line in listing.splitlines():
    match = re.match(r'^ Image (\d+) \(', line)
    if match:
        current = int(match.group(1))
        records[current] = {'hashes': []}
        continue
    if current is None:
        continue
    match = re.match(r'^  Data Size:\s+(\d+) Bytes', line)
    if match:
        records[current]['size'] = int(match.group(1))
    match = re.match(r'^  Hash algo:\s+(\w+)', line)
    if match:
        algorithm = match.group(1)
    match = re.match(r'^  Hash value:\s+([0-9a-f]+)', line)
    if match:
        records[current]['hashes'].append((algorithm, match.group(1)))
    if line.startswith(' Default Configuration:') or line.startswith(' Configuration '):
        current = None

with tempfile.TemporaryDirectory(prefix='t7-fit-check-', dir='/home/builder') as tmp:
    dtb = Path(tmp) / 't7.dtb'
    kernel = Path(tmp) / 'kernel.bin'
    run('dumpimage', '-T', 'flat_dt', '-p', '0', '-o', str(kernel), str(image))
    run('dumpimage', '-T', 'flat_dt', '-p', '1', '-o', str(dtb), str(image))
    compatible = run('fdtget', '-t', 's', str(dtb), '/', 'compatible')
    memory = run('fdtget', '-t', 'x', str(dtb), '/memory@40000000', 'reg')
    reserves = run('fdtget', '-l', str(dtb), '/reserved-memory').splitlines()
    expected = {
        'bootloader@4a100000', 'sbl@4a500000', 'tz@4a600000',
        'smem@4a800000', 'wcss@4a900000',
        'tzapp@49b00000', 'mlo-global-mem@4db00000',
        'qcn9224-pcie1@51e00000',
    }
    missing = sorted(expected.difference(reserves))
    hash_failures = []
    for index, data in ((0, kernel.read_bytes()), (1, dtb.read_bytes())):
        info = records.get(index, {})
        if len(data) != info.get('size'):
            hash_failures.append(f'{index}: size')
        for algo, expected_hash in info.get('hashes', []):
            actual = (f'{zlib.crc32(data):08x}' if algo == 'crc32'
                      else hashlib.new(algo, data).hexdigest())
            if actual != expected_hash:
                hash_failures.append(f'{index}: {algo}')

result = {
    'image': str(image),
    'bytes': image.stat().st_size,
    'sha256': hashlib.sha256(image.read_bytes()).hexdigest(),
    'fit_aarch64': 'Architecture: AArch64' in listing,
    'fit_initramfs_config': "Default Configuration: 'config@mi01.6'" in listing,
    'fit_uses_lzma': 'Compression:  lzma compressed' in listing,
    'compatible': compatible,
    'memory_reg_hex': memory,
    'reserved_nodes_count': len(reserves),
    'missing_key_reservations': missing,
    'fit_components': len(records),
    'checked_component_hashes': sum(len(v['hashes']) for v in records.values()),
    'fit_hash_failures': hash_failures,
}
result['structural_pass'] = all((
    result['fit_aarch64'], result['fit_initramfs_config'],
    result['fit_uses_lzma'], 'acer,predator-t7' in compatible,
    memory == '0 40000000 0 40000000', not missing,
    len(records) == 2, not hash_failures,
))
print(json.dumps(result, indent=2, ensure_ascii=False))
if not result['structural_pass']:
    raise SystemExit(1)
