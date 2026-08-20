document.addEventListener("DOMContentLoaded", () => {
    const menuButton = document.querySelector("[data-menu-button]");
    const mobileMenu = document.querySelector("[data-mobile-menu]");
    const openIcon = document.querySelector("[data-menu-open]");
    const closeIcon = document.querySelector("[data-menu-close]");

    if (!menuButton || !mobileMenu || !openIcon || !closeIcon) {
        return;
    }

    const updateMenu = (isOpen) => {
        mobileMenu.classList.toggle("hidden", !isOpen);
        openIcon.classList.toggle("hidden", isOpen);
        closeIcon.classList.toggle("hidden", !isOpen);

        menuButton.setAttribute("aria-expanded", String(isOpen));
        menuButton.setAttribute(
            "aria-label",
            isOpen ? "Cerrar menú principal" : "Abrir menú principal"
        );
    };

    menuButton.addEventListener("click", () => {
        const isOpen = menuButton.getAttribute("aria-expanded") === "true";
        updateMenu(!isOpen);
    });

    mobileMenu.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => updateMenu(false));
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            updateMenu(false);
            menuButton.focus();
        }
    });

    window.addEventListener("resize", () => {
        if (window.matchMedia("(min-width: 1024px)").matches) {
            updateMenu(false);
        }
    });
});