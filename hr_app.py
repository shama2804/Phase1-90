from flask import Flask
from routes import hr_bp
import os

# Force template folder
TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=TEMPLATE_DIR)

app.secret_key = "shama-key"
app.register_blueprint(hr_bp)

if __name__ == "__main__":
    print("💡 Flask running from hr_app.py...")
    app.run(debug=True)
