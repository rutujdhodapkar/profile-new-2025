#app.py
# app.py

import os
import pandas as pd
from flask import Flask, send_file, abort, request, jsonify, Response

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(ROOT_DIR, "static")
DATA_CSV_PATH = os.path.join(STATIC_DIR, "data.csv")
FEEDBACK_CSV_PATH = os.path.join(STATIC_DIR, "feedbackdata.csv")
SIGNUP_CSV_PATH = os.path.join(STATIC_DIR, "signup.csv")

name = "Rutuj Dhodapkar"

app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/static"
)

@app.route('/')
def index():
    # Serve loading animation.html from static directory
    main_html_path = os.path.join(STATIC_DIR, "loading animation.html")
    if not os.path.isfile(main_html_path):
        return "loading animation.html not found.", 404
    return send_file(main_html_path)

@app.route('/show-data')
def show_data():
    # Serve data.csv as an HTML table
    if not os.path.isfile(DATA_CSV_PATH):
        return "data.csv not found.", 404
    df = pd.read_csv(DATA_CSV_PATH)
    return df.to_html(index=False)

@app.route('/data.csv')
def download_data():
    # Allow direct download of data.csv
    if not os.path.isfile(DATA_CSV_PATH):
        abort(404)
    return send_file(DATA_CSV_PATH, as_attachment=True)

@app.route('/image-from-data/<int:row_idx>')
def serve_image_from_data(row_idx):
    """
    Serve an image file whose path is specified in the data.csv at the given row index.
    The column name for the image path is assumed to be 'pimgpath'.
    The path is relative to the static directory.
    """
    if not os.path.isfile(DATA_CSV_PATH):
        abort(404)
    try:
        df = pd.read_csv(DATA_CSV_PATH)
        if row_idx < 0 or row_idx >= len(df):
            abort(404)
        img_path = df.iloc[row_idx].get('pimgpath', None)
        if not img_path or not isinstance(img_path, str) or not img_path.strip():
            abort(404)
        img_path = img_path.strip().strip('"').strip("'")
        if not os.path.isabs(img_path):
            img_path = os.path.join(STATIC_DIR, img_path)
        img_path = os.path.normpath(img_path)
        # Prevent directory traversal
        if not img_path.startswith(os.path.abspath(STATIC_DIR)):
            abort(403)
        if not os.path.isfile(img_path):
            abort(404)
        return send_file(img_path)
    except Exception as e:
        abort(500)

@app.route('/image-by-path')
def serve_image_by_path():
    """
    Serve an image file by a relative path (from STATIC_DIR) provided as a query parameter.
    Example: /image-by-path?img=images/myimg.png
    """
    img = request.args.get('img', '')
    if not img:
        abort(400)
    img_path = os.path.normpath(os.path.join(STATIC_DIR, img))
    # Prevent directory traversal
    if not img_path.startswith(os.path.abspath(STATIC_DIR)):
        abort(403)
    if not os.path.isfile(img_path):
        abort(404)
    return send_file(img_path)

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    """
    Accept feedback form data via POST and store it in feedbackdata.csv.
    Expects JSON or form data with keys: name, email, rating, feedback.
    """
    # Accept both JSON and form data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    rating = data.get('rating', '').strip()
    feedback = data.get('feedback', '').strip()

    if not (name and email and rating and feedback):
        return jsonify({"success": False, "error": "All fields are required."}), 400

    # Prepare row as dict
    row = {
        "name": name,
        "email": email,
        "rating": rating,
        "feedback": feedback
    }

    # If file does not exist, create with header
    file_exists = os.path.isfile(FEEDBACK_CSV_PATH)
    try:
        df = pd.DataFrame([row])
        if not file_exists:
            df.to_csv(FEEDBACK_CSV_PATH, index=False, mode='w')
        else:
            df.to_csv(FEEDBACK_CSV_PATH, index=False, mode='a', header=False)
    except Exception as e:
        return jsonify({"success": False, "error": "Failed to save feedback."}), 500

    return jsonify({"success": True})

@app.route('/submit-signup', methods=['POST'])
def submit_signup():
    """
    Accept signup form data via POST and store it in signup.csv.
    Expects JSON or form data with keys: name, email, country.
    """
    # Accept both JSON and form data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    country = data.get('country', '').strip()

    if not (name and email and country):
        return jsonify({"success": False, "error": "All fields are required."}), 400

    # Prepare row as dict
    row = {
        "name": name,
        "email": email,
        "country": country
    }

    # If file does not exist, create with header
    file_exists = os.path.isfile(SIGNUP_CSV_PATH)
    try:
        df = pd.DataFrame([row])
        if not file_exists:
            df.to_csv(SIGNUP_CSV_PATH, index=False, mode='w')
        else:
            df.to_csv(SIGNUP_CSV_PATH, index=False, mode='a', header=False)
    except Exception as e:
        return jsonify({"success": False, "error": "Failed to save signup."}), 500

    return jsonify({"success": True})

@app.route('/<path:page>')
def serve_any_page(page):
    # Allow opening any page (HTML file) in the static directory
    # Only allow .html files for security
    if not page.lower().endswith('.html'):
        abort(404)
    safe_path = os.path.normpath(os.path.join(STATIC_DIR, page))
    # Prevent directory traversal
    if not safe_path.startswith(os.path.abspath(STATIC_DIR)):
        abort(403)
    if not os.path.isfile(safe_path):
        abort(404)
    return send_file(safe_path)

# Route to serve .woff font files from the static directory
@app.route('/font/<path:filename>')
def serve_woff_file(filename):
    # Only allow .woff files
    if not filename.lower().endswith('.woff'):
        abort(404)
    font_path = os.path.normpath(os.path.join(STATIC_DIR, "font", filename))
    # Prevent directory traversal
    if not font_path.startswith(os.path.abspath(os.path.join(STATIC_DIR, "font"))):
        abort(403)
    if not os.path.isfile(font_path):
        abort(404)
    # Set correct mimetype for woff fonts
    return send_file(font_path, mimetype="font/woff")

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_ENV") != "production"
    )
