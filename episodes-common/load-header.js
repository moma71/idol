document.addEventListener("DOMContentLoaded", () => {
  // 1) header 삽입
  fetch("/idol/episodes-common/header.html?v=" + Date.now())
    .then((response) => response.text())
    .then((data) => {
      document.body.insertAdjacentHTML("afterbegin", data);

      initHeaderLogic();
    });

  function initHeaderLogic() {
    const hamburgerBtn = document.getElementById("hamburgerBtn");
    const mobileNav = document.getElementById("mobileNav");

    if (!hamburgerBtn || !mobileNav) return;

    // 햄버거 토글
    hamburgerBtn.addEventListener("click", () => {
      mobileNav.classList.toggle("show");
    });

    // --- 에피소드 이동 자동 설정 ---
    const path = window.location.pathname;
    const episodeMatch = path.match(/episode(\d+)/);

    let prevLinks = document.querySelectorAll("#prev-ep, #m-prev-ep");
    let nextLinks = document.querySelectorAll("#next-ep, #m-next-ep");

    if (episodeMatch) {
      const currentNum = parseInt(episodeMatch[1]);

      const prevEp =
        currentNum > 1 ? `/idol/episode${currentNum - 1}/` : "#";
      const nextEp = `/idol/episode${currentNum + 1}/`;// Check specifically for index.html

// Update Previous Link
      prevLinks.forEach((a) => {
        if (currentNum > 1) {
          a.href = prevEp;
        } else {
          a.style.opacity = "0.5";
          a.style.pointerEvents = "none";
          a.href = "#";
        }
      });

      // Update Next Link with Existence Check
      nextLinks.forEach((a) => {
        a.href = nextEp; // Optimistic set

        fetch(nextEp, { method: 'HEAD' })
          .then(response => {
            if (!response.ok) {
              a.style.opacity = "0.5";
              a.style.pointerEvents = "none";
              a.removeAttribute('href');
              a.innerText = "다음화 없음"; // Optional text change
            }
          })
          .catch(() => {
            a.style.opacity = "0.5";
            a.style.pointerEvents = "none";
            a.removeAttribute('href');
          });
      });
    } else {
      prevLinks.forEach((a) => (a.style.display = "none"));
      nextLinks.forEach((a) => (a.style.display = "none"));
    }
  }
});
