document.getElementById("download-form").addEventListener("submit", async function(event) {
  event.preventDefault();
  
  const boardUrl = document.getElementById("board-url").value;
  const statusText = document.getElementById("status");
  const loader = document.getElementById("loader");

  loader.style.display = "block";
  statusText.textContent = "";

  const response = await fetch("/download", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ board_url: boardUrl })
  });

  const data = await response.json();
  loader.style.display = "none";

  if (response.ok && data.download_url) {
    window.location.href = data.download_url;
    statusText.textContent = "✅ Your download is ready!";
  } else {
    statusText.textContent = "❌ Error: " + (data.detail || "Something went wrong.");
  }
});
