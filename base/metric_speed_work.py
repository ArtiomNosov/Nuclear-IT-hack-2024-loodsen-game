import sqlite3
from datetime import datetime

# Connecting to the SQLite database
conn = sqlite3.connect('your_database.db')  # Link to the database path
cursor = conn.cursor()

# SQL query to get the number of completed tasks in the last month
cursor.execute('''
    SELECT COUNT(*) as completed_tasks
    FROM Tasks
    WHERE status = 'Completed' 
      AND time_end >= date('now', '-1 month')
      AND is_for_all = 1
''', )

# Getting the result
completed_tasks = cursor.fetchone()[0]

conn.close()

# Output the number of completed tasks
#print(f"Количество завершённых задач командой за последний месяц: {completed_tasks}")

