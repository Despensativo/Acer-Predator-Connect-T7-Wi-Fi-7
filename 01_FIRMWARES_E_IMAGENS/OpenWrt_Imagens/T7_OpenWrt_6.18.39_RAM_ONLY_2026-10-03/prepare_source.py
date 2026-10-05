#!/usr/bin/env python3
"""Prepare an internal, RAM-only T7 OpenWrt prototype from a pinned tree.

This script reads the existing project DTS as data. It never writes to H: or to
a router. The generated profile intentionally has no persistent image recipe.
"""

from pathlib import Path
import hashlib


SOURCE = Path('/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/03_ENGENHARIA_REVERSA/DeviceTree_DTS/ipq5332-acer-predator-t7.dts')
TREE = Path('/home/builder/t7-openwrt-618')
DTS = TREE / 'target/linux/qualcommbe/dts/ipq5332-acer-predator-t7.dts'
IMAGE_MK = TREE / 'target/linux/qualcommbe/image/ipq53xx.mk'

raw = SOURCE.read_bytes()
text = raw.decode('utf-8').replace('\r\n', '\n')
if 'compatible = "acer,predator-t7"' not in text:
    raise SystemExit('Unexpected source DTS identity')

# Zero MAC addresses are placeholders in the earlier candidate, not hardware
# identifiers. Do not bake them into a new image.
text = text.replace('\t\t\tlocal-mac-address = [00 00 00 00 00 00];\n', '')
if 'local-mac-address = [00 00 00 00 00 00]' in text:
    raise SystemExit('Zero MAC placeholder remains')

# Initial boot experiment excludes the unvalidated radio path. Ethernet stays
# present for inspection; QCA8386 switch support remains outstanding.
text += '\n/* RAM-only prototype: PCIe radio path awaits T7-specific validation. */\n'
text += '&pcie1 { status = "disabled"; };\n'
text += '&pcie1_phy { status = "disabled"; };\n'
text += '''
/* Memory map copied selectively from the T7 live FDT, not generic MI01.6. */
/ {
    memory@40000000 {
        reg = <0x0 0x40000000 0x0 0x40000000>;
    };

    reserved-memory {
        #address-cells = <2>;
        #size-cells = <2>;
        ranges;

        /* Bootloader, SBL, TZ, SMEM and a covering WCSS reservation are
         * already supplied by upstream ipq5332.dtsi. */
        t7_tzapp: tzapp@49b00000 { no-map; reg = <0x0 0x49b00000 0x0 0x600000>; };
        t7_mlo: mlo-global-mem@4db00000 { no-map; reg = <0x0 0x4db00000 0x0 0x1100000>; };
        t7_qcn0: qcn9224-pcie0@4ec00000 { no-map; reg = <0x0 0x4ec00000 0x0 0x3200000>; };
        t7_qcn1: qcn9224-pcie1@51e00000 { no-map; reg = <0x0 0x51e00000 0x0 0x3200000>; };
    };
};
'''
DTS.write_text(text, encoding='utf-8', newline='\n')

profile = '''
# RAM-only T7 development profile. No factory/sysupgrade image is emitted.
define Device/acer_predator-t7
\tDEVICE_VENDOR := Acer
\tDEVICE_MODEL := Predator Connect T7 (RAM prototype)
\tDEVICE_DTS_CONFIG := config@mi01.6
\tSOC := ipq5332
\tDEVICE_DTS := ipq5332-acer-predator-t7
\tSUPPORTED_DEVICES += acer,predator-t7
\tKERNEL_INITRAMFS := kernel-bin | lzma | fit lzma $$(KDIR)/image-$$(DEVICE_DTS).dtb
\tKERNEL_INITRAMFS_SUFFIX := .itb
\tIMAGES :=
\tDEVICE_PACKAGES := ethtool
endef
TARGET_DEVICES += acer_predator-t7
'''
mk = IMAGE_MK.read_text(encoding='utf-8')
if 'define Device/acer_predator-t7' not in mk:
    IMAGE_MK.write_text(mk.rstrip('\n') + '\n' + profile, encoding='utf-8', newline='\n')
elif '\tDEVICE_DTS := ipq5332-acer-predator-t7\n' not in mk:
    old = '\tSOC := ipq5332\n\tSUPPORTED_DEVICES += acer,predator-t7\n'
    if old not in mk:
        raise SystemExit('Existing T7 profile layout changed')
    IMAGE_MK.write_text(mk.replace(old, '\tSOC := ipq5332\n\tDEVICE_DTS := ipq5332-acer-predator-t7\n\tSUPPORTED_DEVICES += acer,predator-t7\n'), encoding='utf-8', newline='\n')

for path in (DTS, IMAGE_MK):
    print(f'{path}: {path.stat().st_size} bytes sha256={hashlib.sha256(path.read_bytes()).hexdigest()}')
