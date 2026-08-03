// Hand-edited list of posts/videos to showcase. Add a new object to POSTS to
// publish a new entry - no build step, just refresh the page.
//
// Fields: platform ('youtube' | 'linkedin' | 'twitter' | 'other'), title, url,
// date ('YYYY-MM' or a free label), excerpt, and thumbnail (optional - YouTube
// entries auto-derive one from the video URL if you leave it out).

function getYoutubeThumbnail(url) {
  var match = url.match(/(?:youtu\.be\/|[?&]v=|\/embed\/)([\w-]{11})/);
  return match ? "https://i.ytimg.com/vi/" + match[1] + "/hqdefault.jpg" : null;
}

var PLATFORM_LABEL = {
  youtube: "YouTube",
  linkedin: "LinkedIn",
  twitter: "X / Twitter",
  other: "Link",
};

var POSTS = [
  {
    platform: "youtube",
    title: "AI Banking Assistant: voice-enabled, 8 specialized agents, sub-2s response",
    url: "https://youtu.be/Hvwg5XZ3TR0",
    date: "2025",
    excerpt: "A walkthrough of the banking assistant I built: secure 2FA, real-time voice interaction, serving 70+ users.",
  },
  {
    platform: "youtube",
    title: "CFO AI Assistant v2: multi-agent financial intelligence",
    url: "https://youtu.be/Hmk_OsMPNt0",
    date: "2025",
    excerpt: "Demo of the RAG pipeline (95%+ accuracy) and query routing built for Nigerian bank CFOs.",
  },
  {
    platform: "other",
    title: "CFO AI Assistant v1: the original build",
    url: "https://github.com/Purepen/CFO-ai-assistant",
    date: "2024",
    excerpt: "Where it started: GPT-4 and FAISS powering the first version of the financial intelligence assistant for Nigerian bank CFOs.",
    thumbnail: "assets/post-placeholder.svg",
  },
];

function renderPosts() {
  var grid = document.getElementById("postGrid");
  if (!grid) return;
  grid.innerHTML = POSTS.map(function (post) {
    var thumb = post.thumbnail || (post.platform === "youtube" ? getYoutubeThumbnail(post.url) : null) || "assets/post-placeholder.svg";
    return (
      '<a class="post-card" href="' + post.url + '" target="_blank" rel="noopener">' +
        '<div class="post-card__thumb">' +
          '<img src="' + thumb + '" alt="" loading="lazy" />' +
          '<span class="post-card__platform">' + PLATFORM_LABEL[post.platform] + '</span>' +
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
