import json
with open('notebooks/AstroLongevity_Data_Pipeline.ipynb', encoding='utf-8') as f:
    nb = json.load(f)
for c in nb['cells']:
    if c['cell_type'] == 'code':
        source = ''.join(c['source'])
        if '.csv' in source:
            print("--- CELL ---")
            for line in source.split('\n'):
                if '.csv' in line:
                    print(line.strip())
