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
fetch("/data/haberler/habercount.txt").then((res) =>
  res.text().then((textRes) => {
    const habercount = parseInt(textRes.trim());
    for (let i = habercount - (p - 1) * 5; i > habercount - p * 5; i--) {
      if (i === 1) {
        lastpage = true;
      }
      if(i === 0) break;
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
    if (!firstpage)
      document
        .querySelector("a#leftarrow")
        .setAttribute("href", `/haberler.html?p=${p - 1}`);
    if(firstpage) document.querySelector("a#leftarrow").classList.add("disabled");
    document
      .querySelector("span#pagenumber")
      .appendChild(document.createTextNode(p));
    if (!lastpage)
      document
        .querySelector("a#rightarrow")
        .setAttribute("href", `/haberler.html?p=${p + 1}`);
    if(lastpage) document.querySelector("a#rightarrow").classList.add("disabled");


  })
);
