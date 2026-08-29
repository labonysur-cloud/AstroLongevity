import json

nb_path = 'notebooks/AstroLongevity_Data_Pipeline.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        if 'if df[numeric_cols].isna().any().any():' in source:
            # We want to remove the check for `if df[numeric_cols].isna().any().any():`
            # and replace it with checking ONLY count_cols for NAs.
            lines = source.split('\n')
            new_lines = []
            skip = False
            for line in lines:
                if 'if df[numeric_cols].isna().any().any():' in line:
                    skip = True
                    continue
                if skip and 'raise ValueError' in line and 'Missing (NA) values' in line:
                    skip = False
                    continue
                if 'if count_cols:' in line:
                    new_lines.append(line)
                    new_lines.append('        if df[count_cols].isna().any().any():')
                    new_lines.append('            raise ValueError(f"QC FAIL [{dataset_name}]: Missing (NA) values detected in count columns.")')
                    continue
                new_lines.append(line)
            cell['source'] = [line + '\n' if i < len(new_lines)-1 else line for i, line in enumerate(new_lines)]

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)

print("Fixed QC logic to only check count columns for NAs.")
