import tkinter as tk
import sqlite3
import json
import copy
import random

learning_file_name1 = "learning_ai1"
learning_file_name2 = "learning_ai2"

def create_table(file_name):
    conn = sqlite3.connect(f'{file_name}.db')
    cursor = conn.cursor()
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS json_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        array_json TEXT
    )
    ''')
    conn.commit()
    conn.close()

def save_data(array_data, file_name):
    array_json = json.dumps(array_data)
    conn = sqlite3.connect(f'{file_name}.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO json_table (array_json) VALUES (?)', (array_json,))
    conn.commit()
    conn.close()

def load_data(file_name):
    conn = sqlite3.connect(f'{file_name}.db')
    cursor = conn.cursor()
    cursor.execute('SELECT array_json FROM json_table')
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return json.loads(result[0])
    else:
        return []

def delete_all_data(file_name):
    conn = sqlite3.connect(f'{file_name}.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM json_table')
    conn.commit()
    conn.close()

create_table(learning_file_name1)
create_table(learning_file_name2)

if len(load_data(learning_file_name1)) != 9:
    delete_all_data(learning_file_name1)
    save_data([[] for _ in range(9)], learning_file_name1)

if len(load_data(learning_file_name2)) != 9:
    delete_all_data(learning_file_name2)
    save_data([[] for _ in range(9)], learning_file_name2)

board = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]

score = [0, 0, 0]  # AI 1 (X), AI 2 (O), Draw

def check_winner():
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != ' ':
            return board[i][0]
    for j in range(3):
        if board[0][j] == board[1][j] == board[2][j] != ' ':
            return board[0][j]
    if board[0][0] == board[1][1] == board[2][2] != ' ' or board[0][2] == board[1][1] == board[2][0] != ' ':
        return board[1][1]
    return None

def check_draw():
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                return False
    return True

tree_level = -1
nodes_x = []
nodes_o = []

def update_ai_data(file_name, ai_nodes, reward):
    data = load_data(file_name)
    while len(data) < 9:
        data.append([])
    for node in ai_nodes:
        lvl = node[0]
        add_node = True
        for existing in data[lvl]:
            if existing[1] == node[1]:
                existing[4] += reward
                if node[2][0] not in existing[2]:
                    existing[2].append(node[2][0])
                add_node = False
                break
        if add_node:
            node[4] += reward
            data[lvl].append(node)
    delete_all_data(file_name)
    save_data(data, file_name)

def ai_move(player, file_name):
    global tree_level, nodes_x, nodes_o
    data = load_data(file_name)
    tree_level += 1
    before_board = copy.deepcopy(board)
    mark = 'X' if player == 'X' else 'O'

    void_list = []
    for x in range(3):
        for y in range(3):
            if board[x][y] == ' ':
                void_list.append([x, y])

    if tree_level < 4:
        drow_list = []
        if len(data) > tree_level:
            for i in data[tree_level]:
                if before_board in i[2]:
                    drow_list.append(i)

        if len(drow_list) < len(void_list):
            row, col = random.choice(void_list)
            for position in void_list:
                potential_board = copy.deepcopy(board)
                potential_board[position[0]][position[1]] = mark
                if potential_board not in [node[1] for node in drow_list]:
                    row, col = position
                    break
        else:
            select_drow = max(drow_list, key=lambda x: x[4])
            row = select_drow[3][0]
            col = select_drow[3][1]
    else:
        row, col = random.choice(void_list)

    board[row][col] = mark
    winner = check_winner()

    node = [tree_level, copy.deepcopy(board), [before_board], [row, col], 0, winner]
    if mark == 'X':
        nodes_x.append(node)
    else:
        nodes_o.append(node)

    update_board()

    if winner:
        if winner == 'X':
            score[0] += 1
            reward_x = 5
            reward_o = -(5 - tree_level // 2)
        else:
            score[1] += 1
            reward_x = -(5 - tree_level // 2)
            reward_o = 5
        update_ai_data(learning_file_name1, nodes_x, reward_x)
        update_ai_data(learning_file_name2, nodes_o, reward_o)
        nodes_x = []
        nodes_o = []
        reset_game()
        return True
    elif check_draw():
        score[2] += 1
        update_ai_data(learning_file_name1, nodes_x, 3)
        update_ai_data(learning_file_name2, nodes_o, 3)
        nodes_x = []
        nodes_o = []
        reset_game()
        return True

    return False

def play_game():
    while True:
        if ai_move('X', learning_file_name1):
            break
        if ai_move('O', learning_file_name2):
            break

def reset_game():
    global score, tree_level
    print_score.config(text=f"[score]\nAI 1 (X) : {score[0]}\nAI 2 (O) : {score[1]}\nDraw : {score[2]}")
    tree_level = -1
    for i in range(3):
        for j in range(3):
            board_buttons[i][j].config(text=' ', state='normal', relief='solid')  
            board[i][j] = ' '

def update_board():
    for i in range(3):
        for j in range(3):
            if board[i][j] == 'X':
                board_buttons[i][j].config(text=board[i][j], fg='red', relief='solid', activebackground='white')  
            elif board[i][j] == 'O':
                board_buttons[i][j].config(text=board[i][j], fg='blue', relief='solid', activebackground='white')  
            else:
                board_buttons[i][j].config(text=board[i][j], relief='solid', activebackground='white')

view = tk.Tk()
view.title("틱택토 머신러닝")
view.geometry("410x500-1-1")
view.configure(bg='white')
view.resizable(0, 0)

turn = -1

board_buttons = []

for i in range(3):
    row_buttons = []
    for j in range(3):
        button = tk.Button(view, relief='solid', text=" ", font=('맑은고딕', 30), padx=40, bg='white', activebackground='white', width=2, height=2,
                                 command=lambda row=i, col=j: play_game(), fg='black')
        button.grid(row=i, column=j)
        row_buttons.append(button)
    board_buttons.append(row_buttons)

print_score = tk.Label(view, text="[score]\nAI 1 (X) : 0\nAI 2 (O) : 0\nDraw : 0", bg="white", font=('맑은고딕', 15))
print_score.place(x=10, y=350)

play_button = tk.Button(view, text="한 판 진행", command=play_game, font=('맑은고딕', 15), bg='white')
play_button.place(x=150, y=450)

view.mainloop()
