
from flask import Flask, request, render_template_string
from pypdf import PdfReader
from io import BytesIO
import os

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Document Printing</title>
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    padding: 20px;
    background: #eef2f7;
    font-family: Arial, sans-serif;
}
.container {
    max-width: 440px;
    margin: 30px auto;
    padding: 25px;
    background: white;
    border-radius: 16px;
    box-shadow: 0 5px 20px #0001;
}
h1 { text-align: center; color: #172554; }
p { color: #555; text-align: center; }
label {
    display: block;
    margin-top: 18px;
    font-weight: bold;
}
input, select {
    width: 100%;
    padding: 13px;
    margin-top: 8px;
    border: 1px solid #ccc;
    border-radius: 8px;
    background: white;
}
button {
    width: 100%;
    padding: 15px;
    margin-top: 24px;
    background: #172554;
    color: white;
    border: 0;
    border-radius: 9px;
    font-size: 17px;
}
.price {
    background: #eef2ff;
    padding: 15px;
    border-radius: 9px;
    line-height: 1.8;
}
</style>
</head>
<body>
<div class="container">
<h1>Document Printing</h1>
<p>Upload your PDF and choose your printing option.</p>

<div class="price">
<b>Black & White:</b> ₹5 per page<br>
<b>Colour:</b> ₹10 per page
</div>

<form action="/upload" method="POST"
enctype="multipart/form-data">

<label>Your Name</label>
<input name="name" maxlength="60" required>

<label>Mobile Number</label>
<input name="mobile" type="tel"
pattern="[0-9]{10}" required>

<label>Choose Printing Type</label>
<select name="type" required>
<option value="bw">Black & White - ₹5/page</option>
<option value="color">Colour - ₹10/page</option>
</select>

<label>Upload PDF (Maximum 10 MB)</label>
<input type="file" name="file"
accept=".pdf,application/pdf" required>

<button type="submit">Calculate Price</button>
</form>
</div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/upload", methods=["POST"])
def upload():
    name = request.form.get("name", "").strip()
    mobile = request.form.get("mobile", "").strip()
    print_type = request.form.get("type")
    file = request.files.get("file")

    if not name or not mobile.isdigit() or len(mobile) != 10:
        return "Invalid name or mobile number", 400

    if print_type not in ("bw", "color"):
        return "Invalid printing type", 400

    if not file or not file.filename.lower().endswith(".pdf"):
        return "Please upload a PDF file", 400

    try:
        data = file.read()
        if not data.startswith(b"%PDF"):
            return "Invalid PDF file", 400

        reader = PdfReader(BytesIO(data), strict=True)

        if reader.is_encrypted:
            return "Password protected PDFs are not supported."

        pages = len(reader.pages)

        if pages < 1 or pages > 300:
            return "PDF must contain 1 to 300 pages."

    except Exception:
        return "Unable to read this PDF. Please try another."

    rate = 5 if print_type == "bw" else 10
    total = pages * rate

    kind = "Black & White" if print_type == "bw" else "Colour"

    return render_template_string("""
    <html>
    <head>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    </head>
    <body style="font-family:Arial;background:#eef2f7;padding:20px">
    <div style="max-width:420px;margin:30px auto;background:white;
    padding:25px;border-radius:15px">
    <h2>Order Price Summary</h2>
    <p>Name: {{name}}</p>
    <p>Pages: {{pages}}</p>
    <p>Print Type: {{kind}}</p>
    <p>Rate: ₹{{rate}} per page</p>
    <h2>Total: ₹{{total}}</h2>
    <p>Payment Status: NOT PAID</p>
    <p>Demo only: Payment gateway is not connected.</p>
    <a href="/">Go Back</a>
    </div>
    </body>
    </html>
    """, name=name, pages=pages, kind=kind,
       rate=rate, total=total)

@app.errorhandler(413)
def too_large(error):
    return "File is too large. Maximum size is 10 MB.", 413

@app.route("/health")
def health():
    return "Website is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
  
