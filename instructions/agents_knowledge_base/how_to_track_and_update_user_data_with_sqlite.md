# How to Track and Update User Data with SQLite

You can use SQLite to track user interactions, update user details, and log knowledge gaps from agent conversations.

## Example: Inserting and Updating Visitor Data

```python
import sqlite3

def db_insert_visitor(ip, user_agent, location_desc, timezone, isp, msg):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            INSERT INTO visitors (ip, user_agent, location_desc, timezone, isp, raw_msg)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ip, user_agent, location_desc, timezone, isp, msg))
        conn.commit()

def db_update_visitor_details(ip, name, email, notes):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            UPDATE visitors
            SET name = ?, email = ?, notes = ?
            WHERE ip = ? AND id = (SELECT MAX(id) FROM visitors WHERE ip = ?)
        ''', (name, email, notes, ip, ip))
        conn.commit()
```
