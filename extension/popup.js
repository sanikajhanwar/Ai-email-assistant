
document.getElementById("summarizeBtn").addEventListener("click", async () => {
    let response = await fetch("http://127.0.0.1:5000/summarize-email");
    let data = await response.json();
    document.getElementById("summary").innerText = data.summary;
});
