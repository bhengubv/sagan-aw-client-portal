import fitz
p = r"C:\Users\tbeng\Downloads\PRD AI Engineer Test.pdf"
o = r"C:\Users\tbeng\Downloads\_aw_test_frames\prd_text.txt"
d = fitz.open(p)
parts = []
for i, page in enumerate(d):
    txt = page.get_text("text")
    parts.append(f"\n========== PAGE {i+1} ==========\n{txt}")
full = "\n".join(parts)
with open(o, "w", encoding="utf-8") as f:
    f.write(full)
print("wrote", len(full), "chars to", o)
