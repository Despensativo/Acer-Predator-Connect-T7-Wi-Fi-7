with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

# Let's search for "Bad CRC" or "Using default environment"
pos = 0
while True:
    idx = data.find(b"Bad CRC", pos)
    if idx == -1: break
    print(f'Found at {hex(idx)} (VA {hex(0x4a400000 + idx)})')
    pos = idx + 1

pos = 0
while True:
    idx = data.find(b"default environment", pos)
    if idx == -1: break
    print(f'Found "default environment" at {hex(idx)} (VA {hex(0x4a400000 + idx)})')
    pos = idx + 1
