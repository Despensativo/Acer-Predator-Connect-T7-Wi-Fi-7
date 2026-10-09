import urllib.request
import re

try:
    html = urllib.request.urlopen('http://192.168.73.2/pub/dist/index.html', timeout=3).read().decode('utf-8', errors='ignore')
    scripts = re.findall(r'src=["\']([^"\']+\.js)["\']', html)
    print('Scripts in index.html:', scripts)
    for s in scripts:
        url = f'http://192.168.73.2/pub/dist/{s}'
        try:
            data = urllib.request.urlopen(url, timeout=5).read().decode('utf-8', errors='ignore')
            for k in ['web_cgi', 'enDataX', 'login_telnet', 'set_telnet', 'set_usb_storage', 'L6bb2tAt', 'hobh264Tk', 'bkcx1z']:
                if k in data:
                    print(f'Found {k} in {s}!')
            # Check what cgi or endpoints exist
            cgis = set(re.findall(r'/[a-zA-Z0-9_-]+\.cgi|/cgi-bin/[a-zA-Z0-9_-]+', data))
            print(f'Endpoints in {s}:', cgis)
        except Exception as e:
            print(f'Error fetching {url}: {e}')
except Exception as ex:
    print(f'Error: {ex}')
