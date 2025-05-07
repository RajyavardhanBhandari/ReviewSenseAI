document.getElementById("uploadForm").addEventListener("submit", function(event) {
    event.preventDefault();  // Prevents page reload

    let fileInput = document.querySelector('input[type="file"]');
    
    if (fileInput.files.length === 0) {
        alert("❌ No file selected!");
        return;
    }

    console.log("📤 Uploading file:", fileInput.files[0].name);  // Debugging

    let formData = new FormData(this);

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        console.log("✅ Upload Response:", data);
        alert("✅ Video uploaded successfully!");
    })
    .catch(error => {
        console.error("❌ Upload failed:", error);
        alert("❌ Upload failed: " + error);
    });
});
