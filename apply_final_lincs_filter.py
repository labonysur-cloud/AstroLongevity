import json

nb_path = 'notebooks/AstroLongevity_Data_Pipeline.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        src = "".join(cell['source'])
        if 'df_drugs = df_drugs.sort_values(' in src:
            filter_code = """
    # Drop LINCS artifacts and drugs without valid PubChem IDs
    df_drugs = df_drugs[
        (~df_drugs["Perturbagen"].astype(str).str.contains("-666")) & 
        (df_drugs["PubChem_ID"] != "Unknown")
    ].reset_index(drop=True)
"""
            if '# Drop LINCS artifacts' not in src:
                src = src.replace(
                    'df_drugs = df_drugs.sort_values("Reversal_Score", ascending=False).drop_duplicates(subset=["Perturbagen_ID"]).reset_index(drop=True)',
                    'df_drugs = df_drugs.sort_values("Reversal_Score", ascending=False).drop_duplicates(subset=["Perturbagen_ID"]).reset_index(drop=True)\n' + filter_code
                )
                
                # Split lines carefully to preserve notebook format
                lines = src.split('\n')
                cell['source'] = [line + '\n' for line in lines[:-1]] + ([lines[-1]] if lines[-1] else [])

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)

print("LINCS artifact filter applied.")
