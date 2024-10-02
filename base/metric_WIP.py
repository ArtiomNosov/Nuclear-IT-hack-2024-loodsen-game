import sqlite3
from datetime import datetime

# Connecting to the SQLite database
conn = sqlite3.connect('your_database.db')  # Link to the database path
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Tasks (
        id INTEGER PRIMARY KEY,
        empl_id INTEGER NOT NULL,
        task_name TEXT NOT NULL,
        description TEXT,
        type TEXT,
        story_point INTEGER,
        time_start TIMESTAMP,
        time_end TIMESTAMP,
        status TEXT,
        is_for_all BOOLEAN
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Metrics (
        id INTEGER PRIMARY KEY,
        dt DATETIME,
        decription TEXT,
        value FLOAT,
        name VARCHAR(128) NOT NULL,
        bal_koef FLOAT
);
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Courses (
        id INTEGER PRIMARY KEY,
        name_of_course VARCHAR(16) NOT NULL,
        content text NOT NULL,
        frequency_of_use FLOAT,
        is_for_all BOOLEAN
);
''')

cursor.execute('''
        CREATE TABLE IF NOT EXISTS CoursesEmployee (
            empl_id INTEGER PRIMARY KEY,
            course_id INTEGER PRIMARY KEY,    
    );
    ''')

# Request for counting tasks with the status "In Progress"
cursor.execute('''
    SELECT COUNT(*) 
    FROM Tasks 
    WHERE status = "In Progress"
''')

# Getting the number of tasks "In Progress"
task_count = cursor.fetchone()[0]

cursor.execute('''
    INSERT INTO Metrics (dt, decription, value, name, bal_koef) 
    VALUES (?, ?, ?, ?, ?)
''', (datetime.now(), "Tasks In Progress", task_count, "In Progress", 1.0))

# Saving changes
conn.commit()

# Closing the connection
conn.close()

#print(f"Метрика обновлена: {task_count} задач со статусом 'In Progress'.")