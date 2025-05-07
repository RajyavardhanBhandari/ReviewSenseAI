const express = require("express");
const multer = require("multer");
const app = express();
const port = 3000;

// Configure multer to store files in "uploads" folder
const storage = multer.diskStorage({
    destination: (req, file, cb) => cb(null, "uploads/"),
    filename: (req, file, cb) => cb(null, file.originalname),
});
const upload = multer({ storage: storage });

app.use(express.static("public"));

// Handle file upload
app.post("/upload", upload.single("file"), (req, res) => {
    res.send("✅ File uploaded successfully!");
});

// Handle text review submission
app.post("/submit_review", express.json(), (req, res) => {
    console.log("Received review:", req.body);
    res.send("✅ Review submitted successfully!");
});

// Start the server
app.listen(port, () => console.log(`🚀 Server running on http://127.0.0.1:${port}`));
