import sqlite3

def setup_database():
    conn = sqlite3.connect('knowledge_base.db')
    cursor = conn.cursor()
    
   
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("SQLite veritabanı (knowledge_base.db) ve 'documents' tablosu başarıyla oluşturuldu.")

if __name__ == "__main__":
    setup_database()