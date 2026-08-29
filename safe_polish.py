import json
import re
import os

nb_path = 'notebooks/AstroLongevity_Data_Pipeline.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell['source'])
        source = source.replace('validates it through three fail-closed quality control gates', 'validates structural and transcriptomic data integrity using explicit QC checks')
        source = source.replace('saves every output to Google Drive', "exports pipeline outputs to the project's `public/data` directory")
        source = source.replace('across independent NASA spaceflight missions (OSD-101, OSD-104)', 'across independent NASA spaceflight missions (OSD-101, OSD-104 ONLY)')
        
        # We assign it back. We split and add newlines cleanly
        lines = source.splitlines()
        cell['source'] = [line + '\n' for line in lines]
        if len(cell['source']) > 0:
            cell['source'][-1] = cell['source'][-1].rstrip('\n') # keep last line without newline if needed, but jupyter handles it
        
    elif cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        
        source = source.replace('from sklearn.preprocessing import StandardScaler\n', '')
        source = source.replace('import matplotlib.patches as mpatches\n', '')
        source = source.replace('import shutil\n', '')
        
        if 'def download_study_file' in source:
            source = source.replace('logger.info(f"Downloading: {target_file}', 'if os.path.exists(save_path):\n            logger.info(f"Using cached file: {target_file}")\n        else:\n            logger.info(f"Downloading from NASA OSDR: {target_file}')
            
        source = source.replace('OSD-21 cleanup: Grouped duplicate probes by SYMBOL mean.', 'OSD-21 cleanup: Applied probe-to-gene mean aggregation.')
        
        if 'PCA effectively separates' in source:
            source = source.replace('PCA effectively separates the flight and ground-control samples, indicating a strong transcriptomic association with the experimental condition.', 'Flight and ground-control samples separate in PCA space, indicating a strong association between the experimental condition and the observed transcriptomic variation.')
            
        source = source.replace('OSD-104 post-download processing benchmark', 'OSD-104 ingestion/QC/PCA benchmark')
        
        if 'def map_mouse_to_human' in source:
            source = source.replace('We strictly use only verified 1:1 orthologs. No uppercase fallbacks.', 'Maps mouse genes to human homologs using MyGene/HomoloGene. No uppercase fallbacks.')
            source = source.replace('print(f"  {len(up_genes_human)} Upregulated orthologs mapped")\\nprint(f"  {len(dn_genes_human)} Downregulated orthologs")', 'print(f"  {len(up_sig)} input upregulated mouse genes -> {len(up_genes_human)} human homologs")\\nprint(f"  {len(dn_sig)} input downregulated mouse genes -> {len(dn_genes_human)} human homologs")')
            source = source.replace('print("DRUG DISCOVERY: LINCS L1000 API INTEGRATION")', 'print("COMPUTATIONAL COUNTERMEASURE PRIORITIZATION")')
            source = source.replace('print("\\nTop 15 Candidate Countermeasures (Signature Reversal):")', 'print("\\nTop 15 Computationally Prioritized Perturbations")\\n    print("Note: Higher score indicates stronger computational opposition to the supplied gene signature under the L1000CDS2 gene-set search; this is not evidence of therapeutic efficacy.")')
            
            prov_export = '''
    # Save raw API provenance
    with open(os.path.join(OUTPUT_DIR, "l1000_query.json"), "w") as f:
        json.dump(payload, f, indent=2)
    with open(os.path.join(OUTPUT_DIR, "l1000_raw_response.json"), "w") as f:
        json.dump(api_data, f, indent=2)
'''
            source = source.replace('df_drugs.to_json(os.path.join(OUTPUT_DIR, "l1000_drug_candidates.json"), orient="records")', 'df_drugs.to_json(os.path.join(OUTPUT_DIR, "l1000_drug_candidates.json"), orient="records")' + prov_export)

        if 'df_drugs.to_json(os.path.join(OUTPUT_DIR, "l1000_drug_candidates.json")' in source:
            prov_export = '''
    # Save raw API provenance
    if 'payload' in locals():
        with open(os.path.join(OUTPUT_DIR, "l1000_query.json"), "w") as f:
            json.dump(payload, f, indent=2)
    if 'api_data' in locals():
        with open(os.path.join(OUTPUT_DIR, "l1000_raw_response.json"), "w") as f:
            json.dump(api_data, f, indent=2)
'''
            if 'l1000_query.json' not in source:
                source = source.replace('print(f"\\nJSON data exported successfully to: {OUTPUT_DIR}")', prov_export + '\\n    print(f"\\nJSON data exported successfully to: {OUTPUT_DIR}")')

        # Clean line breaks to exactly match Jupyter format
        lines = source.splitlines()
        if source.endswith('\\n'):
            cell['source'] = [line + '\\n' for line in lines]
        else:
            cell['source'] = [line + '\\n' for line in lines]
            if len(cell['source']) > 0:
                cell['source'][-1] = cell['source'][-1].rstrip('\\n')

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)

print("Safe string replacement applied.")
