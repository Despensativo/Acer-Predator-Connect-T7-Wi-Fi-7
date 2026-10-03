import socket
import struct
import time

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind(('0.0.0.0', 67))

print("DHCP Listener / Server running on UDP 67 (active for 300s)...")
print("Waiting for DHCP DISCOVER / REQUEST from router...")

s.settimeout(5)
start = time.time()
while time.time() - start < 300:
    try:
        data, addr = s.recvfrom(2048)
        mac = ':'.join(f'{b:02x}' for b in data[28:34])
        print(f"[{time.strftime('%H:%M:%S')}] PACKET FROM MAC: {mac}, source: {addr}")
        
        idx = 240
        msg_type = None
        hostname = "unknown"
        while idx < len(data) - 2:
            opt = data[idx]
            if opt == 255:
                break
            if opt == 0:
                idx += 1
                continue
            opt_len = data[idx+1]
            opt_val = data[idx+2:idx+2+opt_len]
            if opt == 53 and opt_len >= 1:
                msg_type = opt_val[0]
            elif opt == 12:
                hostname = opt_val.decode('ascii', errors='ignore')
            idx += 2 + opt_len
            
        type_names = {1: "DISCOVER", 2: "OFFER", 3: "REQUEST", 4: "DECLINE", 5: "ACK", 6: "NAK"}
        type_str = type_names.get(msg_type, f"TYPE_{msg_type}")
        print(f" -> DHCP {type_str} from {hostname} ({mac})")
        
        xid = data[4:8]
        chaddr = data[28:44]
        offered_ip = socket.inet_aton("192.168.1.100")
        server_ip = socket.inet_aton("192.168.1.5")
        
        resp = bytearray()
        resp += b'\x02\x01\x06\x00'
        resp += xid
        resp += b'\x00\x00\x80\x00'
        resp += b'\x00'*4
        resp += offered_ip
        resp += server_ip
        resp += b'\x00'*4
        resp += chaddr
        resp += b'\x00'*64
        resp += b'\x00'*128
        resp += b'\x63\x82\x53\x63'
        
        resp_type = 2 if msg_type == 1 else 5
        resp += bytes([53, 1, resp_type])
        resp += bytes([54, 4]) + server_ip
        resp += bytes([51, 4]) + struct.pack('>I', 86400)
        resp += bytes([1, 4]) + socket.inet_aton("255.255.255.0")
        resp += bytes([3, 4]) + server_ip
        resp += bytes([6, 4]) + server_ip
        resp += b'\xff'
        
        s.sendto(resp, ('255.255.255.255', 68))
        print(f" -> Sent DHCP {'OFFER' if resp_type == 2 else 'ACK'} with IP 192.168.1.100 to {mac}!")
    except socket.timeout:
        pass

print("DHCP Listener finished.")
