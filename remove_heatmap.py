import os

# 1. Update DrugDiscoveryTable.tsx to remove heatmap
path = 'src/components/DrugDiscoveryTable.tsx'
with open(path, 'r', encoding='utf-8') as f: content = f.read()
heatmap_start = content.find('<div className="mt-4 flex flex-col items-center border-t')
heatmap_end = content.find('</>', heatmap_start)
if heatmap_start != -1 and heatmap_end != -1:
    content = content[:heatmap_start] + content[heatmap_end:]
with open(path, 'w', encoding='utf-8') as f: f.write(content)

# 2. Update README to remove heatmap mention
readme_path = 'README.md'
with open(readme_path, 'r', encoding='utf-8') as f: readme = f.read()
readme = readme.replace('",   """?"? Reversal_Heatmap.png\n', '')
readme = readme.replace('",   "o"?"? Reversal_Heatmap.png\n', '')
with open(readme_path, 'w', encoding='utf-8') as f: f.write(readme)

# 3. Delete Reversal_Heatmap.png
if os.path.exists('public/data/Reversal_Heatmap.png'):
    os.remove('public/data/Reversal_Heatmap.png')

print("Heatmap removed successfully.")
