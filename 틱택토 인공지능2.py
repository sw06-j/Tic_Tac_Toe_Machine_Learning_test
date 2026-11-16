import tkinter as tk
import sqlite3
#import json
import copy
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
        board VARCHAR(20) NOT NULL,
        drop_row INT,
        drop_col INT,
        reward INT DEFAULT 0
    )
    ''')
    
    conn.commit()
    conn.close()

def save_data(level,board,drop_pos,reward,file_name):
    conn = sqlite3.connect(f'{file_name}.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tree (level, board, drop_pos, reward) VALUES (?, ?, ?, ?)",
                   (level, board, drop_pos, reward))
    conn.commit()
    conn.close()

def load_all(file_name):
    # 데이터베이스에서 배열 데이터를 불러와 리스트로 변환합니다.
    conn = sqlite3.connect(f'{file_name}.db')
    cursor = conn.cursor()
    cursor.execute(f'''SELECT * FROM tree''')
    result = cursor.fetchall()
    conn.close()
    return result

def load_free(command,all,file_name):
    # 데이터베이스에서 배열 데이터를 불러와 리스트로 변환합니다.
    conn = sqlite3.connect(f'{file_name}.db')
    cursor = conn.cursor()
    cursor.execute(command)
    if all==1:
        result = cursor.fetchall()
    elif all==2:
        pass
    else:
        result = cursor.fetchone()
    
    conn.close()
    return result

def delete(board, drop_pos, file_name):
    conn = sqlite3.connect(f'{file_name}.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tree WHERE board = ? AND drop_pos = ?", (board, drop_pos))
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
def f_ai_backpropagation(reward):# 역전파
    global temp_save_f
    for i in temp_save_f:
        if 0 == len(load_free(f"SELECT * FROM tree WHERE board='{i[1]}' AND drop_row = {i[2]} AND drop_col = {i[3]}",1,f_learning_name)): # 존재하지 않으면
            save_data(i[0],i[1],i[2],i[3],[4]+reward)
        else: # 존재하면
            load_free(f"UPDATE tree SET reward = reward + ({reward}) WHERE board = '{i[1]}' AND drop_row = {i[2]} AND drop_col = {i[3]}",2,f_learning_name)
            
    temp_save_f = []

def f_ai_drow():
    global tree_level, board, temp_save_f
    #print(load_free(f"SELECT * FROM tree WHERE board='{str(board)}'",1,f_learning_name))

    if tree_level != len(load_free(f"SELECT * FROM tree WHERE board='{str(board)}'",1,f_learning_name)) and 0 < int((load_free(f'''SELECT reward FROM tree WHERE board='{str(board)}' ORDER BY reward''',0,f_learning_name))[0]):
        ran_list = []
        for i in range(9):
            for j in range(9):
                if board[i][j] == ' ':
                    ran_list.append((i,j))
        drop = random.shuffle(ran_list)
        temp_save_f.append([tree_level, board, drop[0], drop[1], 0])
    else:
        drop = load_free(((f'''SELECT drop_row, drop_col FROM tree WHERE board='{str(board)}' ORDER BY reward'''),1,f_learning_name)[0])
        temp_save_f.append([tree_level, board, drop[0], drop[1], 0])
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

def put(row, col):
    global score, reset, tree_level, nodes, rewerd, turn, board, f_reward, s_reward
    tree_level += 1

    # 수 두기
    '''
    if turn == -1:
        board[row][col] = 'X'
    elif turn == 1:
       board[row][col] = 'O'
    turn *= -1
    '''

    board[row][col] = 'X'

    ai_drow = f_ai_drow()#========여기
    board[ai_drow[0]][ai_drow[1]] = 'O'

    update_board()

    # 종료
    if check_winner(): 
        # 승자 점수 부여
        if check_winner()=='X':
            score[0] += 1
            f_rewerd = -1
        elif check_winner()=='O':
            score[1] += 1
            f_rewerd = 1
        else:
            score[2] += 1
            f_rewerd = 0
        f_ai_backpropagation(f_reward)
        
        turn = -1
        tree_level = 0
        reset_game()



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