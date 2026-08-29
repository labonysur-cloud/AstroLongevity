import json

nb_path = 'notebooks/AstroLongevity_Data_Pipeline.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        if 'for sid in DATASETS:' in source:
            lines = source.split('\n')
            new_lines = []
            for line in lines:
                new_lines.append(line)
                if line.strip() == 'else:':
                    new_lines.append('        print(f"  {sid}: FAILED - see error above")')
                    break
            cell['source'] = [line + '\n' if i < len(new_lines)-1 else line for i, line in enumerate(new_lines)]

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)

print("Fixed Cell 3")
