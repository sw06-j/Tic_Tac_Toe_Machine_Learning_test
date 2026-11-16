import tkinter as tk
import sqlite3
import json
import random

f_learning_name = "learning_f"
s_learning_name = "learning_s"

def create_table(file_name):
    # 데이터베이스에 테이블을 생성합니다. 테이블이 이미 존재하면 아무 작업도 하지 않습니다.
    conn = sqlite3.connect(f'{file_name}.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tree (
        level INT NOT NULL,
        board TEXT NOT NULL,
        drop_row INT,
        drop_col INT,
        reward INT DEFAULT 0
    )
    ''')
    conn.commit()
    conn.close()

def save_data(level, board_str, drop_row, drop_col, reward, file_name):
    conn = sqlite3.connect(f'{file_name}.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tree (level, board, drop_row, drop_col, reward) VALUES (?, ?, ?, ?, ?)",
        (level, board_str, drop_row, drop_col, reward)
    )
    conn.commit()
    conn.close()

def get_moves_for_board(board_str, file_name):
    conn = sqlite3.connect(f'{file_name}.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT drop_row, drop_col, reward FROM tree WHERE board = ? ORDER BY reward DESC",
        (board_str,)
    )
    result = cursor.fetchall()
    conn.close()
    return result

def update_or_insert_reward(level, board_str, drop_row, drop_col, reward, file_name):
    conn = sqlite3.connect(f'{file_name}.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT reward FROM tree WHERE board = ? AND drop_row = ? AND drop_col = ?",
        (board_str, drop_row, drop_col)
    )
    existing = cursor.fetchone()
    if existing is None:
        cursor.execute(
            "INSERT INTO tree (level, board, drop_row, drop_col, reward) VALUES (?, ?, ?, ?, ?)",
            (level, board_str, drop_row, drop_col, reward)
        )
    else:
        cursor.execute(
            "UPDATE tree SET reward = reward + ? WHERE board = ? AND drop_row = ? AND drop_col = ?",
            (reward, board_str, drop_row, drop_col)
        )
    conn.commit()
    conn.close()




# 테이블 생성
create_table(f_learning_name)
create_table(s_learning_name)

board = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]

score = [0, 0, 0]  # p1(X), p2(O), 무승부


def check_winner():
    # 가로
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != ' ':
            return board[i][0]
    # 세로
    for j in range(3):
        if board[0][j] == board[1][j] == board[2][j] != ' ':
            return board[0][j]
    # 대각선
    if board[0][0] == board[1][1] == board[2][2] != ' ' or board[0][
            2] == board[1][1] == board[2][0] != ' ':
        return board[1][1]
    if check_draw():
        return "Drow"
    return None

def check_draw():
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                return False
    return True

tree_level = 0
reset = 0
rewerd = 0
nodes = []
temp_save_f=[]
temp_save_s=[]

#================================================================
def f_ai_backpropagation(reward):  # 역전파
    global temp_save_f
    for level, board_str, drop_row, drop_col in temp_save_f:
        update_or_insert_reward(level, board_str, drop_row, drop_col, reward, f_learning_name)
    temp_save_f = []

def f_ai_drow():
    global tree_level, board, temp_save_f
    board_str = json.dumps(board)
    empty_cells = [(i, j) for i in range(3) for j in range(3) if board[i][j] == ' ']

    known_moves = get_moves_for_board(board_str, f_learning_name)
    known_coords = {(r, c) for r, c, _ in known_moves}
    unexplored = [cell for cell in empty_cells if cell not in known_coords]

    # 아직 탐색하지 않은 수가 있거나 최고 보상 수가 양수가 아니면 탐색
    best_known = next(((r, c, rew) for r, c, rew in known_moves if (r, c) in empty_cells), None)
    if unexplored and (best_known is None or best_known[2] <= 0):
        drop = random.choice(unexplored)
    elif best_known is not None:
        drop = (best_known[0], best_known[1])
    else:
        drop = random.choice(empty_cells)

    temp_save_f.append((tree_level, board_str, drop[0], drop[1]))
    return drop
#================================================================
def s_ai_backpropagation():# 역전파
    pass

def s_ai_drow():
    pass
#================================================================

turn = -1
f_reward = 0
s_reward = 0

def finish_if_game_over():
    global turn, tree_level, f_reward
    winner = check_winner()
    if not winner:
        return False

    if winner == 'X':
        score[0] += 1
        f_reward = -1
    elif winner == 'O':
        score[1] += 1
        f_reward = 1
    else:
        score[2] += 1
        f_reward = 0

    f_ai_backpropagation(f_reward)
    turn = -1
    tree_level = 0
    reset_game()
    return True

def put(row, col):
    global tree_level, board
    if board[row][col] != ' ':
        return

    tree_level += 1
    board[row][col] = 'X'
    update_board()

    if finish_if_game_over():
        return

    ai_drow = f_ai_drow()
    board[ai_drow[0]][ai_drow[1]] = 'O'
    update_board()

    finish_if_game_over()



def reset_game():
    global score, board
    print_score.config(
        text=f"[score]\nHuman : {score[0]}\nAI : {score[1]}\nDraw : {score[2]}"
    )
    #print(f"[점수]     p1:{score[0]}, p2:{score[1]}, 무승부:{score[2]}")
    for i in range(3):
        for j in range(3):
            board_buttons[i][j].config(text=' ',
                                       state='normal',
                                       relief='solid')
            board[i][j] = ' '


def update_board():
    for i in range(3):
        for j in range(3):
            if board[i][j] == 'X':
                board_buttons[i][j].config(text=board[i][j],
                                           fg='red',
                                           relief='solid',
                                           activebackground='white')
            elif board[i][j] == 'O':
                board_buttons[i][j].config(text=board[i][j],
                                           fg='blue',
                                           relief='solid',
                                           activebackground='white')
            else:
                board_buttons[i][j].config(
                    text=board[i][j], relief='solid',
                    activebackground='white')  # 버튼 초기 상태의 테두리 설정


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
        button = tk.Button(view,
                           relief='solid',
                           text=" ",
                           font=('맑은고딕', 30),
                           padx=40,
                           bg='white',
                           activebackground='white',
                           width=2,
                           height=2,
                           command=lambda row=i, col=j: put(row, col),
                           fg='black')
        button.grid(row=i, column=j)
        row_buttons.append(button)
    board_buttons.append(row_buttons)

print_score = tk.Label(view,
                       text="[score]\nHuman : 0\nAI : 0\nDraw : 0",
                       bg="white",
                       font=('맑은고딕', 15))
print_score.place(x=10, y=350)

view.mainloop()