with open(r'\\wsl.localhost\Ubuntu\home\builder\appsbl.bin', 'rb') as f:
    f.seek(0x12000)
    code = f.read(0x78048)

with open(r'\\wsl.localhost\Ubuntu\home\builder\appsbl_code.bin', 'wb') as f:
    f.write(code)

print('Extracted successfully!')
