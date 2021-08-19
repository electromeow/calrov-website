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
        })
        .catch(console.error)
    )
    .catch(console.error);
}
main();
