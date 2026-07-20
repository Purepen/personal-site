// Read more / read less toggle for the Home page story section.
(function () {
  var toggle = document.getElementById("storyMoreToggle");
  var more = document.getElementById("storyMore");
  if (!toggle || !more) return;

  var label = toggle.querySelector(".story__more-label");

  toggle.addEventListener("click", function () {
    var expanded = toggle.getAttribute("aria-expanded") === "true";
    toggle.setAttribute("aria-expanded", String(!expanded));
    more.hidden = expanded;
    if (label) label.textContent = expanded ? "Read more" : "Read less";
  });
})();
