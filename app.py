import sys
import os

# Ensure project root is in path so imports work
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, redirect, url_for
from database import init_db
from routes.auth import auth_bp
from routes.transactions import transactions_bp
from routes.summary import summary_bp

app = Flask(__name__)
app.secret_key = "finance_tracker_secret_key_2026"

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(summary_bp)

@app.route('/')
def index():
    return redirect(url_for('auth.login'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)