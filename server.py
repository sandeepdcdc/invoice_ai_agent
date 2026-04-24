from flask import Flask, request, jsonify
import pymysql
from extractor import extract_invoice_data

app = Flask(__name__)

@app.route('/')
def home():
    return "Server is running"

@app.route('/process', methods=['POST'])
def process_invoice():
    try:
        file = request.files['file']
        branch_id = request.form['branch_id']

        invoice_no, amount = extract_invoice_data(
            file.read(),
            file.filename
        )

        # ✅ Create fresh DB connection
        conn = pymysql.connect(
            host="45.114.246.232",
            user="root",
            password="cia%23@08@#%OPD!@#",   # 🔴 update if needed
            database="dcdclive_30_2026"
        )

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO invoices (branch_id, invoice_no, amount)
            VALUES (%s, %s, %s)
        """, (branch_id, invoice_no, amount))

        conn.commit()
        conn.close()

        return jsonify({
            "invoice_no": invoice_no,
            "amount": amount
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("🚀 Starting Flask server...")
    app.run(host='127.0.0.1', port=5000, debug=True)