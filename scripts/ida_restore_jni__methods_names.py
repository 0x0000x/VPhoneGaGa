import re, idaapi

raw = open ( r"C:\Users\amgad\Desktop\Reverse Engineering\vphone_gaga\3.0.0\methods_strings.txt"  ).read()


raw, namef, mapf = raw.splitlines(), set(), {}
pat = re.compile(r'.*?0x([\dA-Fa-f]+): .*?([A-Za-z_][A-Za-z\d_]*::[A-Za-z_][A-Za-z\d_]*).*?')

for line in raw:
    match = pat.fullmatch(line)
    if match is not None:
        addr, name = int(match.group(1), 16), match.group(2)
        if name not in namef:
            mapf[addr] = name
            namef.add(name)

        for addr, name in mapf.items():
            func: idaapi.func_t = idaapi.get_func(addr)
            addr = func.start_ea
            idaapi.set_name(addr, name)
            print('0x%x -> %s' % (addr, name))