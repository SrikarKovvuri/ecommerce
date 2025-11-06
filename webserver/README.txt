Project: Ecommerce Listings & Messaging (Group 119)

Team Members and UNIs:
- Yiming (David) Xiong (yx2948)
- Srikar Kovvuri (srk2211)

PostgreSQL Account (UNI):
- yx2948

Web Application URL:
- http://35.231.59.44:8111/

What we implemented from Part 1:
- Browse active listings on the homepage, including title, price, and seller name
- Product detail page with full attributes and seller contact info
- Create listing form that inserts into Products
- Mark listing as sold (updates Products.is_sold = TRUE)
- Text search over title and description (case-insensitive)
- User inbox page that shows received messages with sender names (join)
- Send message form that creates a message and an automatic notification for the receiver
- Notifications page listing all notifications for a user

What we did not implement from Part 1 and why:
- Real-time websocket messaging was omitted due to scope/time; we use simple form submits instead
- Semantic search beyond ILIKE was omitted due to scope; we use parameterized ILIKE filters
- Full user auth/account creation UI was not built; we operate directly with user ids to focus on SQL
- Fancy grid/category browsing UI was simplified to a basic list and a search bar
- Profile management (delete listings, manage categories) was not implemented to keep the app small
- Orders and Services UIs were not implemented in Part 3; schema remains and can be extended later

New or adjusted features vs Part 1:
- Minimal quick-access controls on the homepage to open an inbox or notifications by uid
- Emphasis on direct SQL (no ORM) and parameterized queries in every route

Two pages with the most interesting database operations:
1) /send_message (GET/POST)
   What it does: lets a user send a text message to another user. On submit, the server inserts a row into Messages and immediately inserts a corresponding row into Notifications for the receiver.
   How it uses the DB: on POST we run an INSERT into Messages with RETURNING message_id, then use that id to INSERT into Notifications in the same request and commit. Inputs are sender_id, receiver_id, and content, which become parameters in the SQL text to prevent injection.
   Why it’s interesting: demonstrates coordinating multi-table writes and using RETURNING to pass generated keys between queries without an ORM.

2) /search (GET)
   What it does: takes a query parameter q and returns unsold products whose title or description matches.
   How it uses the DB: runs a parameterized SELECT with ILIKE on Products.title and Products.description, joins Users to show seller names, filters out sold items, and orders by recency. The input q is bound to a :pattern parameter of the form %q%.
   Why it’s interesting: shows safe text search with parameters, a relational JOIN, and result ordering in a single query.

2) /search
   - Behavior: Keyword search across product title and description; displays matching unsold items with seller.
   - DB Ops: Parameterized query with ILIKE filters, JOIN (Products ↔ Users), and ordering.
   - Why Interesting: Shows safe text search using parameterized queries and combining results across relations.

Notes
- All DB access is via direct SQL strings executed through SQLAlchemy’s engine (no ORM). We commit after INSERT/UPDATE.
- The database is pre-populated with the Part 2 sample data so the app can be used immediately.


