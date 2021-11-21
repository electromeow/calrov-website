from datetime import datetime, timedelta

MONTHS = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]


def timestamp_to_human_time(timestamp_integer):
    timestamp = datetime.utcfromtimestamp(timestamp_integer)
    timestamp = timestamp + timedelta(hours=3)
    return f"{timestamp.day} {MONTHS[timestamp.month]} {timestamp.year} {timestamp.hour+3}:{timestamp.minute if len(str(timestamp.minute)) > 1 else '0'+str(timestamp.minute)}"

DEPRECATED_BROWSER_WARNING = "Görünüşe bakılırsa taş devrinden kalma bir tarayıcı veya Internet Explorer kullanıyorsunuz. \
Girdiğiniz sitelerin düzgün çalışması için lütfen modern bir tarayıcıya geçiş yapınız. \
Modern tarayıcıdan kastımız, Chromium tabanlı(Chromium, Chrome, Edge, Opera...) veya Firefox \
tabanlı(Firefox, LibreWolf, Tor...) bir tarayıcının veya Safari'nin son sürümlerinden birine geçiş yapmanızdır. \
Okuduğunuz için teşekkür ederiz..."