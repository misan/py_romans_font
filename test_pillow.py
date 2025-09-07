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
