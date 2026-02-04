import fitz

doc = fitz.open()
page = doc.new_page()

try:
    page.insert_text((100, 100), "Opacity Test with Rotate", fontsize=40, color=(0,0,0), rotate=45, fill_opacity=0.5)
    print("Success: insert_text supports fill_opacity and rotate")
except Exception as e:
    print(f"Failed: {e}")

doc.save("test_op_rot.pdf")
