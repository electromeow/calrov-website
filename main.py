import asyncio
from flask import Flask, Response, request, render_template
import aiofiles
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote
import os
from utils import *
from waitress import serve

os.system("python3 build.py")

app = Flask(__name__, template_folder="./html")

db_cred = {
    "user": os.environ["MONGO_USER"],
    "password": os.environ["MONGO_PASSWORD"],
    "host": os.environ["MONGO_HOST"],
    "database": os.environ["MONGO_DBNAME"]
}

mongo = AsyncIOMotorClient(f"mongodb+srv://{quote(db_cred['user'])}:{quote(db_cred['password'])}@{db_cred['host']}/{db_cred['database']}?retryWrites=true&w=majority")
mongo.get_io_loop = asyncio.get_running_loop
db = mongo.get_default_database()

@app.before_request
def before_request():
    if (not request.headers.get("user-agent").startswith("Mozilla/5.0")) or request.headers.get("user-agent").find("Trident") > -1:
        return DEPRECATED_BROWSER_WARNING

@app.route("/")
async def index():
    return render_template("index.html")

@app.route("/sponsorluk")
async def sponsorluk():
    return render_template("sponsorluk.html")

@app.route("/hakkimizda")
async def hakkimizda():
    uyeler = await db["users"].find().to_list(9999999999999999999)
    uyeler = sorted(uyeler, key=lambda x: x["_id"])
    return render_template("hakkimizda.html", uyeler=uyeler)

@app.route("/iletisim")
async def iletisim():
    return render_template("iletisim.html")


@app.route("/css/<path:filename>")
async def css(filename):
    async with aiofiles.open(f"./css/{filename}", "r") as f:
        return Response(await f.read(), mimetype="text/css")

@app.route("/images/<path:filename>")
async def image(filename):
    async with aiofiles.open(f"./images/{filename}", "rb") as f:
        mime = None
        extension = filename.split(".")[-1]
        if extension == "jpg" or extension == "jpeg":
            mime = "image/jpeg"
        elif extension == "png":
            mime = "image/png"
        elif extension == "gif":
            mime = "image/gif"
        elif extension == "svg":
            mime = "image/svg+xml"
        return Response(await f.read(), mimetype=mime)

@app.route("/haberler/<path:haber_id>")
async def haber(haber_id):
    haber = await db["haberler"].find_one({"_id": int(haber_id)})
    return render_template("haber.html", json_obj=haber)

@app.route("/scripts/<path:filename>")
async def javascript(filename):
    async with aiofiles.open(f"./scripts/{filename}", "r") as f:
        return Response(await f.read(), mimetype="application/javascript")


@app.route("/fontawesome/<path:filename>")
async def fontawesome(filename):
    async with aiofiles.open(f"./fontawesome/{filename}", "rb") as f:
        mime = None
        if filename.endswith(".css"):
            mime = "text/css"
        elif filename.endswith(".woff"):
            mime = "font/woff"
        elif filename.endswith(".woff2"):
            mime = "font/woff2"
        elif filename.endswith(".ttf"):
            mime = "font/ttf"
        return Response(await f.read(), mimetype=mime)

@app.route("/favicon.ico")
async def favicon():
    async with aiofiles.open("favicon.ico", "rb") as f:
        return Response(await f.read(), mimetype="image/png")

@app.route("/haberler")
async def haberler():
    pageno = None
    try:
        pageno = request.args.get("p")
    except ValueError:
        pass
    pageno = int(1 if pageno is None else pageno)
    haber_count = await db["haberler"].count_documents({})
    haber_ids = list(filter(lambda i: i > 0, [
        i for i in range(haber_count - ((pageno-1)*5), haber_count-(pageno*5), -1)
    ]))
    haberler = await db["haberler"].find({"_id": {
        "$in": haber_ids
    }}).to_list(9999999999999999999)
    firstpage = True if pageno == 1 else False
    lastpage = 1 in haber_ids
    haberler = sorted(haberler, key=lambda i: i["_id"], reverse=True)
    return render_template("haberler.html", haberler=haberler, firstpage=firstpage, lastpage=lastpage, pageno=pageno)


@app.route("/blog")
async def blog():
    pageno = None
    try:
        pageno = request.args.get("p")
    except ValueError:
        pass
    pageno = int(1 if pageno is None else pageno)
    post_count = await db["blog"].count_documents({})
    post_ids = list(filter(lambda i: i > 0, [
        i for i in range(post_count - ((pageno-1)*5), post_count-(pageno*5), -1)
    ]))
    posts = await db["blog"].find({"_id": {
        "$in": post_ids
    }}).to_list(9999999999999999999)
    firstpage = True if pageno == 1 else False
    lastpage = 1 in post_ids
    haberler = sorted(posts, key=lambda i: i["timestamp"], reverse=True)
    return render_template("blog.html", posts=posts, firstpage=firstpage, lastpage=lastpage, pageno=pageno)


@app.route("/blog/<path:post_id>")
async def blog_post(post_id):
    post = await db["blog"].find_one({"_id": int(post_id)})
    author = await db["users"].find_one({"_id": int(post["author_id"])})
    publishtime = timestamp_to_human_time(post["timestamp"])
    return render_template("blogpost.html", json_obj=post, author=author, publishtime=publishtime)

@app.route("/uyeler/<path:uye_id>")
async def uye(uye_id):
    uye = await db["users"].find_one({"_id": int(uye_id)})
    return render_template("uye.html", uye=uye)


if __name__ == "__main__":
    # I created this try/except and if/else statements to make it work in prod. mode on Heroku and in dev. mode on my computer
    try:
        if os.environ["env_type"] == "prod":
            serve(app, listen="*:"+str(os.environ["PORT"]))
        else:
            app.run(port=8080)
    except:
        app.run(port=8080)



