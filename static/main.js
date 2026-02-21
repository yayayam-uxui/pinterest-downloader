document.getElementById("download-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const boardUrlInput = document.getElementById("board-url");
  const statusText = document.getElementById("status");
  const loader = document.getElementById("loader");
  const submitButton = event.target.querySelector("button[type='submit']");
  const boardUrl = boardUrlInput.value.trim();

  loader.style.display = "block";
  statusText.textContent = "";
  submitButton.disabled = true;

  try {
    const response = await fetch("/download", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ board_url: boardUrl })
    });

    const data = await response.json();
    if (response.ok && data.download_url) {
      window.location.href = data.download_url;
      statusText.textContent = "✅ Your download is ready!";
      return;
    }

    statusText.textContent = "❌ Error: " + (data.detail || "Something went wrong.");
  } catch (error) {
    statusText.textContent = "❌ Network error. Please try again.";
  } finally {
    loader.style.display = "none";
    submitButton.disabled = false;
  }
});
