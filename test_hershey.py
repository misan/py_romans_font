from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from HersheySans1 import HersheySans1

def draw_string(c, x, y, text, font):
    """Draws a string with the vector font."""
    paths = font.get_string(text)
    c.saveState()
    c.translate(x, y)
    for path in paths:
        p = c.beginPath()
        p.moveTo(path[0][0], path[0][1])
        for point in path[1:]:
            p.lineTo(point[0], point[1])
        c.drawPath(p, stroke=1, fill=0)
    c.restoreState()

def wrap_and_draw(c, x, y, text, font, line_height, max_width, bottom_margin, top_y):
    """Wraps text and draws it, handling page breaks."""
    y_cursor = y
    words = text.split(' ')
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if font.get_string_length(test_line) > max_width:
            if y_cursor < bottom_margin:
                c.showPage()
                c.setFont("Helvetica-Bold", 12) # Re-set font on new page
                y_cursor = top_y
            draw_string(c, x, y_cursor, current_line, font)
            y_cursor -= line_height
            current_line = word
        else:
            current_line = test_line
            
    if current_line:
        if y_cursor < bottom_margin:
            c.showPage()
            c.setFont("Helvetica-Bold", 12) # Re-set font on new page
            y_cursor = top_y
        draw_string(c, x, y_cursor, current_line, font)
        y_cursor -= line_height
    return y_cursor

def generate_pdf(filename, font_class, font_name):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    font = font_class()
    font_size = 0.8
    font.scale = font_size

    text1 = "This is a sample paragraph rendered using the Romans vector font. It demonstrates the ability to draw text from a custom font definition within a PDF document. The Quick Brown Fox Jumps over a Lazy Dog."
    text2 = ", ".join(map(str, range(1, 201)))

    x = 50
    top_y = height - 100
    bottom_margin = 50
    line_height = 24 * font_size * 1.5
    max_width = width - 2 * x

    # --- Draw the first paragraph ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, top_y + line_height, f"Paragraph 1 ({font_name}):")
    y_cursor = wrap_and_draw(c, x, top_y, text1, font, line_height, max_width, bottom_margin, top_y)

    y_cursor -= line_height
    if y_cursor < bottom_margin:
        c.showPage()
        c.setFont("Helvetica-Bold", 12)
        y_cursor = top_y

    # --- Draw the second paragraph ---
    c.drawString(x, y_cursor + line_height, f"Paragraph 2 ({font_name}):")
    wrap_and_draw(c, x, y_cursor, text2, font, line_height, max_width, bottom_margin, top_y)

    c.save()
    print(f"Successfully created {filename}")

def main():
    generate_pdf("output3.pdf", HersheySans1, "HersheySans1 - Vector Font")

if __name__ == "__main__":
    main()