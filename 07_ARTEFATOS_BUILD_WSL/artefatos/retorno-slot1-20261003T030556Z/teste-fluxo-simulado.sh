C=0
mock(){ C=$((C+1)); echo MOCK_CALL_$C:"$*"; [ $C -ne $FAIL_AT ]; }
setenv(){ mock setenv "$@"; }
imxtract(){ mock imxtract "$@"; }
itest(){ mock itest "$@"; }
cmp.b(){ mock cmp.b "$@"; }
nand(){ mock nand "$@"; }
saveenv(){ mock saveenv "$@"; }
reset(){ mock reset "$@"; }
echo T7_RETURN_SLOT1_CANDIDATE
if setenv filesize; then
echo T7_OK_CLEAR_SIZE_PRE0
else
echo T7_STOP_CLEAR_SIZE_PRE0
exit 1
fi
if imxtract 0x44000000 bc0 0x45000000; then
echo T7_OK_EXTRACT_PRE0
else
echo T7_STOP_EXTRACT_PRE0
exit 1
fi
if itest ${filesize} == 0x80000; then
echo T7_OK_SIZE_PRE0
else
echo T7_STOP_SIZE_PRE0
exit 1
fi
if cmp.b 0x45000000 0x44000cd8 0x80000; then
echo T7_OK_COMPARE_PRE0
else
echo T7_STOP_COMPARE_PRE0
exit 1
fi
if setenv filesize; then
echo T7_OK_CLEAR_SIZE_PRE1
else
echo T7_STOP_CLEAR_SIZE_PRE1
exit 1
fi
if imxtract 0x44000000 bc1 0x45000000; then
echo T7_OK_EXTRACT_PRE1
else
echo T7_STOP_EXTRACT_PRE1
exit 1
fi
if itest ${filesize} == 0x80000; then
echo T7_OK_SIZE_PRE1
else
echo T7_STOP_SIZE_PRE1
exit 1
fi
if cmp.b 0x45000000 0x44080d50 0x80000; then
echo T7_OK_COMPARE_PRE1
else
echo T7_STOP_COMPARE_PRE1
exit 1
fi
if nand device 0; then
echo T7_OK_NAND_DEVICE
else
echo T7_STOP_NAND_DEVICE
exit 1
fi
if setenv filesize; then
echo T7_OK_CLEAR_SIZE_WRITE0
else
echo T7_STOP_CLEAR_SIZE_WRITE0
exit 1
fi
if imxtract 0x44000000 bc0 0x45000000; then
echo T7_OK_EXTRACT_WRITE0
else
echo T7_STOP_EXTRACT_WRITE0
exit 1
fi
if itest ${filesize} == 0x80000; then
echo T7_OK_SIZE_WRITE0
else
echo T7_STOP_SIZE_WRITE0
exit 1
fi
if cmp.b 0x45000000 0x44000cd8 0x80000; then
echo T7_OK_COMPARE_WRITE0
else
echo T7_STOP_COMPARE_WRITE0
exit 1
fi
if nand erase 0x400000 0x80000; then
echo T7_OK_ERASE0
else
echo T7_STOP_ERASE0
exit 1
fi
if nand write 0x45000000 0x400000 0x80000; then
echo T7_OK_WRITE0
else
echo T7_STOP_WRITE0
exit 1
fi
if nand read 0x45000000 0x400000 0x80000; then
echo T7_OK_READBACK0
else
echo T7_STOP_READBACK0
exit 1
fi
if cmp.b 0x45000000 0x44000cd8 0x80000; then
echo T7_OK_VERIFY0
else
echo T7_STOP_VERIFY0
exit 1
fi
if setenv filesize; then
echo T7_OK_CLEAR_SIZE_WRITE1
else
echo T7_STOP_CLEAR_SIZE_WRITE1
exit 1
fi
if imxtract 0x44000000 bc1 0x45000000; then
echo T7_OK_EXTRACT_WRITE1
else
echo T7_STOP_EXTRACT_WRITE1
exit 1
fi
if itest ${filesize} == 0x80000; then
echo T7_OK_SIZE_WRITE1
else
echo T7_STOP_SIZE_WRITE1
exit 1
fi
if cmp.b 0x45000000 0x44080d50 0x80000; then
echo T7_OK_COMPARE_WRITE1
else
echo T7_STOP_COMPARE_WRITE1
exit 1
fi
if nand erase 0x480000 0x80000; then
echo T7_OK_ERASE1
else
echo T7_STOP_ERASE1
exit 1
fi
if nand write 0x45000000 0x480000 0x80000; then
echo T7_OK_WRITE1
else
echo T7_STOP_WRITE1
exit 1
fi
if nand read 0x45000000 0x480000 0x80000; then
echo T7_OK_READBACK1
else
echo T7_STOP_READBACK1
exit 1
fi
if cmp.b 0x45000000 0x44080d50 0x80000; then
echo T7_OK_VERIFY1
else
echo T7_STOP_VERIFY1
exit 1
fi
if setenv fsbootargs; then
echo T7_OK_ENV_ROOT
else
echo T7_STOP_ENV_ROOT
exit 1
fi
if setenv bootcmd bootipq; then
echo T7_OK_ENV_BOOTCMD
else
echo T7_STOP_ENV_BOOTCMD
exit 1
fi
if setenv bootargs 'console=ttyMSM0,115200n8'; then
echo T7_OK_ENV_BOOTARGS
else
echo T7_STOP_ENV_BOOTARGS
exit 1
fi
if saveenv; then
echo T7_OK_ENV_SAVE
else
echo T7_STOP_ENV_SAVE
exit 1
fi
echo T7_RETURN_VERIFIED
reset
