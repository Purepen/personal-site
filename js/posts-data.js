// Hand-edited list of posts to showcase on posts.html. Each entry is a card
// that links to its own detail page (see context.md for the pattern to add
// a new one). No build step, just refresh the page.
//
// Fields: category (short label shown on the card), title, url (a page in
// this repo, e.g. "my-project.html"), date ('YYYY-MM' or a free label),
// excerpt, and thumbnail (path to an image; falls back to a neutral
// placeholder if omitted).

var CATEGORY_LABEL = {
  ai: "AI Engineering",
  bi: "Business Intelligence",
  ml: "Machine Learning",
  notes: "Notes",
};

var POSTS = [
  {
    category: "ai",
    title: "AI Banking Assistant: voice-first banking with two-factor security",
    url: "ai-banking-assistant.html",
    date: "2025",
    excerpt: "A voice-enabled banking assistant with 8 specialized tools, secure two-factor authentication, and sub-2-second responses.",
    thumbnail: "https://i.ytimg.com/vi/Hvwg5XZ3TR0/hqdefault.jpg",
  },
  {
    category: "ai",
    title: "CFO AI Assistant: five agents, one financial brain",
    url: "cfo-ai-assistant.html",
    date: "2024–2025",
    excerpt: "From a 3-agent GitHub prototype to a production-shaped v2: instant answers on financial metrics, CBN compliance, and market intelligence.",
    thumbnail: "https://i.ytimg.com/vi/Hmk_OsMPNt0/hqdefault.jpg",
  },
  {
    category: "ai",
    title: "MamaCare: teaching a cohort to ship an ML + LLM app",
    url: "mamacare-mentorship.html",
    date: "2026",
    excerpt: "An 8-week mentorship project for 3MTT and WeSonline students: a maternal health risk model, wrapped in an LLM advisor, shipped live.",
    thumbnail: "assets/post-placeholder.svg",
  },
  {
    category: "ai",
    title: "AccountAI: an end-to-end AI sales pipeline",
    url: "n8n-sales-automation.html",
    date: "2025",
    excerpt: "Drop in a targeting PDF and a multi-agent n8n pipeline finds prospects, drafts outreach, and books demos through a voice agent.",
    thumbnail: "assets/posts/n8n-sales-automation/hero-overview.jpg",
  },
  {
    category: "bi",
    title: "Car Sales Performance Dashboard",
    url: "powerbi-car-sales.html",
    date: "2023",
    excerpt: "A Power BI dashboard on a full star-schema model, with time-intelligence DAX, bookmarks, and page navigation.",
    thumbnail: "assets/post-placeholder.svg",
  },
  {
    category: "bi",
    title: "Insuring Success: a car insurance claims dashboard",
    url: "powerbi-insurance-claims.html",
    date: "2023",
    excerpt: "Built for Onyx Data's monthly challenge: 38,000 policy holders, $1.88bn in claim exposure, and five concrete recommendations.",
    thumbnail: "assets/posts/powerbi-insurance-claims/cover-page.jpg",
  },
  {
    category: "bi",
    title: "Credit Card Transaction Dashboard",
    url: "powerbi-credit-card.html",
    date: "2024",
    excerpt: "Indian credit card transactions broken down by city, expense category, and region, with bookmark-driven navigation.",
    thumbnail: "assets/posts/powerbi-credit-card/dashboard.jpg",
  },
  {
    category: "bi",
    title: "JU & TOSZ Sales Dashboard",
    url: "powerbi-sales-dashboard.html",
    date: "2024",
    excerpt: "A sales dashboard tracking product demand and regional performance, with theme switching and page navigation.",
    thumbnail: "assets/posts/powerbi-sales-dashboard/dashboard.png",
  },
  {
    category: "ml",
    title: "Forecasting Tanzania's air quality",
    url: "tanzania-air-quality.html",
    date: "2023",
    excerpt: "My first ML project: an ARIMA model on Dar es Salaam PM2.5 readings, cutting error from a baseline of 19.66 to 3.64.",
    thumbnail: "assets/post-placeholder.svg",
  },
  {
    category: "notes",
    title: "AI has no brain",
    url: "ai-has-no-brain.html",
    date: "2025",
    excerpt: "It doesn't know anything, and it doesn't remember you. It's just extraordinarily good at guessing the next word.",
    thumbnail: "assets/posts/ai-has-no-brain/token-probability.jpg",
  },
  {
    category: "notes",
    title: "Why C++ is the machine's best friend",
    url: "cpp-vs-python.html",
    date: "2025",
    excerpt: "A buka in Ondo State explains compiled versus interpreted languages better than any textbook.",
    thumbnail: "assets/posts/cpp-vs-python/buka-street.jpg",
  },
];

function renderPosts() {
  var grid = document.getElementById("postGrid");
  if (!grid) return;
  grid.innerHTML = POSTS.map(function (post) {
    var thumb = post.thumbnail || "assets/post-placeholder.svg";
    return (
      '<a class="post-card" href="' + post.url + '">' +
        '<div class="post-card__thumb">' +
          '<img src="' + thumb + '" alt="" loading="lazy" />' +
          '<span class="post-card__platform">' + CATEGORY_LABEL[post.category] + '</span>' +
        '</div>' +
        '<div class="post-card__body">' +
          '<span class="post-card__date">' + post.date + '</span>' +
          '<span class="post-card__title">' + post.title + '</span>' +
          '<p class="post-card__excerpt">' + post.excerpt + '</p>' +
        '</div>' +
      '</a>'
    );
  }).join("");
}

document.addEventListener("DOMContentLoaded", renderPosts);
