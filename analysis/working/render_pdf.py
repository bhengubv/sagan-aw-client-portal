import fitz
p = r"C:\Users\tbeng\Downloads\Technical_Spec_AW_Client_Report_Portal.pdf"
outdir = r"C:\Users\tbeng\Downloads\_aw_test_frames\specpages"
import os
os.makedirs(outdir, exist_ok=True)
d = fitz.open(p)
print("pages:", d.page_count)
for i, page in enumerate(d):
    pix = page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6))
    pix.save(os.path.join(outdir, f"p{i+1:02d}.png"))
print("rendered", d.page_count, "pages to", outdir)
