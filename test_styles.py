import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from romans2_font import Romans2

class RomansPreview(Romans2):
    def get_string(self, line, bold=False, italic=False):
        x = 0
        out = []
        
        italic_shear = 0.3

        for char in line:
            c = ord(char)
            ch = self.get_char(c)
            if ch:
                processed_ch = ch
                if italic:
                    sheared_ch = []
                    for path in processed_ch:
                        new_path = [(p[0] + italic_shear * p[1], p[1]) for p in path]
                        sheared_ch.append(new_path)
                    processed_ch = sheared_ch

                for path in processed_ch:
                    new_path = [(p[0] * self.scale + x, p[1] * self.scale) for p in path]
                    out.append(new_path)
                    
                    if bold:
                        bold_offset = 0.5 * self.scale
                        bold_path = [(p[0] + bold_offset, p[1]) for p in new_path]
                        out.append(bold_path)

            x += self.get_length(c)
        return out

def draw_string(c, x, y, text, font, bold=False, italic=False):
    paths = font.get_string(text, bold=bold, italic=italic)
    c.saveState()
    c.translate(x, y)
    for path in paths:
        p = c.beginPath()
        p.moveTo(path[0][0], path[0][1])
        for point in path[1:]:
            p.lineTo(point[0], point[1])
        c.drawPath(p, stroke=1, fill=0)
    c.restoreState()

def main():
    c = canvas.Canvas("styles_preview.pdf", pagesize=letter)
    width, height = letter

    font = RomansPreview()
    font_size = 1.5
    font.scale = font_size

    x = 50
    y = height - 100
    line_height = 24 * font_size * 1.5

    c.setFont("Helvetica-Bold", 16)
    c.drawString(x, y + line_height, "Font Style Preview")

    y -= line_height
    c.setFont("Helvetica", 12)
    c.drawString(x, y, "Regular:")
    draw_string(c, x + 100, y, "Hello, World! 123", font)

    y -= line_height
    c.drawString(x, y, "Italic:")
    draw_string(c, x + 100, y, "Hello, World! 123", font, italic=True)

    y -= line_height
    c.drawString(x, y, "Bold:")
    draw_string(c, x + 100, y, "Hello, World! 123", font, bold=True)

    y -= line_height
    c.drawString(x, y, "Bold Italic:")
    draw_string(c, x + 100, y, "Hello, World! 123", font, bold=True, italic=True)

    c.save()
    print("Successfully created styles_preview.pdf")

if __name__ == "__main__":
    main()
