// API element hover-highlight preference.
const HOVER_HIGHLIGHTS_KEY = "sonolink-docs-hover-highlights";
const HOVER_HIGHLIGHTS_DISABLED_CLASS = "hover-highlights-disabled";

(() => {
    if (localStorage.getItem(HOVER_HIGHLIGHTS_KEY) === "disabled") {
        document.body.classList.add(HOVER_HIGHLIGHTS_DISABLED_CLASS);
    }
})();

document.addEventListener("DOMContentLoaded", () => {
    const checkbox = document.getElementById("hover-highlights-checkbox");
    if (!checkbox) return;

    const highlightsEnabled =
        localStorage.getItem(HOVER_HIGHLIGHTS_KEY) !== "disabled";
    checkbox.checked = highlightsEnabled;

    checkbox.addEventListener("change", () => {
        const enabled = checkbox.checked;
        localStorage.setItem(
            HOVER_HIGHLIGHTS_KEY,
            enabled ? "enabled" : "disabled",
        );
        document.body.classList.toggle(HOVER_HIGHLIGHTS_DISABLED_CLASS, !enabled);
    });
});
