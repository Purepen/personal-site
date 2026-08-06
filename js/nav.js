// Active-link highlighting + mobile nav toggle. No theme switching here —
// this site is light-only; dark/light lives inside the embedded Avatar app.
(function () {
  var here = location.pathname.split("/").pop() || "index.html";
  // Project detail pages set <body data-nav="posts.html"> so "Posts" stays
  // highlighted as active while reading one, instead of nothing matching.
  var navGroup = document.body.getAttribute("data-nav") || here;
  document.querySelectorAll(".nav-links a").forEach(function (a) {
    var href = a.getAttribute("href");
    if (href === navGroup || href === here || (here === "" && href === "index.html")) {
      a.classList.add("is-active");
    }
  });

  var toggle = document.getElementById("navToggle");
  var links = document.querySelector(".nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      links.classList.toggle("is-open");
    });
    links.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        links.classList.remove("is-open");
      });
    });
  }
})();
