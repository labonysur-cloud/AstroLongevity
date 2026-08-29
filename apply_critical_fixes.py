import json
import os
import shutil

# 1. Force clear corrupted cache to guarantee a fresh, successful OSD-21 download
cache_dir = os.path.join('notebooks', 'nasa_data')
if os.path.exists(cache_dir):
    try:
        shutil.rmtree(cache_dir)
    except Exception:
        pass

nb_path = 'notebooks/AstroLongevity_Data_Pipeline.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'markdown':
        src = "".join(cell['source'])
        src = src.replace('Three QC gates', 'QC checks')
        src = src.replace('Three fail-closed', 'Explicit')
        src = src.replace('saves every output to Google Drive', 'exports pipeline outputs to the project\'s `public/data` directory')
        src = src.replace('Our pipeline performs differential expression', 'Our pipeline consumes NASA OSDR differential-expression outputs and performs cross-study concordance analysis')
        cell['source'] = [line + '\n' for line in src.split('\n')[:-1]]
        
    elif cell['cell_type'] == 'code':
        src = "".join(cell['source'])
        
        # Implement Fail-Fast execution in Cell 3
        if 'DATASETS = ["OSD-21", "OSD-101", "OSD-104"]' in src:
            if 'failed_datasets = []' not in src:
                src = src.replace('for study_id in DATASETS:', 'failed_datasets = []\nfor study_id in DATASETS:')
                src = src.replace('except Exception as err:\n        logger.error(f"FAILED for {study_id}: {err}")', 'except Exception as err:\n        logger.exception(f"FAILED for {study_id}: {err}")\n        failed_datasets.append(study_id)\n\nif failed_datasets:\n    raise RuntimeError(f"Pipeline stopped because datasets failed: {failed_datasets}")')
            src = "\n".join([line for line in src.split('\n') if 'FAILED - see error' not in line])
            cell['source'] = [line + '\n' for line in src.split('\n')[:-1]]
            
        # Implement Pre-Merge duplicate checking in Cell 7
        if 'concordant = pd.merge(df101_sig, df104_sig, on="SYMBOL"' in src:
            if 'duplicated().any()' not in src:
                check_code = """
# Validate uniqueness before merge to prevent many-to-many explosion
if df101_sig["SYMBOL"].duplicated().any() or df104_sig["SYMBOL"].duplicated().any():
    logger.warning("Duplicate SYMBOLs detected before concordance merge. Dropping duplicates.")
    df101_sig = df101_sig.drop_duplicates(subset=["SYMBOL"])
    df104_sig = df104_sig.drop_duplicates(subset=["SYMBOL"])
"""
                src = src.replace('concordant = pd.merge(df101_sig, df104_sig, on="SYMBOL"', check_code + '\nconcordant = pd.merge(df101_sig, df104_sig, on="SYMBOL"')
                cell['source'] = [line + '\n' for line in src.split('\n')[:-1]]

# Completely rewrite Cell 8 to implement strict 1:1 Orthology Mapping and Export
cell8_src = """# Cell 8: Computational Countermeasure Prioritization via LINCS L1000
#
# Maps mouse genes to human homologs using MyGene/HomoloGene with explicit 1:1 validation.
# Queries the Ma'ayan Lab L1000CDS2 API to identify candidate small-molecule perturbagens.

import requests
import pandas as pd
import os

if 'final_sig' not in locals():
    raise RuntimeError("Signature not found. Run Cell 7 first.")

print("COMPUTATIONAL COUNTERMEASURE PRIORITIZATION")
print("-" * 60)

up_sig = final_sig[final_sig["Average_Log2fc"] > 0].head(50)
dn_sig = final_sig[final_sig["Average_Log2fc"] < 0].tail(50)

map_path = os.path.join(OUTPUT_DIR, "mouse_human_orthology.csv")
if os.path.exists(map_path):
    os.remove(map_path)

def map_mouse_to_human(mouse_symbols, label):
    url = "https://mygene.info/v3/query"
    mapping = []
    try:
        res = requests.post(url, data={'q': ','.join(mouse_symbols), 'scopes': 'symbol', 'fields': 'homologene', 'species': 'mouse'})
        if res.status_code == 200:
            for item in res.json():
                m_sym = item.get('query')
                if 'homologene' in item and 'genes' in item['homologene']:
                    h_matches = [str(g[1]) for g in item['homologene']['genes'] if g[0] == 9606]
                    if len(h_matches) == 1:
                        mapping.append({"Mouse_Symbol": m_sym, "Human_GeneID": h_matches[0], "Direction": label})
            if mapping:
                df_map = pd.DataFrame(mapping)
                # Enforce bidirectional 1:1 uniqueness
                df_map = df_map.drop_duplicates(subset=["Human_GeneID"], keep=False)
                df_map = df_map.drop_duplicates(subset=["Mouse_Symbol"], keep=False)
                
                res2 = requests.post(url, data={'q': ','.join(df_map['Human_GeneID'].tolist()), 'scopes': 'entrezgene', 'fields': 'symbol', 'species': 'human'})
                if res2.status_code == 200:
                    h_dict = {str(i.get('query')): i.get('symbol') for i in res2.json() if 'symbol' in i}
                    df_map['Human_Symbol'] = df_map['Human_GeneID'].map(h_dict)
                    df_map = df_map.dropna(subset=['Human_Symbol'])
                    df_map['Mapping_Type'] = '1:1'
                    
                    hdr = not os.path.exists(map_path)
                    df_map.to_csv(map_path, mode='a', header=hdr, index=False)
                    
                    print(f"  {len(mouse_symbols)} input {label} mouse genes -> {len(df_map)} strict 1:1 human orthologs")
                    return df_map['Human_Symbol'].tolist()
    except Exception as e:
        print(f"Mapping error: {e}")
    return []

up_genes_human = map_mouse_to_human(up_sig["SYMBOL"].tolist(), "upregulated")
dn_genes_human = map_mouse_to_human(dn_sig["SYMBOL"].tolist(), "downregulated")

url = "https://maayanlab.cloud/L1000CDS2/query"
payload = {
    "data": {"upGenes": up_genes_human, "dnGenes": dn_genes_human},
    "config": {"aggravate": False, "searchMethod": "geneSet", "share": False, "combination": False, "db-version": "latest"}
}

response = requests.post(url, json=payload, timeout=30)
response.raise_for_status()
api_data = response.json()

candidates = []
for entry in api_data.get("topMeta", []):
    candidates.append({
        "Drug_Name": entry.get("pert_desc", "Unknown"),
        "Reversal_Score": round(entry.get("score", 0), 4),
        "Cell_Line": entry.get("cell_id", ""),
        "Dose": f"{entry.get('pert_dose', '')} {entry.get('pert_dose_unit', '')}",
        "Time": f"{entry.get('pert_time', '')} {entry.get('pert_time_unit', '')}",
        "PubChem_ID": entry.get("pubchem_id", ""),
        "Perturbagen_ID": entry.get("pert_id", "")
    })

df_drugs = pd.DataFrame(candidates)
if not df_drugs.empty:
    df_drugs = df_drugs.sort_values("Reversal_Score", ascending=False).drop_duplicates(subset=["Perturbagen_ID"]).reset_index(drop=True)
    print("\\nTop 15 Computationally Prioritized Perturbations")
    print("Note: Higher score indicates stronger computational opposition to the supplied gene signature under the L1000CDS2 gene-set search; this is not evidence of therapeutic efficacy.")
    display(df_drugs.head(15))
    drug_path = os.path.join(OUTPUT_DIR, "L1000_Candidate_Drugs.csv")
    df_drugs.to_csv(drug_path, index=False)
    print(f"\\nSaved candidates locally: {drug_path}")
else:
    print("\\nNo drugs returned from L1000CDS2 API.")
"""
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code' and 'def map_mouse_to_human' in "".join(cell['source']):
        nb['cells'][i]['source'] = [line + '\n' for line in cell8_src.split('\n')[:-1]]
        break

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)

print("Critical fixes applied.")
