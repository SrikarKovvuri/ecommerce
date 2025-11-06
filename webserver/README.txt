Project: Ecommerce Listings & Messaging (Group 119)

Team Members and UNIs:
- Yiming (David) Xiong (yx2948)
- Srikar Kovvuri (srk2211)

PostgreSQL Account (UNI):
- yx2948

Web Application URL:
- http://<YOUR-VM-IP>:8111/

How to Run
1) Ensure Python 3 is used: python3 --version
2) Install dependencies (Flask, SQLAlchemy)
3) From the webserver/ folder, run: python3 server.py
4) Open http://localhost:8111/ (or http://<VM-IP>:8111/ on your VM)

Database Connection
The app connects using:
  postgresql://yx2948:113211@35.227.79.146/proj1part2

Implemented Routes/Features
- / (Homepage): Lists unsold products (Products JOIN Users), shows title, price, seller, and details link. Includes search bar.
- /product/<product_id>: Product details + seller contact; link to mark as sold.
- /add_product (GET/POST): Form to insert a new product (INSERT).
- /mark_sold/<product_id>: Updates product is_sold = TRUE (UPDATE); redirects home.
- /search?q=...: Case-insensitive keyword search in title/description (parameterized SELECT with ILIKE).
- /messages/<uid>: Inbox for a user (Messages JOIN Users for sender name), ordered by newest first.
- /send_message (GET/POST): Inserts a message and a corresponding notification using the inserted message_id; commits both.
- /notifications/<uid>: Lists notifications for a user (SELECT ordered by timestamp).

Most Interesting Pages
1) /send_message
   - Behavior: Accepts sender_id, receiver_id, and content; inserts into Messages and then into Notifications using the inserted message_id.
   - DB Ops: Uses RETURNING message_id to chain multi-table inserts in a single request and commits them together.
   - Why Interesting: Demonstrates transaction-style logic and coordinating inserts across related tables.

2) /search
   - Behavior: Keyword search across product title and description; displays matching unsold items with seller.
   - DB Ops: Parameterized query with ILIKE filters, JOIN (Products ↔ Users), and ordering.
   - Why Interesting: Shows safe text search using parameterized queries and combining results across relations.

Notes
- Orders and Services are present in the schema; the core web flows above focus on Products, Users, Messages, and Notifications per project requirements. These can be expanded as future work.


