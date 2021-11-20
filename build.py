import os
from sass import compile as sass
from htmlmin import minify as htmlmin
from jsmin import jsmin


try:
    os.mkdir("css")
except FileExistsError:
    pass
try:
    os.mkdir("html")
except FileExistsError:
    pass
try:
    os.mkdir("scripts")
except FileExistsError:
    pass

# Compile SASS files in sass/ folder to css/ folder with minimizing emabled
sass(dirname=("sass", "css"), output_style="compressed")

# Minimize HTML files in src/html/ folder into html/ folder.
for htmlfile in os.listdir("src/html"):
    with open("src/html/"+htmlfile, 'r') as f:
        content = f.read()
    with open("html/"+htmlfile, 'w') as f:
        f.write(htmlmin(content, remove_empty_space=True, remove_comments=True))

# Minimize JS files in src/scripts/ into scripts/
for jsfile in os.listdir("src/scripts"):
    with open("src/scripts/"+jsfile, 'r') as f:
        content = f.read()
    with open("scripts/"+jsfile, 'w') as f:
        f.write(jsmin(content, quote_chars="'\"`"))
