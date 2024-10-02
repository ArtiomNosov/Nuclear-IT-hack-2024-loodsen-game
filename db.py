import sqlite3

def convert_to_binary_data(filename):
    with open(filename, 'rb') as file:
        blob_data = file.read()
    return blob_data


def insert_product(id,name,cost,amount,art,created,description,updated,img):
    connection = sqlite3.connect('db.sqlite3')
    cursor = connection.cursor()
    insert_prompt = """INSERT INTO base_product (id,name,cost,amount,art, created, description, updated, img) values(?,?,?,?,?,?,?,?,?)"""
    product_photo = convert_to_binary_data(img)
    data_tuple = (id,name,cost,amount,art,created,description,updated,product_photo)
    cursor.execute(insert_prompt, data_tuple)
    connection.commit()
    cursor.close()

"""connection = sqlite3.connect('db.sqlite3')
cursor = connection.cursor()
cursor.execute(CREATE TABLE IF NOT EXISTS base_product(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    cost INTEGER,
    amount INTEGER,
    art DECIMAL,
    created DATETIME,
    description TEXT NOT NULL,
    updated DATETIME))
connection.close()"""
insert_product(1,"Толстовка",200,15,243295,"27.09.2024","Яркая толстовка в стиле лоции!","01.10.2024","static/images/hoodie.jpg")
                                