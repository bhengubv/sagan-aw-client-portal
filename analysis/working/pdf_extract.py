import fitz, json
p = r"C:\Users\tbeng\Downloads\PRD AI Engineer Test.pdf"
d = fitz.open(p)
print("=== META ===")
print("pages:", d.page_count)
print("metadata:", json.dumps(d.metadata, ensure_ascii=False))
total_img = 0
out = []
for i, page in enumerate(d):
    txt = page.get_text("text")
    imgs = page.get_images(full=True)
    total_img += len(imgs)
    out.append(f"\n========== PAGE {i+1} (images on page: {len(imgs)}, chars: {len(txt)}) ==========\n{txt}")
print("total embedded images:", total_img)
print("\n".join(out))
