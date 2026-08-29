import json
with open('notebooks/AstroLongevity_Data_Pipeline.ipynb', 'r', encoding='utf-8') as f: 
    nb = json.load(f)
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        source = source.replace('print(f"  {len(up_genes_human)} Upregulated orthologs mapped")', 'print(f"  {len(up_sig)} input upregulated mouse genes -> {len(up_genes_human)} human homologs")')
        source = source.replace('print(f"  {len(dn_genes_human)} Downregulated orthologs")', 'print(f"  {len(dn_sig)} input downregulated mouse genes -> {len(dn_genes_human)} human homologs")')
        
        # Remove the weird double export I created in Cell 8
        if 'l1000_query.json' in source and 'df_drugs.to_json' in source and 'l1000_drug_candidates.json' in source:
             weird_str = 'df_drugs.to_json(os.path.join(OUTPUT_DIR, "l1000_drug_candidates.json"), orient="records")\n    # Save raw API provenance\n    with open(os.path.join(OUTPUT_DIR, "l1000_query.json"), "w") as f:\n        json.dump(payload, f, indent=2)\n    with open(os.path.join(OUTPUT_DIR, "l1000_raw_response.json"), "w") as f:\n        json.dump(api_data, f, indent=2)\n'
             source = source.replace(weird_str, 'df_drugs.to_json(os.path.join(OUTPUT_DIR, "l1000_drug_candidates.json"), orient="records")')
             
        # Fix the "Drive" claim
        source = source.replace('print(f"\\nSaved candidates to Drive: {drug_path}")', 'print(f"\\nSaved candidates locally: {drug_path}")')
        source = source.replace('print(f"\\nSignature saved to Drive: {sig_path}")', 'print(f"\\nSignature saved locally: {sig_path}")')
        
        # Splitlines while preserving newlines
        lines = source.splitlines(True)
        cell['source'] = lines

with open('notebooks/AstroLongevity_Data_Pipeline.ipynb', 'w', encoding='utf-8') as f: 
    json.dump(nb, f, indent=2)
print("Applied final targeted text fixes.")
