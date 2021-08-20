function main() {
  const urlParams = new URLSearchParams(window.location.search);
  if (!urlParams.get("id")) return;
  fetch(`/data/haberler/haber-${urlParams.get("id")}.json`)
    .then((res) =>
      res
        .json()
        .then((jsonres) => {
          let element = document.createElement("h1");
          element.appendChild(document.createTextNode(jsonres.title));
          let section = document.querySelector("section");
          document.querySelector("head meta[name=description]").setAttribute("content", jsonres.summary);
          section.appendChild(element);
          section.innerHTML += jsonres.content;
          document.title = jsonres.title + " - CALROV";
          document.getElementsByName("twitter:title")[0].setAttribute("content", jsonres.title);
          document.getElementsByName("og:title")[0].setAttribute("content", jsonres.title);
          document.getElementsByName("twitter:description")[0].setAttribute("content", jsonres.summary);
          document.getElementsByName("og:description")[0].setAttribute("content", jsonres.summary);
          document.getElementsByName("twitter:card")[0].setAttribute("content", jsonres.thumbnail);
          document.getElementsByName("og:url")[0].setAttribute("content", jsonres.link);
        })
        .catch(console.error)
    )
    .catch(console.error);
}
main();
