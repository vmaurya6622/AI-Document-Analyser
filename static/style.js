async function uploadAndAnalyze() {
  const formData = new FormData(document.getElementById("uploadForm"));
  document.getElementById("status").innerText = "📂 Uploading and analyzing...";

  try {
    const response = await fetch("/analyze", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      document.getElementById("status").innerText = "❌ Error occurred during analysis.";
      return;
    }

    const result = await response.json();
    document.getElementById("status").innerText = "✅ Analysis complete.";

    const table = document.getElementById("resultsTable");
    table.innerHTML = "<tr><th>Serial</th><th>PDF Name</th><th>Document Type</th><th>Summary</th></tr>";

    result.forEach((row) => {
      const tr = document.createElement("tr");
      row.forEach((col) => {
        const td = document.createElement("td");
        td.textContent = col;
        tr.appendChild(td);
      });
      table.appendChild(tr);
    });

  } catch (error) {
    document.getElementById("status").innerText = "⚠️ Network or server error.";
    console.error("Upload error:", error);
  }
}
