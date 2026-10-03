with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import capstone
md_thumb = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

# We want to check all functions reachable from do_bootm (0x4a409780)
# and see if any SMC function (0x4a401a14, 0x4a401ad8, 0x4a400398) or
# do_boot_signedimg functions are called.

visited = set()
to_visit = [0x4a409780]
auth_funcs = {0x4a401a14, 0x4a401ad8, 0x4a400398, 0x4a401d66, 0x4a402920, 0x4a402d00}

found_auth_calls = []

while to_visit:
    func_va = to_visit.pop(0)
    if func_va in visited:
        continue
    visited.add(func_va)
    
    file_off = func_va - 0x4a400000
    if not (0 <= file_off < len(data) - 4):
        continue
    
    # scan instructions up to pop {..., pc} or bx lr or 200 insns
    count = 0
    for insn in md_thumb.disasm(data[file_off:file_off+0x400], func_va):
        count += 1
        if count > 200:
            break
        if insn.mnemonic in ['bl', 'b']:
            try:
                target = int(insn.op_str.strip('#'), 16)
                if target in auth_funcs:
                    found_auth_calls.append((hex(insn.address), hex(func_va), insn.mnemonic, hex(target)))
                elif 0x4a400000 <= target < 0x4a400000 + len(data):
                    if target not in visited and target not in to_visit:
                        to_visit.append(target)
            except:
                pass
        if insn.mnemonic in ['pop', 'bx', 'b'] and ('pc' in insn.op_str or 'lr' in insn.op_str):
            if insn.mnemonic != 'bl':
                break

print(f"Total reachable functions from do_bootm: {len(visited)}")
print(f"Auth calls found: {found_auth_calls}")
