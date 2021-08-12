const urlParams = new URLSearchParams(window.location.search);
let p;
if (!urlParams.get("p")) {
  p = 1;
} else {
  p = urlParams.get("p");
}
p = parseInt(p);
const firstpage = parseInt(p) === 1;
let lastpage = false;
for (let i = p * 5; i > p * 5 - 5; i--) {
  console.log(p);
  if (i === 1) {
    lastpage = true;
  }
  fetch(`/data/haberler/haber-${i}.json`).then((res) =>
    res.json().then((jsonres) => {
      let element = document.createElement("div");
      element.className = "haber";
      let link = document.createElement("a");
      link.setAttribute("href", `/haber.html?id=${i}`);
      let img = document.createElement("img");
      img.src = jsonres.thumbnail;
      img.alt = "haber küçük resim";
      link.appendChild(img);
      let div = document.createElement("div");
      let h1 = document.createElement("h1");
      h1.appendChild(document.createTextNode(jsonres.title));
      div.appendChild(h1);
      let p = document.createElement("p");
      p.appendChild(document.createTextNode(jsonres.summary));
      div.appendChild(p);
      link.appendChild(div);
      element.appendChild(link);
      document.querySelector("div#haberler").appendChild(element);
    })
  );
}
