import sqlite3

DATABASE_NAME = 'geofilm.db'
conn = sqlite3.connect(DATABASE_NAME)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

def create_db():
    with conn:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                user_id INTEGER UNIQUE NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS category(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS kino(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                janr TEXT NOT NULL,
                category_id INTEGER,
                yil INTEGER,
                age TEXT NOT NULL,
                rating TEXT NOT NULL,
                video TEXT,
                FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE CASCADE
            )
        """)
        cur.execute("""
             CREATE TABLE IF NOT EXISTS admin(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER
            )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS channel_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER NOT NULL,
            channel_url TEXT NOT NULL
        )
        """)
        
        
        

def add_channel(channel_id, url):
    try:
        cur.execute("INSERT OR IGNORE INTO channel_info(channel_id, channel_url) VALUES (?, ?)", (channel_id, url))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при добавлении канала: {e}")

def get_channel_info():
    cur.execute("SELECT channel_id, channel_url FROM channel_info")
    result = cur.fetchall()  # Fetch all rows
    return result

def del_channel(id):
    cur.execute("Delete  from channel_info Where id =?",(id))
    conn.commit


def is_admin(user_id):
    cur.execute("SELECT * FROM admin WHERE user_id = ?", (user_id,))
    admin = cur.fetchone()
    return admin is not None

def is_user_registered(user_id):
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cur.fetchone() is not None

# Функция для регистрации пользователя
def register_user(user_id, username):
    cur.execute("INSERT INTO users(name, user_id) VALUES (?, ?)", ( username, user_id))
    conn.commit()

def get_all_categories():
    cur.execute("SELECT * FROM category")
    rows = cur.fetchall()
    return [dict(row) for row in rows] if rows else []

def get_c_id_by_name(name):
    cur.execute("SELECT id FROM category WHERE name=?", (name,))
    row = cur.fetchone()
    return row['id'] if row else None

def search_kino_by_id(kino_id):
    cur.execute("SELECT * FROM kino WHERE id=?", (kino_id,))
    result = cur.fetchone()
    if result:
        return {
            "id": result["id"],
            "name": result["name"],
            "janr": result["janr"],
            "category_id": result["category_id"],
            "video": result["video"],
            "yil": result["yil"],
            "age": result["age"],
            "rating": result["rating"],
        }
    return None

def search_kino_by_name(kino_name):
    cur.execute("SELECT * FROM kino WHERE name=?", (kino_name,))
    result = cur.fetchone()
    if result:
        return {
            "id": result["id"],
            "name": result["name"],
            "janr": result["janr"],
            "category_id": result["category_id"],
            "video": result["video"],
            "yil": result["yil"],
            "age": result["age"],
            "rating": result["rating"],
        }
    return None

def add_new_kino(name, janr, category_id, video, yil, age, rating):
    cur.execute(
        "INSERT INTO kino (name, janr, category_id, video, yil, age, rating) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (name, janr, category_id, video, yil, age, rating)
    )
    conn.commit()


def get_movies_by_category(category_name):
    # Находим ID категории
    cur.execute("SELECT id FROM category WHERE name = ?", (category_name,))
    category_id = cur.fetchone()

    if not category_id:  # Если категории нет
        return []

    # Получаем фильмы этой категории
    cur.execute("SELECT name FROM kino WHERE category_id = ?", (category_id[0],))
    movies = cur.fetchall()
    return [{'name': row['name']} for row in movies] if movies else []
    
    
def get_users(limit):
    cur.execute("SELECT user_id FROM users LIMIT ?", (limit,))
    rows = cur.fetchall()
    return [row['user_id'] for row in rows]

def del_kino_from_id(id):
    cur.execute("Delete From kino where id = ?",(id,))
    conn.commit()
    