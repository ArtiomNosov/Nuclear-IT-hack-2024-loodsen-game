import sqlite3
from datetime import datetime

def counting_activity(cursor, emp_id):
    cursor.execute('''
        SELECT value
        FROM Stat_empl 
        WHERE name = "tasks_done" AND empl_id = emp_id
    ''')

    done = cursor.fetchal()

    cursor.execute('''
        SELECT COUNT(*)
        FROM Tasks 
        WHERE empl_id = emp_id
        ''')

    general = cursor.fetchal()

    act = (done / general) * 100
    return act



def partic_comun(cursor, emp_id):
    res = 1

    cursor.execute('''
            SELECT value
            FROM Stat_empl
            WHERE name = "Number of messages from an employee" 
            AND empl_id = emp_id
        ''')

    empl_mes = cursor.fetchal()

    cursor.execute('''
                SELECT value
                FROM Stat_team 
                WHERE name = "The average number of messages per command" 
            ''')

    team_mes = cursor.fetchal()

    res = (empl_mes / team_mes) * 100
    return res


def involv_cod_rev(cursor, emp_id):
    involved = 1
    cursor.execute('''
                SELECT value
                FROM Stat_empl 
                WHERE name = "Number of employee reviews"
                 AND empl_id = emp_id
            ''')

    empl_involv = cursor.fetchal()

    cursor.execute('''
                    SELECT value
                    FROM Stat_team 
                    WHERE name = "The total number of revues per team" 
                ''')

    team_involv = cursor.fetchal()

    res = (empl_involv / team_involv) * 100
    return involved


def quality_of_work(cursor, emp_id):
    cursor.execute('''
        SELECT value
        FROM Stat_empl
        WHERE name = "The number of closed tasks without bugs" 
        AND empl_id = emp_id
    ''')

    without_bags = cursor.fetchal()

    cursor.execute('''
        SELECT value
        FROM Stat_empl
        WHERE name = "tasks_done" 
        AND empl_id = emp_id
        ''')

    general = cursor.fetchal()

    qual = (without_bags / general) * 100
    return qual

def quant_cours(cursor, emp_id):
    cursor.execute('''
           SELECT COUNT(CoursesEmployee.course_id) AS course_count
           FROM CoursesEmployee
           JOIN Course ON CoursesEmployee.course_id = Course.id
           WHERE CoursesEmployee.employee_id = empl_id
            ''')
    course_count = cursor.fetchal()
    return course_count

def counting_engagement(emp_id):
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MetricsEmployee (
            empl_id INTEGER,
            metric_id INTEGER,    
            PRIMARY KEY (empl_id, metric_id)
    );
    ''')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS MetricsTeam (
                team_id INTEGER,
                metric_id INTEGER, 
                PRIMARY KEY (team_id, metric_id)   
        );
        ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Employees (
            id INTEGER PRIMARY KEY,
            name VARCHAR(64) NOT NULL,
            team_id INTEGER NOT NULL,
            email VARCHAR(64), 
            interestings VARCHAR(256)    
        );
    ''')

    cursor.execute('''
                CREATE TABLE IF NOT EXISTS Stat_empl (
                empl_id INTEGER PRIMARY KEY,
                name VCHAR(64),
                value INTEGER,
                dt DATETIME   
            );
            ''')

    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Statl_team (
                    id INTEGER PRIMARY KEY,
                    name VCHAR(64),
                    dt DATETIME   
                );
                ''')
    cursor.execute('SELECT bal_koef FROM Metrics')
    koef_list = [row[0] for row in cursor.fetchall()]
    metric = (counting_activity(cursor, emp_id) * koef_list[0])

    metric += (partic_comun(cursor, emp_id) * koef_list[1])
    metric += (involv_cod_rev(cursor, emp_id) * koef_list[2])
    metric += (quality_of_work(cursor, emp_id) * koef_list[3])
    metric += (quant_cours(cursor, emp_id) * koef_list[4])
    conn.close()

    return metric

counting_engagement(0)

