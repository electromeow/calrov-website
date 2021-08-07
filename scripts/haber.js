function main() {
  const urlParams = new URLSearchParams(window.location.search);
  if (!urlParams.get("id")) return;
  fetch(`./data/haberler/haber-${urlParams.get("id")}.json`)
    .then((res) =>
      res.json().then((jsonres) => {
        document.querySelector("section").innerHTML +=
          "<h1>" + jsonres.title + "</h1>" + jsonres.content;
        document.querySelector("title").innerHTML =
          jsonres.title + " - CALROV";
      })
    )
    .catch(console.error);
}
main();