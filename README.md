# Romans Vector Font Libraries

This project provides two simple, self-contained Python libraries for rendering text using a classic vector font. The font data is embedded directly in the Python files, so there are no external dependencies for the font itself. Font data was obtained from https://ncplot.com/stickfont/stickfont.htm and later massaged a bit with Gemini AI.

## Features

- **Two Font Styles**: 
    - `Romans`: A monospaced font with kerning adjustments for a clean, classic look.
    - `Romans2`: A proportionally spaced version for improved readability.
- **Easy Integration**: Simple API for use with any Python graphics library that supports drawing paths (e.g., Pillow, reportlab, Pygame).
- **Self-Contained**: No external font files needed.

## Project Files

- **`romans_font.py`**: The monospaced font library.
- **`romans2_font.py`**: The proportional font library.
- **`test_romans.py`**: An example script that generates `output.pdf` and `output2.pdf` to demonstrate the fonts.
- **`HOWTO.md`**: A detailed guide for developers.
- **`output.pdf` / `output2.pdf`**: Sample PDF files showing the two fonts.

## Getting Started

To use the fonts, simply place `romans_font.py` and/or `romans2_font.py` in your project directory.

Here is a minimal example of how to get the drawing paths for a string:

```python
from romans_font import Romans

# 1. Create a font object and set the scale
font = Romans()
font.scale = 1.0

# 2. Get the paths for a string
paths = font.get_string("Hello, World!")

# 3. Render the paths with your graphics library
# (Conceptual example)
# for path in paths:
#     graphics.draw_path(path)
```

## Usage Examples

### Rendering to a PDF with `reportlab`

This example uses the `Romans2` font to render text into a PDF file.

```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from romans2_font import Romans2

def draw_string(c, x, y, text, font):
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

c = canvas.Canvas("my_document.pdf", pagesize=letter)
font = Romans2()
font.scale = 1.0
draw_string(c, 50, 700, "Hello, PDF!", font)
c.save()
```

## visual_vector.py
`visual_vector.py` allows you to create a PDF of the nesting performed by the https://github.com/misan/packing2D project using the Bin-??.txt file output. 

## License

This project is licensed under the MIT License. See the `LICENSE.md` file for details.
