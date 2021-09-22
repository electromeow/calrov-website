from flask import Flask, Response, request, render_template_string
import aiofiles
from pymongo import MongoClient
import json
from threading import Thread
from urllib.parse import quote
import os
from utils import *
from waitress import serve

app = Flask(__name__)

db_cred = {
    "user": os.environ["MONGO_USER"],
    "password": os.environ["MONGO_PASSWORD"],
    "host": os.environ["MONGO_HOST"],
    "database": os.environ["MONGO_DBNAME"]
}

mongo = MongoClient(f"mongodb+srv://{quote(db_cred['user'])}:{quote(db_cred['password'])}@{db_cred['host']}/{db_cred['database']}?retryWrites=true&w=majority")
db = mongo["calrovwebsite"]

@app.before_request
def before_request():
    if (not request.headers.get("user-agent").startswith("Mozilla/5.0")) or request.headers.get("user-agent").find("Trident") > -1:
        return "Görünüşe bakılırsa taş devrinden kalma bir tarayıcı veya Internet Explorer kullanıyorsunuz. \
Girdiğiniz sitelerin düzgün çalışması için lütfen modern bir tarayıcıya geçiş yapınız. \
Modern tarayıcıdan kastımız, Chromium tabanlı(Chromium, Chrome, Edge, Opera...) veya Firefox \
tabanlı(Firefox, LibreWolf, Tor...) bir tarayıcının veya Safari'nin son sürümlerinden birine geçiş yapmanızdır. \
Okuduğunuz için teşekkür ederiz..."



@app.route("/")
async def index():
    Thread(target=send_telemetry, args=(db, request.headers.get("user-agent"), request.remote_addr, "/")).start()
    async with aiofiles.open("./static/index.html", "r") as f:
        return await f.read()

@app.route("/sponsorluk")
async def sponsorluk():
    Thread(target=send_telemetry, args=(db, request.headers.get("user-agent"), request.remote_addr, "/sponsorluk")).start()
    async with aiofiles.open("./static/sponsorluk.html", "r") as f:
        return await f.read()

@app.route("/hakkimizda")
async def hakkimizda():
    Thread(target=send_telemetry,
           args=(db, request.headers.get("user-agent"), request.remote_addr, "/hakkimizda")).start()
    async with aiofiles.open("./static/hakkimizda.html", "r") as f:
        async with aiofiles.open("./uyeler.json", 'r') as uyelerjson:
            uyeler = json.loads(await uyelerjson.read())
        return render_template_string(await f.read(), uyeler=uyeler)

@app.route("/iletisim")
async def iletisim():
    Thread(target=send_telemetry, args=(db, request.headers.get("user-agent"), request.remote_addr, "/iletisim")).start()
    async with aiofiles.open("./static/iletisim.html", "r") as f:
        return await f.read()


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
    Thread(target=send_telemetry,
           args=(db, request.headers.get("user-agent"), request.remote_addr, request.path)).start()
    haber = db["haberler"].find_one({"_id": int(haber_id)})
    async with aiofiles.open("./static/haber.html") as f:
        skeleton = await f.read()
        return render_template_string(skeleton, json_obj=haber)

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
    Thread(target=send_telemetry,
           args=(db, request.headers.get("user-agent"), request.remote_addr, "/haberler")).start()
    async with aiofiles.open("./static/haberler.html", 'r') as f:
        pageno = None
        try:
            pageno = request.args.get("p")
        except ValueError:
            pass
        pageno = int(1 if pageno is None else pageno)
        haber_count = db["haberler"].estimated_document_count()
        haber_ids = list(filter(lambda i: i > 0, [
            i for i in range(haber_count - ((pageno-1)*5), haber_count-(pageno*5), -1)
        ]))
        haberler = list(db["haberler"].find({"_id": {
            "$in": haber_ids
        }}))
        firstpage = True if pageno == 1 else False
        lastpage = 1 in haber_ids
        haberler = sorted(haberler, key=lambda i: i["_id"], reverse=True)
        return render_template_string(await f.read(), haberler=haberler, firstpage=firstpage, lastpage=lastpage, pageno=pageno)


if __name__ == "__main__":
    serve(app, listen="*:8080")
