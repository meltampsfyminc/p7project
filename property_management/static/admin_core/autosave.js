// admin_core/autosave.js
// Preserves formset data using sessionStorage (page reload / accidental navigation safe)

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    if (!form) return;

    const STORAGE_KEY = "admin_core_mass_form";

    // Restore saved data
    const savedData = sessionStorage.getItem(STORAGE_KEY);
    if (savedData) {
        try {
            const parsed = JSON.parse(savedData);
            parsed.forEach(item => {
                const field = document.querySelector(
                    `[name="${item.name}"]`
                );
                if (field) {
                    field.value = item.value;
                }
            });
        } catch (e) {
            console.warn("Autosave restore failed:", e);
        }
    }

    // Save on every change
    form.addEventListener("input", function () {
        const data = [];
        const inputs = form.querySelectorAll(
            "input, select, textarea"
        );

        inputs.forEach(el => {
            if (el.name && el.type !== "hidden" && el.type !== "csrf") {
                data.push({
                    name: el.name,
                    value: el.value
                });
            }
        });

        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    });

    // Clear autosave after successful submit
    form.addEventListener("submit", function () {
        sessionStorage.removeItem(STORAGE_KEY);
    });
});
