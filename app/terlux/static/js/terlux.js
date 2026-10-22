(() => {
  const toggle = (button, panel) => {
    if (!button || !panel) return;
    button.addEventListener("click", () => {
      const open = panel.classList.toggle("hidden");
      button.setAttribute("aria-expanded", String(!open));
      if (!open) panel.querySelector("input, a, button")?.focus({ preventScroll: true });
    });
  };

  toggle(document.querySelector("[data-menu-toggle]"), document.querySelector("[data-menu-panel]"));
  toggle(document.querySelector("[data-search-toggle]"), document.querySelector("[data-search-panel]"));

  const gallery = document.querySelector("[data-gallery]");
  if (gallery) {
    const main = gallery.querySelector("[data-gallery-main]");
    const thumbs = [...gallery.querySelectorAll("[data-gallery-thumb]")];
    thumbs.forEach((thumb) => {
      thumb.addEventListener("click", () => {
        main.src = thumb.dataset.src;
        thumbs.forEach((other) => {
          other.classList.toggle("border-ink", other === thumb);
          other.classList.toggle("border-line", other !== thumb);
        });
      });
    });
  }

  document.querySelectorAll("[data-hide-with-js]").forEach((node) => node.remove());
  document.querySelectorAll("select[data-autosubmit]").forEach((select) => {
    select.addEventListener("change", () => select.form?.requestSubmit());
  });
})();
