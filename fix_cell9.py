import json

nb_path = 'notebooks/AstroLongevity_Data_Pipeline.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        if 'FRONTEND HAND-OFF' in source:
            new_source = '''# Cell 9: Frontend Data Export
#
# Exports all pipeline outputs as static JSON files to the Next.js `public/data/` 
# directory for lightning-fast frontend dashboard rendering.

import os
import json

print("FRONTEND HAND-OFF")
print("-" * 60)

# Static JSON Export for Next.js Frontend
try:
    if 'pca_df' in locals():
        pca_df.to_json(os.path.join(OUTPUT_DIR, "pca_coordinates.json"), orient="records")
    if 'final_sig' in locals():
        final_sig.head(100).to_json(os.path.join(OUTPUT_DIR, "concordant_signature.json"), orient="records")
    if 'df_bench_results' in locals():
        df_bench_results.to_json(os.path.join(OUTPUT_DIR, "benchmark_stats.json"), orient="records")
    if 'df_drugs' in locals():
        df_drugs.to_json(os.path.join(OUTPUT_DIR, "l1000_drug_candidates.json"), orient="records")

    print(f"\\nJSON data exported successfully to: {OUTPUT_DIR}")

except Exception as e:
    print(f"Failed to export JSON: {e}")
'''
            cell['source'] = [line + '\n' for line in new_source.split('\n')]
            
with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)
