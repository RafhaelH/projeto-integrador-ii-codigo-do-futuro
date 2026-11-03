document.addEventListener("click", (event) => {
  const link = event.target.closest("a[data-download-feedback]");
  if (!link) return;
  const feedback = document.getElementById("download-feedback");
  if (feedback) {
    feedback.hidden = false;
    feedback.textContent = "Download solicitado. Confira a área de downloads do navegador. Se o arquivo não aparecer, tente novamente.";
  }
});
