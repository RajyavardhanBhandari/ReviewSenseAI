from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload_video():
    if "file" not in request.files:
        return "No file part", 400
    file = request.files["file"]
    file.save("uploads/" + file.filename)
    return "File uploaded successfully!", 200

@app.route("/submit_review", methods=["POST"])
def submit_review():
    review = request.form.get("text_review")
    return jsonify({"message": "Review received!", "review": review})

if __name__ == "__main__":
    app.run(debug=True)
