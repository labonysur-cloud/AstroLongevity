import json
with open('notebooks/AstroLongevity_Data_Pipeline.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        new_source = []
        for line in cell['source']:
            if 'logger.info(f"Downloading: {target_file}  ->  {save_path}")' in line:
                line = line.replace('logger.info(f"Downloading: {target_file}  ->  {save_path}")', 'if os.path.exists(save_path):\n            logger.info(f"Using cached file: {target_file}")\n        else:\n            logger.info(f"Downloading from NASA OSDR: {target_file}")')
            new_source.append(line)
        final_source = []
        for line in new_source:
            parts = line.split('\n')
            for i in range(len(parts) - 1):
                final_source.append(parts[i] + '\n')
            if parts[-1]:
                final_source.append(parts[-1])
        cell['source'] = final_source
with open('notebooks/AstroLongevity_Data_Pipeline.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)
print("Fixed downloading log.")
