# from flask import Flask, request, jsonify
# import pymysql
# import os
# from extractor import extract_invoice_data

# app = Flask(__name__)

# @app.route('/')
# def home():
#     return "Server is running"

# @app.route('/process', methods=['POST'])
# def process_invoice():
#     try:
#         file = request.files['file']
#         branch_id = request.form['branch_id']

#         invoice_no, amount = extract_invoice_data(
#             file.read(),
#             file.filename
#         )

#         # Create fresh DB connection
#         conn = pymysql.connect(
#             host=os.getenv("DB_HOST"),
#             user=os.getenv("DB_USER"),
#             password=os.getenv("DB_PASS"),
#             database=os.getenv("DB_NAME"),
#             connect_timeout=10
#         )

#         cursor = conn.cursor()

#         cursor.execute("""
#             INSERT INTO invoices (branch_id, invoice_no, amount)
#             VALUES (%s, %s, %s)
#         """, (branch_id, invoice_no, amount))

#         conn.commit()
#         conn.close()

#         return jsonify({
#             "invoice_no": invoice_no,
#             "amount": amount
#         })

#     except Exception as e:
#         print("ERROR:", str(e))
#         return jsonify({"error": str(e)}), 500


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=10000)

from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import os
from extractor import extract_invoice_data

app = Flask(__name__)

# ✅ Enable CORS (required for HMIS integration)
CORS(app)


# -----------------------------
# Health Check API
# -----------------------------
@app.route('/')
def home():
    return "Invoice AI Agent Server is running"


# -----------------------------
# Process Invoice API
# -----------------------------
@app.route('/process', methods=['POST'])
def process_invoice():
    try:
        # =========================
        # Validate Input
        # =========================
        if 'file' not in request.files or 'branch_id' not in request.form:
            return jsonify({
                "status": "error",
                "message": "Missing file or branch_id"
            }), 400

        file = request.files['file']
        branch_id = request.form['branch_id']

        # =========================
        # Extract Invoice Data
        # =========================
        file_bytes = file.read()
        filename = file.filename

        invoice_no, amount = extract_invoice_data(file_bytes, filename)

        # =========================
        # Database Connection
        # =========================
        conn = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            connect_timeout=10,
            autocommit=True
        )

        cursor = conn.cursor()

        # =========================
        # Insert Data
        # =========================
        cursor.execute("""
            INSERT INTO invoices (branch_id, invoice_no, amount)
            VALUES (%s, %s, %s)
        """, (branch_id, invoice_no, amount))

        conn.close()

        # =========================
        # Success Response
        # =========================
        return jsonify({
            "status": "success",
            "invoice_no": invoice_no,
            "amount": amount
        })

    except Exception as e:
        print("ERROR:", str(e))

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)