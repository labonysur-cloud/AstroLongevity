import json
import os

nb_path = 'notebooks/AstroLongevity_Data_Pipeline.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'markdown':
        new_source = []
        for line in cell['source']:
            line = line.replace('validates it through three fail-closed quality control gates', 'validates structural and transcriptomic data integrity using explicit QC checks')
            line = line.replace('saves every output to Google Drive', "exports pipeline outputs to the project's `public/data` directory")
            line = line.replace('across independent NASA spaceflight missions (OSD-101, OSD-104)', 'across independent NASA spaceflight missions (OSD-101, OSD-104 ONLY)')
            new_source.append(line)
        cell['source'] = new_source
        
    elif cell['cell_type'] == 'code':
        new_source = []
        for line in cell['source']:
            if 'from sklearn.preprocessing import StandardScaler' in line: continue
            if 'import matplotlib.patches as mpatches' in line: continue
            if 'import shutil' in line: continue
            
            line = line.replace('logger.info(f"Downloading: {target_file}")', 'if os.path.exists(save_path):\n            logger.info(f"Using cached file: {target_file}")\n        else:\n            logger.info(f"Downloading from NASA OSDR: {target_file}")')
            line = line.replace('OSD-21 cleanup: Grouped duplicate probes by SYMBOL mean.', 'OSD-21 cleanup: Applied probe-to-gene mean aggregation.')
            line = line.replace('PCA effectively separates the flight and ground-control samples, indicating a strong transcriptomic association with the experimental condition.', 'Flight and ground-control samples separate in PCA space, indicating a strong association between the experimental condition and the observed transcriptomic variation.')
            line = line.replace('OSD-104 post-download processing benchmark', 'OSD-104 ingestion/QC/PCA benchmark')
            line = line.replace('We strictly use only verified 1:1 orthologs. No uppercase fallbacks.', 'Maps mouse genes to human homologs using MyGene/HomoloGene. No uppercase fallbacks.')
            line = line.replace('print(f"  {len(up_genes_human)} Upregulated orthologs mapped")', 'print(f"  {len(up_sig)} input upregulated mouse genes -> {len(up_genes_human)} human homologs")')
            line = line.replace('print(f"  {len(dn_genes_human)} Downregulated orthologs")', 'print(f"  {len(dn_sig)} input downregulated mouse genes -> {len(dn_genes_human)} human homologs")')
            line = line.replace('print("DRUG DISCOVERY: LINCS L1000 API INTEGRATION")', 'print("COMPUTATIONAL COUNTERMEASURE PRIORITIZATION")')
            line = line.replace('print("\\nTop 15 Candidate Countermeasures (Signature Reversal):")', 'print("\\nTop 15 Computationally Prioritized Perturbations")\n    print("Note: Higher score indicates stronger computational opposition to the supplied gene signature under the L1000CDS2 gene-set search; this is not evidence of therapeutic efficacy.")')
            
            line = line.replace('print(f"\\nSaved candidates to Drive: {drug_path}")', 'print(f"\\nSaved candidates locally: {drug_path}")')
            line = line.replace('print(f"\\nSignature saved to Drive: {sig_path}")', 'print(f"\\nSignature saved locally: {sig_path}")')
            
            if 'df_drugs.to_json(os.path.join(OUTPUT_DIR, "l1000_drug_candidates.json"), orient="records")' in line and cell['source'][0].startswith('# Cell 9'):
                new_source.append(line)
                new_source.append('    \n')
                new_source.append('    # Save raw API provenance\n')
                new_source.append('    if \'payload\' in locals():\n')
                new_source.append('        with open(os.path.join(OUTPUT_DIR, "l1000_query.json"), "w") as f:\n')
                new_source.append('            json.dump(payload, f, indent=2)\n')
                new_source.append('    if \'api_data\' in locals():\n')
                new_source.append('        with open(os.path.join(OUTPUT_DIR, "l1000_raw_response.json"), "w") as f:\n')
                new_source.append('            json.dump(api_data, f, indent=2)\n')
                continue
                
            new_source.append(line)
            
        # Re-split everything by \n in case I inserted \n inside strings, to ensure Jupyter format is correct
        final_source = []
        for line in new_source:
            parts = line.split('\n')
            for i in range(len(parts) - 1):
                final_source.append(parts[i] + '\n')
            if parts[-1]:
                final_source.append(parts[-1])
                
        cell['source'] = final_source

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)

print("Safely replaced strings line-by-line.")
