try{
  window.fetch("/");
}
catch(e){
  document.body.innerHTML = "<h1>Görünüşe göre Internet Explorer veya başka bir eski kalmış tarayıcı kullanıyorsunuz.<br>Lütfen sadece bu site değil, kullanacağınız pek çok sitenin düzgün çalışması için modern bir tarayıcının(Firefox veya Chromium-tabanlı olan Chrome, Opera, Brave gibi bir tarayıcı tavsiye edilir) yeni sürümlerine geçiş yapınız.</h1>";
}