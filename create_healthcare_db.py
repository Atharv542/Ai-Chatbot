import sqlite3

# Connect to (or create) a database
conn = sqlite3.connect("healthcare.db")
cursor = conn.cursor()

# Create a table for health-related Q&A
cursor.execute("""
CREATE TABLE IF NOT EXISTS healthcare (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL
)
""")

# Insert sample data
sample_data = [
    ("how to prevent dengue", "Use mosquito repellents, wear full sleeves, and avoid stagnant water."),
    ("how to improve immunity", "Eat healthy, exercise regularly, sleep well, and manage stress."),
    ("symptoms of fever", "Common symptoms of fever include high temperature, chills, sweating, and headache."),
    ("how to treat headache", "You can treat headaches with rest, hydration, and over-the-counter medication."),
    ("how much water should I drink", "Generally, you should drink about 8 glasses (2 liters) of water per day."),
]

cursor.executemany("INSERT INTO healthcare (question, answer) VALUES (?, ?)", sample_data)

conn.commit()
conn.close()
