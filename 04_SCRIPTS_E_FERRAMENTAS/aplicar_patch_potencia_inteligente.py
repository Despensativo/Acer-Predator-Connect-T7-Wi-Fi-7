import socket
import time

lua_code = """local f = io.open('/www/luci-static/resources/view/network/wireless.js', 'r')
local content = f:read('*a')
f:close()

local old_target = "var stdPowers=[15,17,19,20,22,24,26,28,30];for(var j=0;j<stdPowers.length;j++){var p=stdPowers[j];if(!seen[p]){var mw=Math.round(Math.pow(10,p/10));this.value(p,'%d dBm (%d mW)'.format(p,mw));}}"

local new_replacement = [[var bandsPowers = {
    'wifi0': [ {p:16, label:'16 dBm (40 mW - Máximo 2.4 GHz)'}, {p:14, label:'14 dBm (25 mW)'}, {p:12, label:'12 dBm (16 mW)'}, {p:10, label:'10 dBm (10 mW - Econômico)'} ],
    'wifi1': [ {p:23, label:'23 dBm (200 mW - Máximo 5 GHz)'}, {p:22, label:'22 dBm (158 mW)'}, {p:20, label:'20 dBm (100 mW)'}, {p:18, label:'18 dBm (63 mW)'}, {p:15, label:'15 dBm (31 mW - Econômico)'} ],
    'wifi2': [ {p:15, label:'15 dBm (32 mW - Máximo 6 GHz / 320 MHz LPI)'}, {p:13, label:'13 dBm (20 mW)'}, {p:11, label:'11 dBm (12 mW)'}, {p:9, label:'9 dBm (8 mW - Econômico)'} ]
};
var pList = bandsPowers[section_id] || [ {p:20, label:'20 dBm'}, {p:15, label:'15 dBm'} ];
for(var j=0;j<pList.length;j++){
    this.value(pList[j].p, pList[j].label);
}]]

local s, e = content:find(old_target, 1, true)
if s then
    content = content:sub(1, s-1) .. new_replacement .. content:sub(e+1)
    local out = io.open('/www/luci-static/resources/view/network/wireless.js', 'w')
    out:write(content)
    out:close()
    print('PATCH_SUCCESS')
else
    print('PATCH_TARGET_NOT_FOUND')
end
"""

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)
s.connect(('192.168.76.1', 23))
time.sleep(0.5)
data = s.recv(4096).decode('utf-8', errors='ignore')
if 'login:' in data:
    s.sendall(b'root\n')
    time.sleep(0.5)
    data += s.recv(4096).decode('utf-8', errors='ignore')
    s.sendall(b'admin0100\n')
    time.sleep(0.5)
    data += s.recv(4096).decode('utf-8', errors='ignore')

def run_cmd(cmd):
    s.sendall((cmd + '\n').encode())
    time.sleep(0.8)
    res = ''
    while True:
        try:
            chunk = s.recv(8192).decode('utf-8', errors='ignore')
            if not chunk: break
            res += chunk
            if '#' in chunk or '$' in chunk: break
        except socket.timeout:
            break
    return res

run_cmd('cp /www/luci-static/resources/view/network/wireless.js.bak /www/luci-static/resources/view/network/wireless.js')
run_cmd('cat << \\\'EOF\\\' > /tmp/patch_wireless.lua\n' + lua_code.strip() + '\nEOF')
res = run_cmd('lua /tmp/patch_wireless.lua')
print('Result:', res)
s.close()
