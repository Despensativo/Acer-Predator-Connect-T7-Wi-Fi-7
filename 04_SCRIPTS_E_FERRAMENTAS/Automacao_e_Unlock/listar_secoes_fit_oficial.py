import struct

path = r'Backups_MTD\nand-4k-ipq5332-single_101000024.img'

with open(path, 'rb') as f:
    buf = f.read()

# Parse FDT header
magic, totalsize, off_dt_struct, off_dt_strings, off_mem_rsvmap, version, last_comp_version = struct.unpack('>IIIIIII', buf[:28])

print(f"FDT Version: {version}, Total Size: {totalsize}")
print(f"Struct offset: 0x{off_dt_struct:x}, Strings offset: 0x{off_dt_strings:x}")

# Let's extract strings
strings_blob = buf[off_dt_strings:]
def get_str(offset):
    end = strings_blob.find(b'\x00', offset)
    return strings_blob[offset:end].decode('ascii', errors='ignore')

# Simple FDT parser to walk nodes and properties under /images
pos = off_dt_struct
node_stack = []

OF_DT_BEGIN_NODE = 1
OF_DT_END_NODE = 2
OF_DT_PROP = 3
OF_DT_NOP = 4
OF_DT_END = 9

nodes = []
current_props = {}

while pos < off_dt_strings:
    tag = struct.unpack('>I', buf[pos:pos+4])[0]
    pos += 4
    if tag == OF_DT_BEGIN_NODE:
        end = buf.find(b'\x00', pos)
        name = buf[pos:end].decode('ascii', errors='ignore')
        pos = (end + 4) & ~3
        node_stack.append(name)
        if len(node_stack) == 3 and node_stack[1] == 'images':
            current_props = {'name': name}
    elif tag == OF_DT_END_NODE:
        if len(node_stack) == 3 and node_stack[1] == 'images':
            nodes.append(current_props)
            current_props = {}
        node_stack.pop()
    elif tag == OF_DT_PROP:
        val_len, name_off = struct.unpack('>II', buf[pos:pos+8])
        pos += 8
        prop_val = buf[pos:pos+val_len]
        pos = (pos + val_len + 3) & ~3
        prop_name = get_str(name_off)
        if len(node_stack) >= 2 and node_stack[1] == 'images':
            if prop_name in ['description', 'type', 'arch', 'compression', 'load', 'entry']:
                try:
                    current_props[prop_name] = prop_val.decode('ascii', errors='ignore').strip('\x00')
                except:
                    current_props[prop_name] = prop_val.hex()
            elif prop_name == 'data':
                current_props['data_size'] = val_len
    elif tag == OF_DT_NOP:
        pass
    elif tag == OF_DT_END:
        break

print(f"\nExtracted {len(nodes)} sections from official Acer FIT image:")
for n in nodes:
    print(f" Section: {n.get('name', 'unknown'):<20} | Type: {n.get('type', ''):<12} | Arch: {n.get('arch', ''):<6} | Size: {n.get('data_size', 0):>10} bytes ({n.get('data_size', 0)/1024/1024:.2f} MB) | Desc: {n.get('description', '')}")
