"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const csrf = document.querySelector('meta[name="csrf-token"]')?.content || "";

  document.querySelectorAll(".tool-form").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const button = form.querySelector("button[type=submit], button:not([type])");
      const output = form.parentElement.querySelector(".output");
      const payload = Object.fromEntries(new FormData(form).entries());
      const rdapCheckbox = form.querySelector('input[name="rdap"]');
      if (rdapCheckbox) payload.rdap = rdapCheckbox.checked;
      const endpoint = form.dataset.endpoint;

      if (!endpoint || !output) return;

      const originalText = button?.textContent || "Consultar";
      if (button) {
        button.disabled = true;
        button.textContent = "Consultando...";
      }
      output.textContent = "A consulta está em andamento…";

      try {
        const response = await fetch(endpoint, {
          method: "POST",
          credentials: "same-origin",
          headers: {
            "Content-Type": "application/json",
            "X-CSRF-Token": csrf
          },
          body: JSON.stringify(payload)
        });

        const body = await response.json().catch(() => ({}));
        if (!response.ok || !body.ok) {
          throw new Error(body.error || `Falha na consulta (HTTP ${response.status}).`);
        }
        output.textContent = JSON.stringify(body.result, null, 2);
      } catch (error) {
        output.textContent = error.message || "Não foi possível concluir a consulta.";
      } finally {
        if (button) {
          button.disabled = false;
          button.textContent = originalText;
        }
      }
    });
  });
});
