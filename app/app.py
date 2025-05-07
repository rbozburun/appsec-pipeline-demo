from flask import Flask, render_template, request

app = Flask(__name__)

# Hardcoded password vulnerability
HARDCODED_PASSWORD = "P@ssw0rd123"

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    if request.method == "POST":
        name = request.form.get("name", "")
        password = request.form.get("password", "")
        if password == HARDCODED_PASSWORD:
            message = f"Welcome {name}, you are authenticated!"
        else:
            message = "Invalid password."
    return render_template("index.html", message=message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)