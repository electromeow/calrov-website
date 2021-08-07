if (!firstpage)
  document
    .querySelector("a#leftarrow")
    .setAttribute("href", `./haberler.html?p=${p - 1}`);
document.querySelector("span#pagenumber").innerHTML = p;
if (!lastpage)
  document
    .querySelector("a#rightarrow")
    .setAttribute("href", `./haberler.html?p=${p + 1}`);