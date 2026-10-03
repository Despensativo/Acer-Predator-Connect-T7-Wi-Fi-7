with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

keywords = [b"rsa", b"signature", b"key-", b"fit_image_check_sig", b"image-sig", b"Bad signature", b"Signature check"]
for kw in keywords:
    pos = 0
    found = 0
    while True:
        idx = data.find(kw, pos)
        if idx == -1: break
        found += 1
        pos = idx + 1
    print(f"Keyword {kw}: {found} occurrences")
