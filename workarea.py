import sqlite3

DATABASE = 'canteen.db'

def add_users_with_roles():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Insert users with roles into the users table
    users_with_roles = [
        (0,"admin", "admin", 100),
        (1,"canteen_manager", "canteen manager", 100)
        (2,"manu", "user", 100),  
    ]

    cursor.executemany("INSERT INTO users (id , username, role, score) VALUES (?, ?, ?)", users_with_roles)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    add_users_with_roles()
