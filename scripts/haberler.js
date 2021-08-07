const urlParams = new URLSearchParams(window.location.search);
let p;
if (!urlParams.get("p")) {
  p = 1;
} else {
  p = urlParams.get("p");
}
const firstpage = parseInt(p) === 1;
let lastpage = false;
for (let i = p * 5 - 4; i < p * 5 + 1; i++) {
  if (i === 1) {
    lastpage = true;
  }
  fetch(`/data/haberler/haber-${i}.json`).then((res) =>
    res.json().then((jsonres) => {
      document.querySelector(
        "div#haberler"
      ).innerHTML += `<div class="haber"><a href="/haber.html?id=${i}"><img src="${jsonres.thumbnail}" alt="haber küçük resim" /><div><h1>${jsonres.title}</h1><p>${jsonres.summary}</p></a></div>`;
    })
  );
}