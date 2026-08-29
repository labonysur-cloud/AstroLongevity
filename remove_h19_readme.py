with open('README.md', 'r', encoding='utf-8') as f:
    content = f.read()

target = """## Key Result (Validated)

The H19 gene in OSD-104 shows significant downregulation in spaceflight samples:

| Metric | Value | Source |
|---|---|---|
| Group Mean (Ground Control) | 113,282 | NASA OSD-104 |
| Group Mean (Spaceflight) | 76,442 | NASA OSD-104 |
| Log2 Fold Change | -0.5675 | NASA OSD-104 |
| Adjusted P-value | 5.57e-10 | NASA OSD-104 |
| Manual cross-check | log2(76442/113282) = -0.568 | Calculated |

The manual calculation matches the NASA reference to three significant figures, confirming the pipeline reads authentic, unmodified NASA data.

---

"""

content = content.replace(target, "")

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(content)
