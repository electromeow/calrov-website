import asyncio
import smtplib
import ssl
import html
import json
from flask import Flask, Response, request, render_template, redirect
import aiofiles
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote
import os
from utils import *
from waitress import serve
from datetime import datetime as dt

os.system("python3 build.py")

app = Flask(__name__, template_folder="./html")

db_cred = {
    "user": os.environ["MONGO_USER"],
    "password": os.environ["MONGO_PASSWORD"],
    "host": os.environ["MONGO_HOST"],
    "database": os.environ["MONGO_DBNAME"]
}

mongo = AsyncIOMotorClient(
    f"mongodb://{quote(db_cred['user'])}:{quote(db_cred['password'])}@{db_cred['host']}/{db_cred['database']}?tlsAllowInvalidCertificates=true&tls=true&retryWrites=true&w=majority")
mongo.get_io_loop = asyncio.get_running_loop
db = mongo.get_default_database()

mailer_ctx = ssl.create_default_context()

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
    uyeler = await db["users"].find({}).to_list(9999999999999999999)
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
    posts = sorted(posts, key=lambda i: i["timestamp"], reverse=True)
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


@app.route("/api/haberler/<path:haber_id>", methods=["GET", "PUT", "DELETE"])
async def api_haberler_by_id(haber_id):
    if request.method == "GET":
        return await db["haberler"].find_one({"_id": int(haber_id)})
    elif request.method == "PUT":
        if await check_user(request.headers.get("authorization"), db):
            haber = json.loads(request.data)
            if haber.get("summary") is None or haber.get("thumbnail") is None or haber.get("title") is None or haber.get("content") is None:
                return Response("One or more of fields thumbnail, summary, title, or content do not exist.", status=400)
            haber["link"] = "/haberler/"+haber_id
            haber["_id"] = int(haber_id)
            await db["haberler"].replace_one({"_id": int(haber_id)}, haber)
            return Response(status=200)
        else:
            return Response(status=401)
    elif request.method == "DELETE":
        if await check_user(request.headers.get("authorization"), db):
            await db["haberler"].delete_one({"_id": int(haber_id)})
            return Response(status=200)
        else:
            return Response(status=401)


@app.route("/api/haberler", methods=["POST"])
async def api_haberler_post():
    if await check_user(request.headers.get("authorization"), db):
        haber = json.loads(request.data)
        if haber.get("summary") is None or haber.get("thumbnail") is None or haber.get("title") is None or haber.get("content") is None:
            return Response("One or more of fields thumbnail, summary, title or content do not exist.", status=400)
        haber["_id"] = await db["haberler"].count_documents({})+1
        haber["link"] = "./haberler/"+str(haber["_id"])
        await db["haberler"].insert_one(haber)
        return Response(status=200)
    else:
        return Response(status=401)


@app.route("/api/blog/<path:post_id>", methods=["GET", "PUT", "DELETE"])
async def api_blog_by_id(post_id):
    if request.method == "GET":
        post_obj = dict(await db["blog"].find_one({"_id": int(post_id)}))
        author_id = post_obj.pop("author_id")
        post_obj["author"] = await db["users"].find_one({"_id": author_id})
        return post_obj
    elif request.method == "PUT":
        if await check_user(request.headers.get("authorization"), db):
            post_obj = json.loads(request.data)
            if post_obj.get("title") is None or post_obj.get("content") is None or post_obj.get("thumbnail") is None or post_obj.get("summary") is None:
                return Response("One or more of the fields content, thumbnail, summary or title do not exist.", status=400)
            post_obj["author_id"] = int(codecs.decode(request.headers.get("authorization").split(" ")[0].encode("utf-8"), "base64").decode("utf-8"))
            post_obj["_id"] = int(post_id)
            post_obj["timestamp"] = (await db["blog"].find_one({"_id": int(post_id)}))["timestamp"]
            await db["blog"].replace_one({"_id": int(post_id)}, post_obj)
            return Response(status=200)
        else:
            return Response(status=401)
    elif request.method == "DELETE":
        if await check_user(request.headers.get("authorization"), db):
            await db["blog"].delete_one({"_id": int(post_id)})
            return Response(status=200)
        else:
            return Response(status=401)


@app.route("/api/blog", methods=["POST"])
async def api_blog_post():
    if await check_user(request.headers.get("authorization"), db):
        post_obj = json.loads(request.data)
        if post_obj.get("thumbnail") is None or post_obj.get("title") is None or post_obj.get("summary") is None or post_obj.get("content") is None:
            return Response(status=400)
        else:
            post_obj["author_id"] = int(codecs.decode(request.headers.get("authorization").split(" ")[0].encode("utf-8"), "base64").decode("utf-8"))
            post_obj["_id"] = await db["blog"].count_documents({})+1
            post_obj["timestamp"] = dt.utcnow().timestamp()
            await db["blog"].insert_one(post_obj)
            return Response(status=200)
    else:
        return Response(status=401)

@app.route("/api/login", methods=["GET"])
async def api_login():
    if await check_user(request.headers.get("authorization"), db):
        return Response(status=200)
    else:
        return Response(status=403)

@app.route("/admin")
async def admin_index():
    return render_template("admin/index.html")

@app.route("/admin/login")
async def admin_login():
    return render_template("admin/login.html")

@app.route("/admin/menu")
async def admin_menu():
    if await check_user(request.headers.get("authorization"), db):
        return render_template("admin/menu.html")
    else:
        return Response(status=401)

@app.route("/admin/haberler")
async def admin_haberler():
    if await check_user(request.headers.get("authorization"), db):
        haberler = await db["haberler"].find({}).to_list(9999999999999999999)
        haberler = sorted(haberler, key=lambda i: i["_id"], reverse=True)
        return render_template("admin/haberler.html", haberler=haberler)
    else:
        return Response(status=401)

@app.route("/admin/haberDuzenle/<path:haber_id>")
async def admin_haber_editor(haber_id):
    if await check_user(request.headers.get("authorization"), db):
        haber = await db["haberler"].find_one({"_id": int(haber_id)})
        return render_template("admin/habereditor.html", haber=haber)

@app.route("/admin/blog")
async def admin_blog():
    if await check_user(request.headers.get("authorization"), db):
        blog_posts = await db["blog"].find({}).to_list(9999999999999999999)
        blog_posts = sorted(blog_posts, key=lambda i: i["timestamp"], reverse=True)
        return render_template("admin/blog.html", posts=blog_posts)

@app.route("/admin/blogDuzenle/<path:post_id>")
async def admin_blog_editor(post_id):
    if await check_user(request.headers.get("authorization"), db):
        blog_post = await db["blog"].find_one({"_id":int(post_id)})
        return render_template("admin/blogposteditor.html", post=blog_post)

@app.route("/urunler")
async def urunler_index():
    urunler = await db["urunler"].find({}).to_list(9999999999999999999)
    return render_template("urunler/index.html", urunler=urunler)

@app.route("/urunler/<path:urun_id>")
async def urun_bilgi(urun_id):
    urun = await db["urunler"].find_one({"_id": int(urun_id)})
    return render_template("urunler/urun_bilgi.html", urun=urun)

@app.route("/api/createCart", methods=["POST"])
async def createCart():
    incoming_data = json.loads(request.data)
    urunler = await db["urunler"].find({"_id": { "$in": list(map(lambda i: int(i), incoming_data.keys())) } }).to_list(9999999999999999999)
    toplam_fiyat = 0
    for i in urunler:
        i["quantity"] = incoming_data[str(i["_id"])]
        toplam_fiyat += float(i["price"]) * int(i["quantity"])
    return render_template("urunler/sepet.html", urunler=urunler, toplam_fiyat=toplam_fiyat)

@app.route("/api/siparisVer", methods=["POST"])
async def siparis():
    order_data = json.loads(request.data)
    print(order_data)
    order_email = f"""From: CALROV <siparisler@calrovteam.com>\nTo: CALROV <siparisler@calrovteam.com>\nSubject: Sipariş Alındı!\n

Bir Sipariş Alındı!

Bilgiler
Ad Soyad: {html.escape(order_data["ad-soyad-calrov"])}
E-Posta: {html.escape(order_data["e-mail-calrov"])}
Telefon: {html.escape(order_data["telefon-calrov"])}
Şehir: {html.escape(order_data["sehir-calrov"])}
İletişim Tercihi: {"Telefonla Arama" if order_data["iletisim-tercih"]=="telefon"
    else ("WhatsApp" if order_data["iletisim-tercih"]=="wp"
          else ("E-Posta" if order_data["iletisim-tercih"]=="email"
                else "?"))}

Sipariş Edilen Ürünler
"""
    urunler = await db["urunler"].find({"_id": {
        "$in": list(map(lambda i: int(i), order_data["cart"].keys()))
    }}).to_list(9999999999999999999)
    toplam_fiyat = 0
    for i in urunler:
        i["quantity"] = order_data["cart"][str(i["_id"])]
        toplam_fiyat += int(i["quantity"]) * float(i["price"])
        order_email += f"""
{i["quantity"]} Adet "{i["name"]}"
"""
    order_email +=f"\nToplam Fiyat: {toplam_fiyat}₺"
    order_email_for_customer = f"""From: CALROV <siparisler@calrovteam.com>\nTo: {html.escape(order_data["ad-soyad-calrov"])} <{html.escape(order_data["e-mail-calrov"])}>\nMIME-Version: 1.0\nSubject: Siparişiniz Alındı!\nContent-Type: text/html\n
<div style="font-family: Helvetica, Arial, sans-serif;">
<p>Sayın {html.escape(order_data["ad-soyad-calrov"])},</p>
<p>Web sitemiz üzerinden vermiş olduğunuz sipariş elimize başarılı olarak ulaşmıştır.<br/>
Siparişinizle ilgili gerekli iletişim en yakın zamanda tarafınızla tercih etmiş olduğunuz iletişim yoluyla({"Telefonla Arama" if order_data["iletisim-tercih"]=="telefon"
    else ("WhatsApp" if order_data["iletisim-tercih"]=="wp"
          else ("E-Posta" if order_data["iletisim-tercih"]=="email"
                else "?"))}) sağlanacaktır.<p>
<h3>Sipariş Edilen Ürünler:</h3>
<ul>
  {"".join(["<li>"+i["name"]+" ("+i["quantity"]+" adet)</li>" for i in urunler])}
</ul>
<h3>Toplam Ürün Fiyatı: {toplam_fiyat}₺</h3>
<p>Bizi tercih ettiğiniz için teşekkürler.<br />
İyi Günler Dileriz.</p>
<p>CALROV Ekibi</p>
</div>
"""
    with smtplib.SMTP_SSL(host="smtp.yandex.com", port=465, context=mailer_ctx) as mailserver:
        mailserver.login("siparisler@calrovteam.com", os.environ["EMAIL_PASSWORD"])
        mailserver.sendmail("siparisler@calrovteam.com", "siparisler@calrovteam.com", order_email.encode("utf-8"))
        mailserver.sendmail("siparisler@calrovteam.com", order_data["e-mail-calrov"], order_email_for_customer.encode("utf-8"))
    return Response(status=200)

@app.route("/sepet")
async def sepet():
    return render_template("urunler/sepet-body.html")

if __name__ == "__main__":
    # I created this try/except and if/else statements to make it work in prod. mode on Heroku and in dev. mode on my computer
    try:
        if os.environ["env_type"] == "prod":
            serve(app, listen="*:"+str(os.environ["PORT"]))
        else:
            app.run(port=8080)
    except:
        app.run(port=8080)
