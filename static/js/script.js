function fetchVideoInfo() {
  const videoUrl = document.getElementById("video-url").value.trim();
  const videoInfo = document.getElementById("videoInfo");
  const loader = document.getElementById("loader");
  const message = document.getElementById("message");
  const titleEl = document.getElementById("videoTitle");
  const thumbEl = document.getElementById("thumbnail");
  const btnContainer = document.getElementById("resolutionButtons");

  message.textContent = "";
  videoInfo.style.display = "none";
  loader.style.display = "block";
  btnContainer.style.display = "none";

  fetch("/video_info", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ video_url: videoUrl })
  })
    .then(res => res.json())
    .then(data => {
      loader.style.display = "none";
      if (data.success) {
        videoInfo.style.display = "block";
        titleEl.textContent = data.title;
        thumbEl.src = data.thumbnail;
        btnContainer.style.display = "flex";

        const allBtns = btnContainer.querySelectorAll(".res-btn");
        allBtns.forEach(btn => btn.style.display = "none");

        let selectedResolution = null;

        data.resolutions.forEach(res => {
          const btn = document.getElementById(`res-${res}`);
          if (btn) {
            btn.style.display = "inline-block";

            btn.onclick = () => {
              document.querySelectorAll(".res-btn").forEach(b => b.classList.remove("selected-res"));
              btn.classList.add("selected-res");

              selectedResolution = res;
              const downloadBtn = document.getElementById("downloadBtn");
              downloadBtn.style.display = "block";

              downloadBtn.onclick = () => {
                if (!selectedResolution) {
                  alert("Please select a resolution first.");
                  return;
                }
                startDownload(videoUrl, selectedResolution);
              };
            };
          }
        });

      } else {
        message.textContent = data.message;
        message.style.color = "red";
      }
    })
    .catch(err => {
      loader.style.display = "none";
      message.textContent = "❌ Error: " + err.message;
      message.style.color = "red";
    });
}

function startDownload(videoUrl, resolution) {
  const loader = document.getElementById("loader");
  const message = document.getElementById("message");

  loader.style.display = "block";
  message.textContent = "";

  fetch("/download", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ video_url: videoUrl, resolution: resolution })
  })
    .then(res => res.json())
    .then(data => {
      loader.style.display = "none";
      if (data.success) {
        message.innerHTML = `✅ <a href="${data.download_url}" target="_blank" download>Click here to download (${resolution}p)</a>`;
        message.style.color = "green";
      } else {
        message.textContent = "❌ Error: " + data.message;
        message.style.color = "red";
      }
    })
    .catch(err => {
      loader.style.display = "none";
      message.textContent = "❌ Error: " + err.message;
      message.style.color = "red";
    });
}

document.querySelectorAll('.qa-question').forEach(button => {
  button.addEventListener('click', () => {
    const answer = button.nextElementSibling;
    const isOpen = answer.style.display === 'block';
    document.querySelectorAll('.qa-answer').forEach(a => a.style.display = 'none');
    answer.style.display = isOpen ? 'none' : 'block';
  });
});

function pasteLink() {
  navigator.clipboard.readText()
    .then(text => {
      document.getElementById("video-url").value = text;
      fetchVideoInfo(); // Automatically fetch when pasted
    })
    .catch(err => {
      alert("Failed to access clipboard. Paste manually.");
      console.error(err);
    });
}

document.addEventListener("DOMContentLoaded", function () {
  const scrollElements = document.querySelectorAll(".scroll-fade");

  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.2 });

  scrollElements.forEach(el => observer.observe(el));

  const toggleBtn = document.getElementById("themeToggle");
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const savedTheme = localStorage.getItem("theme");

  if (savedTheme === "dark" || (!savedTheme && prefersDark)) {
    document.documentElement.classList.add("dark-mode");
    toggleBtn.textContent = "☀️";
  }

  toggleBtn.addEventListener("click", () => {
    const isDark = document.documentElement.classList.toggle("dark-mode");
    localStorage.setItem("theme", isDark ? "dark" : "light");
    toggleBtn.textContent = isDark ? "☀️" : "🌙";
  });
});
