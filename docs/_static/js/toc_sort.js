// Alphabetically sort the "On this page" (right-hand) table of contents.
(() => {
    const getLabel = (li) => {
        const link = li.querySelector(":scope > a");
        return (link ? link.textContent : "").trim().toLowerCase();
    };

    const sortList = (ul) => {
        const items = Array.from(ul.children).filter((el) => el.tagName === "LI");
        items.sort((a, b) => getLabel(a).localeCompare(getLabel(b)));
        for (const li of items) {
            ul.appendChild(li);
            const nested = li.querySelector(":scope > ul");
            if (nested) sortList(nested);
        }
    };

    document.addEventListener("DOMContentLoaded", () => {
        const root = document.querySelector(".toc-tree");
        if (!root) return;

        const topLevel = root.querySelector(":scope > ul");
        if (!topLevel) return;

        // The first <li> is the page title itself (links to "#"); its
        // children are the page's actual headings, which is what we sort.
        const pageTitleItem = topLevel.querySelector(":scope > li");
        if (!pageTitleItem) return;

        const headings = pageTitleItem.querySelector(":scope > ul");
        if (headings) sortList(headings);
    });
})();
