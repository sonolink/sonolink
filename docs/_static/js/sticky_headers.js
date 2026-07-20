// Each h3's sticky offset must match the height of the h2 above it in the
// same section (heights vary with text length/viewport), so we measure
// every h2 and apply its height as the stacking offset to its own h3s.
(() => {
    const updateOffsets = () => {
        const headings = document.querySelectorAll("article h2, article h3");
        let currentH2Height = null;

        for (const heading of headings) {
            if (heading.tagName === "H2") {
                currentH2Height = heading.getBoundingClientRect().height;
            } else if (currentH2Height !== null) {
                heading.style.top = `${currentH2Height}px`;
            }
        }
    };

    document.addEventListener("DOMContentLoaded", updateOffsets);
    window.addEventListener("resize", updateOffsets);
})();
