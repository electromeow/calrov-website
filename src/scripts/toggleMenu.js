function toggleMenu() {
  document.querySelector("nav ul").classList.toggle("opened");
  const hamburgerIcon = document.querySelector("i[name=hamburger]");
  hamburgerIcon.classList.toggle("fa-bars");
  hamburgerIcon.classList.toggle("fa-times");
}
