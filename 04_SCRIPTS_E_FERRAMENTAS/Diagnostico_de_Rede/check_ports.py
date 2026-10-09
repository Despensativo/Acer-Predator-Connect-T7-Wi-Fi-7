import socket

target = "192.168.73.2"
ports = [22, 23, 80, 443]

print(f"Scanning {target}:")
for p in ports:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2.0)
    res = s.connect_ex((target, p))
    s.close()
    status = "OPEN" if res == 0 else f"CLOSED (code {res})"
    print(f"  Port {p:3}: {status}")
