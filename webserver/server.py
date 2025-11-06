"""
Columbia COMS W4111 Project 1 - Web Front-End (Group 119)

Run locally:
    python3 server.py
Go to http://localhost:8111
"""
import os
from typing import List, Dict, Any

from flask import Flask, request, render_template, g, redirect, url_for, abort
from sqlalchemy import create_engine, text


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir, static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'))


# Database configuration
DATABASE_USERNAME = "yx2948"
DATABASE_PASSWORD = "113211"
DATABASE_HOST = "35.227.79.146"
DATABASE_NAME = "proj1part2"  # Assumed database name used in course starter
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"


# Initialize engine
engine = create_engine(DATABASEURI)


@app.before_request
def before_request():
    try:
        g.conn = engine.connect()
    except Exception:
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    try:
        if g.get('conn') is not None:
            g.conn.close()
    except Exception:
        pass


def rows_to_dicts(cursor) -> List[Dict[str, Any]]:
    cols = cursor.keys()
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


@app.route('/')
def index():
    # List all unsold products with seller name
    query = text(
        """
        SELECT p.product_id, p.title, p.price, u.name AS seller_name
        FROM Products p
        JOIN Users u ON p.uid = u.uid
        WHERE p.is_sold = FALSE
        ORDER BY p.created_at DESC, p.product_id DESC
        """
    )
    cursor = g.conn.execute(query)
    products = rows_to_dicts(cursor)
    cursor.close()
    return render_template('index.html', products=products)


@app.route('/product/<int:product_id>')
def product_detail(product_id: int):
    query = text(
        """
        SELECT p.*, u.name AS seller_name, u.email AS seller_email, u.phone_number AS seller_phone
        FROM Products p
        JOIN Users u ON p.uid = u.uid
        WHERE p.product_id = :pid
        """
    )
    cursor = g.conn.execute(query, {"pid": product_id})
    row = cursor.fetchone()
    cursor.close()
    if row is None:
        abort(404)
    # Convert to dict for template convenience
    cols = row.keys()
    product = dict(zip(cols, row))
    return render_template('product.html', product=product)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'GET':
        return render_template('add_product.html')

    # POST: insert a new product
    uid = request.form.get('uid')
    title = request.form.get('title', '').strip()
    description = request.form.get('description')
    condition = request.form.get('condition')
    category = request.form.get('category')
    price = request.form.get('price')
    image_url = request.form.get('image_url')

    if not uid or not title or not category or not price:
        return render_template('add_product.html', error='Please fill in all required fields (uid, title, category, price).'), 400

    try:
        insert_q = text(
            """
            INSERT INTO Products (uid, title, description, condition, category, price, image_url, is_sold)
            VALUES (:uid, :title, :description, :condition, :category, :price, :image_url, FALSE)
            """
        )
        g.conn.execute(
            insert_q,
            {
                "uid": int(uid),
                "title": title,
                "description": description if description else None,
                "condition": condition if condition else None,
                "category": category,
                "price": float(price),
                "image_url": image_url if image_url else None,
            },
        )
        g.conn.commit()
    except Exception as e:
        return render_template('add_product.html', error=f'Error inserting product: {e}'), 500

    return redirect(url_for('index'))


@app.route('/mark_sold/<int:product_id>', methods=['POST', 'GET'])
def mark_sold(product_id: int):
    try:
        upd = text("UPDATE Products SET is_sold = TRUE WHERE product_id = :pid")
        g.conn.execute(upd, {"pid": product_id})
        g.conn.commit()
    except Exception as e:
        return f"Failed to mark sold: {e}", 500
    return redirect(url_for('index'))


@app.route('/search')
def search():
    q = request.args.get('q', '').strip()
    products: List[Dict[str, Any]] = []
    if q:
        pattern = f"%{q}%"
        query = text(
            """
            SELECT p.product_id, p.title, p.price, u.name AS seller_name
            FROM Products p
            JOIN Users u ON p.uid = u.uid
            WHERE (p.title ILIKE :pattern OR p.description ILIKE :pattern)
              AND p.is_sold = FALSE
            ORDER BY p.created_at DESC, p.product_id DESC
            """
        )
        cursor = g.conn.execute(query, {"pattern": pattern})
        products = rows_to_dicts(cursor)
        cursor.close()
    return render_template('search.html', q=q, products=products)


@app.route('/messages/<int:uid>')
def view_messages(uid: int):
    # Inbox for received messages
    query = text(
        """
        SELECT m.message_id, m.content, m.sent_at, m.is_read,
               s.name AS sender_name, s.uid AS sender_id
        FROM Messages m
        JOIN Users s ON m.sender_id = s.uid
        WHERE m.receiver_id = :uid
        ORDER BY m.sent_at DESC, m.message_id DESC
        """
    )
    cursor = g.conn.execute(query, {"uid": uid})
    messages = rows_to_dicts(cursor)
    cursor.close()
    return render_template('messages.html', uid=uid, messages=messages)


@app.route('/send_message', methods=['GET', 'POST'])
def send_message():
    if request.method == 'GET':
        return render_template('send_message.html')

    sender_id = request.form.get('sender_id')
    receiver_id = request.form.get('receiver_id')
    content = request.form.get('content', '').strip()

    if not sender_id or not receiver_id or not content:
        return render_template('send_message.html', error='All fields are required.'), 400

    try:
        # Get sender name for notification text
        srow = g.conn.execute(text("SELECT name FROM Users WHERE uid = :uid"), {"uid": int(sender_id)}).fetchone()
        sender_name = srow[0] if srow else "Someone"

        ins_msg = text(
            """
            INSERT INTO Messages (sender_id, receiver_id, content, is_read)
            VALUES (:sid, :rid, :content, FALSE)
            RETURNING message_id
            """
        )
        msg_row = g.conn.execute(
            ins_msg, {"sid": int(sender_id), "rid": int(receiver_id), "content": content}
        ).fetchone()
        message_id = msg_row[0]

        notif_text = f"New message from {sender_name}"
        ins_notif = text(
            """
            INSERT INTO Notifications (recipient_id, message_id, notification_text, is_seen)
            VALUES (:rid, :mid, :text, FALSE)
            """
        )
        g.conn.execute(ins_notif, {"rid": int(receiver_id), "mid": int(message_id), "text": notif_text})
        g.conn.commit()
    except Exception as e:
        return render_template('send_message.html', error=f'Error sending message: {e}'), 500

    return redirect(url_for('view_messages', uid=int(receiver_id)))


@app.route('/notifications/<int:uid>')
def view_notifications(uid: int):
    query = text(
        """
        SELECT notification_id, message_id, notification_text, created_at, is_seen
        FROM Notifications
        WHERE recipient_id = :uid
        ORDER BY created_at DESC, notification_id DESC
        """
    )
    cursor = g.conn.execute(query, {"uid": uid})
    notifications = rows_to_dicts(cursor)
    cursor.close()
    return render_template('notifications.html', uid=uid, notifications=notifications)


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        HOST, PORT = host, port
        print(f"running on {HOST}:{PORT}")
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()


