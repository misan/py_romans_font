# How to Use the Romans Font Libraries

## Introduction

This project provides two simple, self-contained Python libraries for rendering text using a classic vector font. The font data is embedded directly in the Python files, so there are no external dependencies for the font itself.

- **`romans_font.py`**: Provides the `Romans` class, a monospaced vector font with kerning adjustments for a clean, classic look.
- **`romans2_font.py`**: Provides the `Romans2` class, a proportionally spaced version of the same font, ideal for body text and numbers where variable character widths improve readability.

These libraries can be integrated with any Python graphics library that supports drawing paths or polygons, such as `reportlab`, `Pygame`, `Pillow`, or `PyCairo`.

## Features

- **Two Font Styles**: Choose between a monospaced (`Romans`) or proportional (`Romans2`) font.
- **Easy Integration**: Simple API makes it easy to use with any graphics library.
- **Self-Contained**: No external font files are needed.

## Installation

To use the fonts, simply place `romans_font.py` and/or `romans2_font.py` in your project directory and import the `Romans` or `Romans2` class.

## Use Case 1: Basic Text Rendering

Here is a basic example of how to get the drawing paths for a string. You can then use these paths to render the text with your graphics library of choice.

```python
from romans_font import Romans

# 1. Create a font object
font = Romans()

# 2. Set the desired size (scale)
font.scale = 1.0

# 3. Get the paths for a string
text_to_render = "Hello, World!"
paths = font.get_string(text_to_render)

# paths is a list of lists of (x, y) tuples.
# Each inner list represents a continuous line to be drawn.

# 4. Render the paths with your graphics library
# (This is a conceptual example)
# graphics_library.set_color("black")
# for path in paths:
#     graphics_library.draw_path(path)
```

## Use Case 2: Integration with `reportlab` to Create a PDF

This example shows how to use the `Romans2` font to render text and save it as a PDF file using the `reportlab` library.

```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from romans2_font import Romans2

def draw_string(c, x, y, text, font):
    """Draws a string with the vector font on a reportlab canvas."""
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

# Create a new PDF document
c = canvas.Canvas("my_document.pdf", pagesize=letter)

# Create a Romans2 font object
font = Romans2()
font.scale = 1.0

# Draw some text
draw_string(c, 50, 700, "This is a test with the proportional Romans2 font.", font)

# Save the PDF
c.save()
```

## Use Case 3: Rendering to an Image with Pillow

This example shows how to use the `Romans` font to render text onto a PNG image using the Pillow library.

```python
    from PIL import Image, ImageDraw
    from romans_font import Romans

    # 1. Set up the image and drawing context
    width, height = 400, 100
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # 2. Create a font object and set its properties
    font = Romans()
    font.scale = 1.5
    text_to_render = "Hello, Pillow!"

    # 3. Get the paths from the font library
    paths = font.get_string(text_to_render)

    # 4. Define position and color
    x_pos = 20
    baseline_y = 60
    fill_color = "black"

    # 5. Draw the paths on the image
    for path in paths:
        # The path needs to be translated to the correct position and the y-axis flipped
        translated_path = [(p[0] + x_pos, baseline_y - p[1]) for p in path]
        draw.line(translated_path, fill=fill_color, width=1)

    # 6. Save the image
    image.save("hello_pillow.png")
```

## API Overview

- `__init__()`: Creates a new font object.
- `get_string(line)`: Takes a string and returns a list of paths. Each path is a list of `(x, y)` tuples.
- `get_string_length(line)`: Returns the total width of a string in the font's internal units.
- `scale`: A property to set the size of the font. It's a multiplier for the internal units.
