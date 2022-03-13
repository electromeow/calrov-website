const adminContent = document.querySelector("div#admin-content");
function loadMenu() {
  adminContent.innerHTML = " ";
  fetch("/admin/menu", { headers: { Authorization: localStorage.getItem("calrovAdminAuthHeader") } })
    .then((res) => res.text())
    .then((res) => {
      adminContent.innerHTML = res;
    });
}
function logout() {
  localStorage.removeItem("calrovAdminAuthHeader");
  loadLogin();
  alert("Başarıyla Çıkış Yapıldı!");
}
function loadHaberEditor(haberid) {
  adminContent.innerHTML = " ";
  fetch("/admin/haberDuzenle/" + haberid, { headers: { Authorization: localStorage.getItem("calrovAdminAuthHeader") } })
    .then((res) => res.text())
    .then((res) => (adminContent.innerHTML = res));
}
function createHaber() {
  fetch("/api/haberler", {
    method: "POST",
    headers: { Authorization: localStorage.getItem("calrovAdminAuthHeader") },
    body: JSON.stringify({
      title: "Yeni Haber",
      thumbnail: "/images/calrovlogo.png",
      content: "Bu sayfa hazırlanma aşamasındadır.",
      summary: "Bu sayfa hazırlanma aşamasındadır.",
    }),
  }).then((res) => {
    if (res.status == 200) {
      loadHaberler();
      alert("Haber Oluşturuldu.");
    } else {
      loadLogin();
      alert("Benim yetkim yok hojam! En iyisi tekrar giriş yapim.");
    }
  });
}
function editHaber(haberid) {
  const title = document.querySelector("input#haber-title").value;
  const summary = document.querySelector("input#haber-summary").value;
  const content = document.querySelector("textarea#haber-content").value;
  const thumbnail = document.querySelector("input#haber-thumbnail").value;
  const reqBody = {
    title: title,
    summary: summary,
    content: content,
    thumbnail: thumbnail,
  };
  fetch("/api/haberler/" + haberid, {
    method: "PUT",
    headers: { Authorization: localStorage.getItem("calrovAdminAuthHeader") },
    body: JSON.stringify(reqBody),
  }).then((res) => {
    if (res.status == 200) {
      loadHaberler();
      alert("Haber başarıyla düzenlendi!");
    } else {
      loadLogin();
      alert("Benim yetkim yok hojam! En iyisi tekrar giriş yapim.");
    }
  });
}
function deleteHaber(haberid) {
  if (confirm("Haberi silmek istediğine emin misin? Bak geri dönüşü olmaz sonra...")) {
    fetch("/api/haberler/" + haberid, { method: "DELETE", headers: { Authorization: localStorage.getItem("calrovAdminAuthHeader") } }).then((res) => {
      if (res.status == 200) {
        loadHaberler();
        alert("Haber Başarıyla Silindi!");
      } else {
        loadLogin();
        alert("Benim yetkim yok hojam! En iyisi tekrar giriş yapim.");
      }
    });
  }
}
function loadHaberler() {
  adminContent.innerHTML = " ";
  fetch("/admin/haberler", { headers: { Authorization: localStorage.getItem("calrovAdminAuthHeader") } })
    .then((res) => res.text())
    .then((res) => (adminContent.innerHTML = res));
}
function loginsubmit() {
  let userid = document.querySelector("section form input#idinput").value;
  let password = document.querySelector("section form input#passwordinput").value;
  let authHeader = btoa(userid) + " " + btoa(password);
  fetch("/api/login", { headers: { Authorization: authHeader } }).then((res) => {
    if (res.status == 200) {
      localStorage.setItem("calrovAdminAuthHeader", authHeader);
      loadMenu();
    } else if (res.status == 403) {
      document.querySelector("section div#loginerror").style.display = "inline-block";
    }
  });
  return false;
}
function loadBlog() {
  fetch("/admin/blog", {
    headers: {
      "Authorization": localStorage.getItem("calrovAdminAuthHeader")
    }
  })
    .then(res => res.text())
    .then(res => {
      adminContent.innerHTML = res;
    });
}
function loadBlogPostEditor(postid){
  fetch("/admin/blogDuzenle/"+postid, {
    headers: {
      "Authorization":localStorage.getItem("calrovAdminAuthHeader")
    }
  }).then(res => res.text()).then(res => {
    adminContent.innerHTML = res;
  });

}
function editBlogPost(postid){
  const title = document.querySelector("input#blog-title").value;
  const summary = document.querySelector("input#blog-summary").value;
  const content = document.querySelector("textarea#blog-content").value;
  const thumbnail = document.querySelector("input#blog-thumbnail").value;
  const reqBody = {
    title: title,
    summary: summary,
    content: content,
    thumbnail: thumbnail,
  };
  fetch("/api/blog/" + postid, {
    method: "PUT",
    headers: { "Authorization": localStorage.getItem("calrovAdminAuthHeader") },
    body: JSON.stringify(reqBody),
  }).then((res) => {
    if (res.status == 200) {
      loadBlog();
      alert("Makale başarıyla düzenlendi!");
    } else {
      loadLogin();
      alert("Benim yetkim yok hojam! En iyisi tekrar giriş yapim.");
    }
  });
}
function deleteBlogPost(postid){
  if(confirm("Makaleyi silmek istediğine emin misin? Bak geri dönüşü olmaz sonra...")) {
    fetch("/api/blog/" + postid, {
      method: "DELETE",
      headers: {
        "Authorization": localStorage.getItem("calrovAdminAuthHeader")
      }
    }).then(res => {
      if (res.status == 200) {
        loadBlog();
        alert("Makale Başarıyla Silindi!");
      } else {
        loadLogin();
        alert("Benim yetkim yok hojam! En iyisi tekrar giriş yapim.");
      }
    });
  }
}
function createBlogPost(){
  fetch("/api/blog", {
    method: "POST",
    headers: {
      "Authorization": localStorage.getItem("calrovAdminAuthHeader")
    },
    body: JSON.stringify({
      "title": "Yeni Makale",
      "summary": "Bu makale düzenlenme aşamasındadır.",
      "content": "Bu makale düzenlenme aşamasındadır.",
      "thumbnail": "/images/calrovlogo.png"
    })
  }).then(res => {
    if(res.status==200){
      loadBlog();
      alert("Makale Başarıyla Oluşturuldu!");
    }
    else {
      loadLogin();
      alert("Benim yetkim yok hojam! En iyisi tekrar giriş yapim.");
    }
  });
}
function loadLogin() {
  fetch("/admin/login")
    .then((res) => res.text())
    .then((res) => (adminContent.innerHTML = res));
}

