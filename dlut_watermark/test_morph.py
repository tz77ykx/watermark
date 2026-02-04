import fitz

doc = fitz.open()
page = doc.new_page()

try:
    mat = fitz.Matrix(45) # 45 degrees
    p = fitz.Point(100, 100)
    # Note: morph=(p, mat)
    page.insert_text(p, "Morph Opacity Test", fontsize=40, color=(0,0,0), morph=(p, mat), fill_opacity=0.5)
    print("Success: insert_text supports morph and fill_opacity")
except Exception as e:
    print(f"Failed: {e}")

doc.save("test_morph.pdf")
