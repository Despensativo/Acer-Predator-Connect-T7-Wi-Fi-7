from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
source = Path("/home/builder/openwrt/target/linux/qualcommbe/dts/ipq5332-acer-predator-t7.dts").read_text()
base = (BASE / "fontes/t7-diagnostico.dts").read_text()
def section(name):
    start = source.index("&" + name + " {")
    braces = 0
    for index in range(source.index("{", start), len(source)):
        braces += (source[index] == "{") - (source[index] == "}")
        if braces == 0:
            return source[start:index+2]
    raise ValueError("No nao terminado")
base = base.replace('&qcom_ppe { status = "disabled"; };', section("qcom_ppe"))
base = base.replace('#include "qcom/ipq5332.dtsi"', '#include "qcom/ipq5332.dtsi"\n#include <dt-bindings/gpio/gpio.h>')
base += "\n" + "\n".join(section(name) for name in ("pcs0", "pcs1", "mdio", "tlmm")) + "\n"
base = base.replace("maxcpus=1 rdinit=/init", "maxcpus=1 rdinit=/init netconsole=6665@169.254.73.2/lan,6667@169.254.73.1/ff:ff:ff:ff:ff:ff")
with (BASE / "fontes/t7-diagnostico-net-v2.dts").open("x", encoding="utf-8") as stream:
    stream.write(base)
print("DTS candidato criado a partir de secoes locais existentes; nenhuma validacao no hardware.")
