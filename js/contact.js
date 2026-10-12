// Sends the contact form through Web3Forms (https://web3forms.com), which
// emails it straight to olaniyimicheal1376@gmail.com. No backend of our own.
// The access key is public by design: it only lets people send to that inbox.
(function () {
  var ACCESS_KEY = "e878f283-3068-4476-a14d-4093d38cd385";
  var FALLBACK_EMAIL = "olaniyimicheal1376@gmail.com";

  var form = document.getElementById("contactForm");
  if (!form) return;
  var button = form.querySelector('button[type="submit"]');
  var status = document.getElementById("cfStatus");

  function show(text, kind, html) {
    status.className = "form-status form-status--" + kind;
    if (html) status.innerHTML = html; else status.textContent = text;
    status.hidden = false;
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var name = document.getElementById("cfName").value.trim();
    var email = document.getElementById("cfEmail").value.trim();
    var message = document.getElementById("cfMessage").value.trim();

    button.disabled = true;
    show("Sending...", "pending");

    fetch("https://api.web3forms.com/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({
        access_key: ACCESS_KEY,
        subject: "New message from " + name + " (micheal.fly.dev)",
        from_name: "micheal.fly.dev contact form",
        name: name,
        email: email,
        message: message,
        botcheck: form.querySelector('[name="botcheck"]').checked
      })
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (!data.success) throw new Error(data.message || "Send failed");
        form.reset();
        show("Thanks, " + name + ". Your message is in my inbox and I'll reply to " + email + " soon.", "ok");
      })
      .catch(function () {
        show("", "error",
          "Sorry, that didn't go through. Please email me directly at " +
          '<a href="mailto:' + FALLBACK_EMAIL + '">' + FALLBACK_EMAIL + "</a> or try again in a moment.");
      })
      .then(function () { button.disabled = false; });
  });
})();
