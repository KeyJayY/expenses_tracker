from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import math
import os
from dotenv import load_dotenv

app = Flask(__name__, static_folder="static")
CORS(app)

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT"),
    options=os.getenv("DB_OPTIONS"),
)


@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/records", methods=["GET"])
def get_records():
    page = int(request.args.get("page", 0))
    page_size = int(request.args.get("page_size", 5))
    sort_by = request.args.get("sort_by", "date")
    sort_order = request.args.get("sort_order", "desc")
    query = request.args.get("query", "")

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        where_clause = ""
        values = []

        if query:
            where_clause = (
                "WHERE title ILIKE %s OR category ILIKE %s OR description ILIKE %s"
            )
            like_query = f"%{query}%"
            values = [like_query, like_query, like_query]

        count_sql = f"SELECT COUNT(*) FROM expenses {where_clause}"
        cur.execute(count_sql, values)
        total_count = cur.fetchone()["count"]
        total_pages = math.ceil(total_count / page_size)

        sql = f"""
        SELECT * FROM expenses
        {where_clause}
        ORDER BY {sort_by} {sort_order}
        LIMIT %s OFFSET %s
        """
        values += [page_size, page * page_size]
        cur.execute(sql, values)
        records = cur.fetchall()

    return jsonify({"records": records, "total_pages": total_pages})


@app.route("/records", methods=["POST"])
def create_record():
    data = request.get_json()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO expenses (date, amount, category, title, description) VALUES (%s, %s, %s, %s, %s)",
            (
                data["date"],
                data["amount"],
                data["category"],
                data["title"],
                data.get("desc"),
            ),
        )
        conn.commit()
    return jsonify({"message": "Record added"}), 201


@app.route("/records/<int:record_id>", methods=["PUT"])
def update_record(record_id):
    data = request.get_json()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE expenses SET date=%s, amount=%s, category=%s, title=%s, description=%s WHERE id=%s",
            (
                data["date"],
                data["amount"],
                data["category"],
                data["title"],
                data.get("desc"),
                record_id,
            ),
        )
        conn.commit()
    return jsonify({"message": "Record updated"})


@app.route("/records/<int:record_id>", methods=["DELETE"])
def delete_record(record_id):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM expenses WHERE id = %s", (record_id,))
        conn.commit()
    return jsonify({"message": "Record deleted"})


if __name__ == "__main__":
    app.run(port=7000)
