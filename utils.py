from datetime import datetime, timedelta

MONTHS = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]


def timestamp_to_human_time(timestamp_integer):
    timestamp = datetime.fromtimestamp(timestamp_integer)
    timestamp = timestamp + timedelta(hours=3)
    return f"{timestamp.date} {MONTHS[timestamp.month]} {timestamp.year} {timestamp.hour}:{timestamp.minute}"

def send_telemetry(db, useragent, ip, path):
    db["telemetry"].insert_one({"ip": ip, "useragent": useragent, "path": path})
    pass

def create_haber_card(json_obj):
    return f"""
<div class="haber">
<a href="/haberler/{json_obj["_id"]}">
<img src="{json_obj["thumbnail"]}" alt="haber küçük resim">
<div>
<h1>{json_obj["title"]}</h1>
<p>{json_obj["summary"]}</p>
</div>
</a>
</div>
"""
