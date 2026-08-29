import json

with open('notebooks/AstroLongevity_Data_Pipeline.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        src = "".join(cell['source'])
        if 'set101 = set(sig101["SYMBOL_STD"])' in src:
            src = src.replace('set101 = set(sig101["SYMBOL_STD"])', 'sig101["SYMBOL_STD"] = sig101["SYMBOL"].str.upper().str.strip()\nset101 = set(sig101["SYMBOL_STD"])')
            src = src.replace('set104 = set(sig104["SYMBOL_STD"])', 'sig104["SYMBOL_STD"] = sig104["SYMBOL"].str.upper().str.strip()\nset104 = set(sig104["SYMBOL_STD"])')
            src = src.replace('on="SYMBOL"\n)', 'on="SYMBOL_STD"\n)\nmerged["SYMBOL"] = merged["SYMBOL_x"] if "SYMBOL_x" in merged.columns else merged["SYMBOL"]')
        cell['source'] = [line + '\n' for line in src.split('\n')[:-1]]

with open('notebooks/AstroLongevity_Data_Pipeline.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)
