import json
from pathlib import Path
import re

nb_path = 'notebooks/AstroLongevity_Data_Pipeline.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    src = "".join(cell['source'])
    
    if cell['cell_type'] == 'markdown':
        src = src.replace("three-dataset", "two-dataset")
        src = src.replace("141 genes conserved across all three", "141 concordant genes from OSD-101 and OSD-104")
        src = src.replace("strict 1:1 human orthologs", "strict unique mouse-to-human homolog mappings")
        src = src.replace("variance stabilization", "reduce count-scale skew")
        src = src.replace("NASA data download runtime", "Cached-data ingestion and preprocessing runtime")
        src = src.replace("then copied to Google Drive at the end of this cell.", "")
        
    elif cell['cell_type'] == 'code':
        # Cell 2: OUTPUT_DIR
        if 'OUTPUT_DIR = "../public/data"' in src:
            src = src.replace('OUTPUT_DIR = "../public/data"', 'from pathlib import Path\nOUTPUT_DIR = str((Path.cwd().resolve().parent / "public" / "data").resolve())')
        
        # Cell 3: Caching & Checksum
        if 'pd.read_csv(save_path, nrows=5)' in src:
            src = src.replace('pd.read_csv(save_path, nrows=5)', 'pd.read_csv(save_path, low_memory=False) # Full parse to ensure integrity\n                import hashlib\n                sha256_hash = hashlib.sha256(open(save_path, "rb").read()).hexdigest()\n                logger.info(f"SHA256: {sha256_hash}")')
        src = src.replace('Using valid cached file', 'Using fully verified cached file')
        
        # Cell 5: Benchmark
        src = src.replace('Peak_RAM_MB', 'Peak_Python_RAM_MB')
        src = src.replace('Runtime: Local Benchmark', 'Runtime: Local Python Execution')
        
        # Cell 7: Merge checks
        if 'concordant = pd.merge(' in src:
            unique_checks = """
    if df101_sig["SYMBOL_STD"].duplicated().any(): raise ValueError("Duplicate normalized symbols in OSD-101")
    if df104_sig["SYMBOL_STD"].duplicated().any(): raise ValueError("Duplicate normalized symbols in OSD-104")
"""
            if 'raise ValueError("Duplicate normalized symbols' not in src:
                src = src.replace('concordant = pd.merge(', unique_checks.lstrip() + '    concordant = pd.merge(')
                
        # Cell 8: Orthology & PubChem & CSV rename
        if 'def map_mouse_to_human' in src:
            src = src.replace('"PubChem_ID": entry.get("pubchem_id", ""),', '"PubChem_ID": pubchem,')
            src = src.replace('"Drug_Name":', '"Perturbagen":')
            src = src.replace('L1000_Candidate_Drugs.csv', 'L1000_Perturbation_Candidates.csv')
            src = src.replace('df_drugs.to_json(os.path.join(OUTPUT_DIR, "l1000_drug_candidates.json"', 'df_drugs.to_json(os.path.join(OUTPUT_DIR, "l1000_perturbation_candidates.json"')
            
            src = src.replace('print(f"  Input {label} mouse genes: {len(mouse_symbols)}")', 'print(f"  Input {label} mouse genes: {len(mouse_symbols)}")\n                    print(f"  -> {len(mouse_symbols) - len(mapping)} dropped (no homolog or multiple matches)")\n                    print(f"  -> {len(mapping) - len(df_map)} dropped (duplicate resolution)")')
            
        # Cell 9: Metadata & Deprecation
        if 'import pkg_resources' in src:
            src = src.replace('import pkg_resources', 'from importlib.metadata import version')
            src = src.replace('pkg_resources.get_distribution("pandas").version', 'version("pandas")')
            src = src.replace('pkg_resources.get_distribution("numpy").version', 'version("numpy")')
            src = src.replace('pkg_resources.get_distribution("scikit-learn").version', 'version("scikit-learn")')
            src = src.replace('pkg_resources.get_distribution("requests").version', 'version("requests")')
            src = src.replace('"l1000_db_version": "latest (pinned to execution timestamp)"', '"l1000_db_version": "latest"')
            src = src.replace('L1000_Candidate_Drugs.csv', 'L1000_Perturbation_Candidates.csv')
            src = src.replace('l1000_drug_candidates.json', 'l1000_perturbation_candidates.json')
            
    lines = src.split('\n')
    cell['source'] = [line + '\n' for line in lines[:-1]] + ([lines[-1]] if lines[-1] else [])

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)

# Also update the React Component
react_file = 'src/components/DrugDiscoveryTable.tsx'
if os.path.exists(react_file):
    with open(react_file, 'r', encoding='utf-8') as f:
        react_src = f.read()
    
    react_src = react_src.replace('l1000_drug_candidates.json', 'l1000_perturbation_candidates.json')
    react_src = react_src.replace('Drug_Name', 'Perturbagen')
    react_src = react_src.replace('Drug Name', 'Perturbagen')
    
    with open(react_file, 'w', encoding='utf-8') as f:
        f.write(react_src)

print("Applied V4 audit fixes.")
