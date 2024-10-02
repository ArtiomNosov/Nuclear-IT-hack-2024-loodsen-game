import sqlite3
from datetime import datetime

# Подключение к базе данных SQLite
conn = sqlite3.connect('your_database.db')  # Замените на путь к вашей базе данных
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
CREATE TABLE `Metrics` (
  `id` int PRIMARY KEY,
  `dt` datetime,
  `decription` text,
  `value` float,
  `name` varchar(128) NOT NULL,
  `bal_koef` float
);
''')

# Запрос для подсчета задач со статусом "In Progress"
cursor.execute('''
    SELECT COUNT(*) 
    FROM Tasks 
    WHERE status = "In Progress"
''')

# Получаем количество задач "In Progress"
task_count = cursor.fetchone()[0]

# Вставляем данные в таблицу Metrics
cursor.execute('''
    INSERT INTO Metrics (dt, decription, value, name, bal_koef) 
    VALUES (?, ?, ?, ?, ?)
''', (datetime.now(), "Tasks In Progress", task_count, "In Progress", 1.0))

# Сохранение изменений
conn.commit()

# Закрытие соединения
conn.close()

print(f"Метрика обновлена: {task_count} задач со статусом 'In Progress'.")