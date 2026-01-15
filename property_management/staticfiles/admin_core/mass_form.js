
// admin_core/mass_form.js

document.addEventListener("DOMContentLoaded", function () {
    const addBtn = document.getElementById("add-row-btn");
    if (!addBtn) return;

    addBtn.addEventListener("click", function () {
        const totalForms = document.getElementById("id_form-TOTAL_FORMS");
        const formCount = parseInt(totalForms.value);

        const emptyForm = document.getElementById("empty-form").innerHTML;
        const newFormHtml = emptyForm.replace(/__prefix__/g, formCount);

        document.getElementById("formset-body")
            .insertAdjacentHTML("beforeend", newFormHtml);

        totalForms.value = formCount + 1;
    });
});
