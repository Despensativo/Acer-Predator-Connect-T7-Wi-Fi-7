import pyfdt.pyfdt as pyfdt
with open(r"H:\FEITOS COM IA\Acer-Predator-Connect-T7\3 - Ferramentas de Recuperacao\acionar_tftp.itb", "rb") as f:
    fdt = pyfdt.FdtBlobParse(f).to_fdt()

for node in fdt.get_rootnode():
    if isinstance(node, pyfdt.FdtNode):
        for sub in node:
            if isinstance(sub, pyfdt.FdtNode):
                for p in sub:
                    if isinstance(p, pyfdt.FdtProperty) and p.name == "data":
                        try:
                            print(f"{sub.name}: {bytes(p.bytes).decode('ascii')}")
                        except:
                            print(f"{sub.name}: <binary {len(p)} bytes>")
