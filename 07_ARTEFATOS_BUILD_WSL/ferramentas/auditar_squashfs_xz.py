"""Auditoria de metadados SquashFS; nao extrai em disco nem altera imagens."""
from pathlib import Path
import hashlib,json,struct,subprocess
BASE=Path(__file__).resolve().parents[1]
PROJECT=BASE.parent
def audit(rel):
    path=PROJECT/rel
    with path.open("rb") as stream:
        header=stream.read(160)
    flags=struct.unpack_from("<H",header,24)[0]
    result={"file":rel,"file_bytes":path.stat().st_size,
            "squashfs_bytes_used":struct.unpack_from("<Q",header,40)[0],
            "block_size":struct.unpack_from("<I",header,12)[0],
            "flags_hex":hex(flags),"compression_id":struct.unpack_from("<H",header,20)[0],
            "compressor_options_present":bool(flags&0x400)}
    with path.open("rb") as stream:result["sha256"]=hashlib.file_digest(stream,"sha256").hexdigest()
    if flags&0x400:
        meta=struct.unpack_from("<H",header,96)[0]
        assert meta&0x8000
        size=meta&0x7fff
        result["options_bytes"]=size
        result["options_hex"]=header[98:98+size].hex()
        result["first_word_dictionary_bytes"]=struct.unpack_from("<I",header,98)[0]
    wsl="/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/"+rel
    for name,args in [("superblock",["-s"]),("read_version",["-cat"]),
                      ("listing",["-ll"])]:
        command=["wsl","-d","Ubuntu","--","unsquashfs",*args,wsl]
        if name=="read_version":command.append("etc/version")
        run=subprocess.run(command,capture_output=True,text=True)
        entry={"returncode":run.returncode,"stderr":run.stderr}
        if name!="listing":entry["stdout"]=run.stdout
        else:
            entries=[]
            for line in run.stdout.splitlines():
                columns=line.split(); filename=columns[-1] if columns else ""
                if filename.startswith("squashfs-root/") and filename.count("/")==1:
                    entries.append(filename)
            entry["root_entries"]=entries
        result[name]=entry
    return result
result={"scope":"offline_read_only_no_hardware","images":[
 audit("Backups_MTD/backup_predator_t7_ubi_rootfs.bin"),
 audit("Firmwares_Custom/openwrt_predator_t7_release_rootfs.bin")]}
with (BASE/"evidencias/squashfs-xz-20261002.json").open("x",encoding="utf-8") as stream:
    stream.write(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
for image in result["images"]:
    print(image["file"],"opts=",image.get("options_bytes",0),
          "version_read_rc=",image["read_version"]["returncode"],
          "top_level_entries=",len(image["listing"]["root_entries"]))
