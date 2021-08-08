if (!firstpage)
  document
    .querySelector("a#leftarrow")
    .setAttribute("href", `/haberler.html?p=${p - 1}`);
document.querySelector("span#pagenumber").appendChild = document.createTextNode(p);
if (!lastpage)
  document
    .querySelector("a#rightarrow")
    .setAttribute("href", `/haberler.html?p=${p + 1}`);