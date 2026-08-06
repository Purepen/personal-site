// Builds a mailto: link from the contact form fields and hands off to the
// visitor's email app. No backend, no third-party form service, nothing
// leaves the browser until the visitor hits send themselves.
(function () {
  var form = document.getElementById("contactForm");
  if (!form) return;

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var name = document.getElementById("cfName").value.trim();
    var email = document.getElementById("cfEmail").value.trim();
    var message = document.getElementById("cfMessage").value.trim();

    var subject = "New message from " + name;
    var body = message + "\n\nFrom: " + name + " (" + email + ")";
    var mailto =
      "mailto:olaniyimicheal1376@gmail.com" +
      "?subject=" + encodeURIComponent(subject) +
      "&body=" + encodeURIComponent(body);

    window.location.href = mailto;
  });
})();
