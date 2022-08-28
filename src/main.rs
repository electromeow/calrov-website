#[macro_use] extern crate rocket;
mod structs;
mod utils;
use std::sync::Mutex;
use std::path::{PathBuf, Path};
use rocket::State;
use rocket::http::ContentType;
use tera::{Tera,Context};
use mongodb::Client;
use mongodb::bson::doc;
use structs::Sponsor;

async fn static_file(path: PathBuf) -> (ContentType, Vec<u8>) {
    let extension = match path.extension() {
        Some(ext) => ext.to_str().unwrap(),
        None => ""
    };
    let extension = extension.to_lowercase();
    let content_type = match ContentType::from_extension(extension.as_str()) {
        Some(t) => t,
        None => ContentType::Any
    };
    (content_type, rocket::tokio::fs::read(path).await.unwrap())
}

#[get("/")]
fn index(templating: &State<Mutex<Tera>>) -> (ContentType, String) {
    let template_engine = templating.inner().lock().unwrap();
    match template_engine.render("index.html", &Context::new()) {
        Ok(s) => (ContentType::HTML, s),
        Err(e) => panic!("{:?}", e)
    }
}

#[get("/css/<filename>")]
async fn css(filename: &str) -> (ContentType, Vec<u8>) {
    static_file(Path::new("css/").join(filename)).await
}

#[get("/fontawesome/<filename>")]
async fn fa(filename: &str) -> (ContentType, Vec<u8>) {
    static_file(Path::new("fontawesome/").join(filename)).await
}

#[get("/iletisim")]
fn iletisim(templating: &State<Mutex<Tera>>) -> (ContentType, String) {
    let template_engine = templating.inner().lock().unwrap();
    (ContentType::HTML, template_engine.render("iletisim.html", &Context::new()).unwrap())
}

#[get("/sponsorluk")]
async fn sponsorluk(templating: &State<Mutex<Tera>>, db: &State<mongodb::Database>) -> (ContentType, String) {
    let mut cursor = db.collection::<Sponsor>("sponsors").find(doc!{}, None).await.unwrap();
    let (years, sponsors) = utils::group_sponsors(
        utils::cursor_collect(&mut cursor)
            .await.unwrap()
    );
    let mut cx = Context::new();
    cx.insert("years", &years);
    cx.insert("sponsors", &sponsors);
    let template_engine = templating.inner().lock().unwrap();
    (ContentType::HTML, template_engine.render("sponsorluk.html", &cx).unwrap())
}


#[get("/haberler?<p>")]
async fn haberler(templating: &State<Mutex<Tera>>, db: &State<mongodb::Database>, p: Option<u8>) -> (ContentType, String){
    let page = match p {
        Some(s) => {
            if s==0 {
                1
            }
            else {
                s as i32
            }
        },
        None => 1 as i32
    };
    let count = db.collection::<structs::Haber>("haberler").count_documents(None, None).await.unwrap() as i32;
    let ids_list = utils::get_page_range(5, count, page);
    let mut cursor = db.collection::<structs::Haber>("haberler").find(doc!{"_id": {"$in": ids_list}}, None).await.unwrap();
    let is_last_page: bool;
    let mut haberler = utils::cursor_collect(&mut cursor).await.unwrap();
    haberler.reverse();
    if (haberler.last().unwrap())._id == (1 as u32) {
        is_last_page = true
    } else {
        is_last_page = false;
    }
    let template_engine = templating.inner().lock().unwrap();
    let mut cx = Context::new();
    cx.insert("haberler", &haberler);
    cx.insert("page", &page);
    cx.insert("is_last_page", &is_last_page);
    (
        ContentType::HTML,
        template_engine.render("haberler.html", &cx).unwrap()
    )
}

#[get("/haberler/<filename>")]
async fn haber(templating: &State<Mutex<Tera>>, db: &State<mongodb::Database>, filename: &str) -> (ContentType, String) {
    let mut full_link = String::from("/haberler/");
    full_link.push_str(filename);
    let result = db.collection::<structs::Haber>("haberler").find_one(doc!{"link": full_link}, None).await.unwrap();
    let (content, title, date) = match result {
        Some(haber) => (
            haber.content,
            haber.title,
            match haber.date {
                Some(d) => utils::date_to_human_date(d),
                None => String::new()
            }
        ),
        None => (
            String::from("Aradığınız haber sitede bulunmuyor ya da haber taşındı!"),
            String::from("Haber Bulunamadı"),
            String::new()
        )
    };
    let mut cx = Context::new();
    cx.insert("content", &content);
    cx.insert("date", &date);
    cx.insert("title", &title);
    let template_engine = templating.inner().lock().unwrap();
    (ContentType::HTML, template_engine.render("haber.html", &cx).unwrap())
}

#[get("/hakkimizda")]
async fn hakkimizda(templating: &State<Mutex<Tera>>, db: &State<mongodb::Database>) -> (ContentType, String) {
    let mut cursor = db.collection::<structs::Member>("users").find(doc!{}, None).await.unwrap();
    let mut members = utils::cursor_collect(&mut cursor).await.unwrap();
    members.sort_by_key(|x| x._id);
    let mut cx = Context::new();
    cx.insert("members", &members);
    let template_engine = templating.inner().lock().unwrap();
    (ContentType::HTML, template_engine.render("hakkimizda.html", &cx).unwrap())
}

#[get("/uyeler/<id>")]
async fn member_info(templating: &State<Mutex<Tera>>, db: &State<mongodb::Database>, id: u8) -> (ContentType, String) {
    let member = db.collection::<structs::Member>("users")
        .find_one(doc!{"_id": (id as i32)}, None)
        .await
        .unwrap()
        .unwrap();
    let mut cx = Context::new();
    cx.insert("member", &member);
    let template_engine = templating.inner().lock().unwrap();
    (ContentType::HTML, template_engine.render("uye.html", &cx).unwrap())
}

#[get("/images/<filename>")]
async fn img(filename: &str) -> (ContentType, Vec<u8>) {
    static_file(Path::new("images/").join(filename)).await
}
#[get("/favicon.ico")]
async fn favicon() -> (ContentType, Vec<u8>) {
    static_file(PathBuf::new("favicon.ico")).await
}
#[launch]
async fn rocket() -> _ {
    let templating = Tera::new("templates/**/*.html").unwrap_or_else(|e| {
        eprintln!("Can't create Tera instance: {}", e);
        std::process::exit(1);
    });
    let mongo_uri = std::env::var("MONGO_URI").unwrap_or_else(|_e| {
        eprintln!("MONGO_URI environment variable not defined or isn't accessible!");
        std::process::exit(1);
    });
    let mongo_client = Client::with_uri_str(mongo_uri).await.unwrap_or_else(|e| {
        eprintln!("Can't connect to DB: {:?}", e);
        std::process::exit(1);
    });
    let db = mongo_client.database("calrovwebsite");
    rocket::build()
        .manage(Mutex::new(templating))
        .manage(db)
        .mount("/", routes![index,css,fa, img, iletisim,sponsorluk,hakkimizda,haberler, member_info, haber, favicon])
}
