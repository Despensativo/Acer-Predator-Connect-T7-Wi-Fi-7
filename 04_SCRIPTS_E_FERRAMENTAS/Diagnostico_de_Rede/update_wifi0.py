with open(r'C:\Users\User\.gemini\antigravity\scratch\build_config_turbinado.py', 'r') as fp:
    c = fp.read()

# Replace wifi0 settings in build_config_turbinado.py:
c = c.replace("option txpower '24'", "option txpower '25'")
c = c.replace("option htmode 'HT40'", "option htmode 'HT20'")

with open(r'C:\Users\User\.gemini\antigravity\scratch\build_config_turbinado.py', 'w') as fp:
    fp.write(c)

print('Updated build_config_turbinado.py with HT20 and txpower 25')
