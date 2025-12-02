document.addEventListener("DOMContentLoaded", () => {
  // 1) header 삽입
  fetch("/idol/episodes-common/header.html")
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
      const nextEp = `/idol/episode${currentNum + 1}/`;

      prevLinks.forEach((a) => (a.href = prevEp));
      nextLinks.forEach((a) => (a.href = nextEp));
    } else {
      prevLinks.forEach((a) => (a.style.display = "none"));
      nextLinks.forEach((a) => (a.style.display = "none"));
    }
  }
});
