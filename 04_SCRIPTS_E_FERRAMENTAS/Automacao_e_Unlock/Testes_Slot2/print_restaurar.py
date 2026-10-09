import pyfdt.pyfdt as pyfdt
with open(r"H:\FEITOS COM IA\Acer-Predator-Connect-T7\3 - Ferramentas de Recuperacao\restaurar_acer.itb", "rb") as f:
    fdt = pyfdt.FdtBlobParse(f).to_fdt()

def print_node(node, indent=0):
    prefix = "  " * indent
    print(f"{prefix}{node.name}/")
    for prop in node:
        if isinstance(prop, pyfdt.FdtProperty):
            if prop.name == "data":
                raw = bytes(prop.bytes)
                if len(raw) < 500:
                    print(f"{prefix}  {prop.name} = \"{raw.decode(errors='replace')}\"")
                else:
                    print(f"{prefix}  {prop.name} = <{len(raw)} bytes>")
            else:
                try:
                    s = bytes(prop.bytes).decode("ascii").rstrip("\x00")
                    print(f"{prefix}  {prop.name} = \"{s}\"")
                except:
                    print(f"{prefix}  {prop.name} = {list(prop)}")
        elif isinstance(prop, pyfdt.FdtNode):
            print_node(prop, indent + 1)

print_node(fdt.get_rootnode())
