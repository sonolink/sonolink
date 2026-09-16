// Content Width Toggle Functionality
const CONTENT_WIDTH_KEY = "sonolink-docs-content-width";

(() => {
  const savedWidth = localStorage.getItem(CONTENT_WIDTH_KEY);
  const isWide = savedWidth === "wide";
  if (isWide) {
    document.body.classList.add("wide-mode");
  }
})();

document.addEventListener("DOMContentLoaded", () => {
  const standardRadio = document.getElementById("standard-width-radio");
  const wideRadio = document.getElementById("wide-width-radio");

  if (!standardRadio || !wideRadio) return;

  const savedWidth = localStorage.getItem(CONTENT_WIDTH_KEY);
  const isWide = savedWidth === "wide";

  if (isWide) {
    wideRadio.checked = true;
  } else {
    standardRadio.checked = true;
  }

  standardRadio.addEventListener("change", () => {
    if (standardRadio.checked) {
      localStorage.setItem(CONTENT_WIDTH_KEY, "standard");
      document.body.classList.remove("wide-mode");
    }
  });

  wideRadio.addEventListener("change", () => {
    if (wideRadio.checked) {
      localStorage.setItem(CONTENT_WIDTH_KEY, "wide");
      document.body.classList.add("wide-mode");
    }
  });
});
