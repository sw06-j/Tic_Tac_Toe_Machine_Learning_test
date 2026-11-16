import sqlite3
import json

learning_file_name = "learning2"

def create_table():
    # 데이터베이스에 테이블을 생성합니다. 테이블이 이미 존재하면 아무 작업도 하지 않습니다.
    conn = sqlite3.connect(f'{learning_file_name}.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS json_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        array_json TEXT
    )
    ''')
    conn.commit()
    conn.close()

create_table()

def load_data():
    # 데이터베이스에서 배열 데이터를 불러와 리스트로 변환합니다.
    conn = sqlite3.connect(f'{learning_file_name}.db')
    cursor = conn.cursor()
    cursor.execute('SELECT array_json FROM json_table')
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return json.loads(result[0])
    else:
        return []
    


for i in load_data():
    print()
    for j in i:
        print(j)

input()