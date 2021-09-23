import os
from sass import compile as sass
from htmlmin import minify as htmlmin
from jsmin import jsmin

try:
    os.mkdir("css")
except FileExistsError:
    pass
try:
    os.mkdir("static")
except FileExistsError:
    pass
try:
    os.mkdir("scripts")
except FileExistsError:
    pass

sass(dirname=("sass", "css"), output_style="compressed")

for htmlfile in os.listdir("src/static"):
    with open("src/static/"+htmlfile, 'r') as f:
        content = f.read()
    with open("static/"+htmlfile, 'w') as f:
        f.write(htmlmin(content, remove_empty_space=True, remove_comments=True))


for jsfile in os.listdir("scripts"):
    with open("src/scripts/"+jsfile, 'r') as f:
        content = f.read()
    with open("scripts/"+jsfile, 'w') as f:
        f.write(jsmin(content, quote_chars="'\"`"))