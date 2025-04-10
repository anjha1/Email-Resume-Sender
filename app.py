from flask import Flask, request, jsonify, render_template, session
import os, json, subprocess

app = Flask(__name__)
app.secret_key = "replace_with_strong_secret"  # For session use
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/save_config", methods=["POST"])
def save_config():
    resume_file = request.files.get("resume_file")
    csv_file = request.files.get("csv_file")

    if not resume_file or not csv_file:
        return jsonify({"message": "Please upload both resume and CSV files"}), 400

    resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_file.filename)
    csv_path = os.path.join(app.config['UPLOAD_FOLDER'], csv_file.filename)

    resume_file.save(resume_path)
    csv_file.save(csv_path)

    session["sender_password"] = request.form.get("sender_password")

    config = {
        "sender_email": request.form.get("sender_email"),
        "subject": request.form.get("subject"),
        "message": request.form.get("message"),
        "resume_path": resume_path,
        "csv_path": csv_path
    }

    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

    return jsonify({"message": "Configuration saved successfully!"})

@app.route("/send_emails", methods=["POST"])
def send_emails():
    if "sender_password" not in session:
        return jsonify({"error": "Password missing from session"}), 401

    # Inject password into config temporarily
    with open("config.json", "r") as f:
        config = json.load(f)

    config["sender_password"] = session["sender_password"]

    temp_config_path = "temp_config.json"
    with open(temp_config_path, "w") as f:
        json.dump(config, f)

    try:
        result = subprocess.run(["python", "send_emails.py", temp_config_path],
                                capture_output=True, text=True)
        os.remove(temp_config_path)
        return jsonify({"output": result.stdout})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
