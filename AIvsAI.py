import os
import random
import time
import cv2
import torch
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox
from playsound import playsound

ver = 4.0

# YOLOv5 모델 불러오기
model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s.pt', force_reload=True)


# 웹캠에서 영상을 읽어오기 위한 비디오 캡처 객체 생성
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))  # 코덱 설정
cap.set(cv2.CAP_PROP_FPS, 60)  # 프레임 속도 설정

# 기본 창 생성
window = tk.Tk()
window.title(f"사물인식 카메라(조대부고)_ver:{ver}")

# 창 크기 조절 비활성화
window.resizable(False, False)

reversal = -1
boxing = 1
texting = 1
accuracy = -1
stoping = -1

object_list = [] # 3개 리스트

fps = ''

def turn_reversal(): # 좌우 반전 함수
    global reversal
    reversal = reversal * -1

def turn_boxing(): # 박스 표시 여부 함수
    global boxing
    boxing = boxing*-1
    if boxing == 1:
        boxing_button["text"] = "테두리 숨김"
    else:
        boxing_button["text"] = "테두리 표시"

def turn_accuracy(): # 정확도 표시 여부
    global accuracy
    accuracy = accuracy*-1
    if accuracy == 1:
        accuracy_button["text"] = "정확도 표시"
    else:
        accuracy_button["text"] = "정확도 숨김"

def turn_texting(): # 텍스트 표시 여부 함수
    global texting
    texting = texting*-1

    if texting == 1:
        texting_button["text"] = "텍스트 숨김"
    else:
        texting_button["text"] = "텍스트 표시"


    if texting == 1: # 텍스트 표시 여부에 따른 정확도 표시 버튼 활성화 여부
        accuracy_button["state"] = "normal"
    else:
        accuracy_button["state"] = "disable"

def turn_stoping():
    global stoping
    stoping = stoping*-1

def all_clear(): # 전체 종료
    global reversal, boxing, texting, accuracy
    boxing = -1
    texting = -1
    accuracy = 1
    accuracy_button["state"] = "disable"





def exit_program(): # 지금 안씀
    if messagebox.askokcancel("닫기", "종료하시겠습니까?"):
        window.destroy()

# 메인 디스플레이
canvas = tk.Canvas(window, width=750, height=500)
canvas.pack()

#fps
fps_text = tk.Label(window, text=f"", font=('맑은 고딕', 20, "bold"))
fps_text.place(x=650,y=10)


# 인식된 사물 리스트 생성
object_text = tk.Label(text=f"")
object_text.pack()

# 좌우 반전 버튼 생성
reversal_button = tk.Button(window, text="좌우반전", command=turn_reversal, bg="gray88", overrelief="solid" , activebackground="gray", bd=3, relief='flat')
reversal_button.place(x=660, y=80)

# 테두리 버튼 생성
boxing_button = tk.Button(window, text="테두리 숨김", command=turn_boxing, bg="gray88", overrelief="solid" , activebackground="gray", bd=3, relief='flat')
boxing_button.place(x=660, y=120)

# 텍스트 버튼 생성
texting_button = tk.Button(window, text="텍스트 숨김", command=turn_texting, bg="gray88", overrelief="solid" , activebackground="gray", bd=3, relief='flat')
texting_button.place(x=660, y=160)

accuracy_button = tk.Button(window, text="정확도 숨김", command=turn_accuracy, bg="gray88", overrelief="solid" , activebackground="gray", bd=3, relief='flat')
accuracy_button.place(x=660, y=200)

all_button = tk.Button(window, text="전체 숨김", command=all_clear, bg="gray88", overrelief="solid" , activebackground="gray", bd=3, relief='flat')
all_button.place(x=660, y=240)

stoping_button = tk.Button(window, text="⏸️", command=turn_stoping, overrelief="solid" , activebackground="gray", bd=3, relief='flat', font=('맑은 고딕', 30))
stoping_button.place(x=660, y=300)


audio_file = "ttt.mp3"

# 프레임
def update_frame():
    global reversal, boxing, texting, accuracy, stoping

    if stoping == 1: # 일시 정지 명령
        stoping_button["text"] = "▶️"
        accuracy_button["state"] = "disable"
        texting_button["state"] = "disable"
        boxing_button["state"] = "disable"
        reversal_button["state"] = "disable"
        messagebox.showwarning("일시정지", "다시 실행 하시겠습니까?")
        stoping_button["text"] = "⏸️"
        accuracy_button["state"] = "normal"
        texting_button["state"] = "normal"
        boxing_button["state"] = "normal"
        reversal_button["state"] = "normal"
        stoping = -1

    start_time = time.time()

    # 영상 프레임 읽기
    ret, frame = cap.read()
    if not ret or frame is None:
        window.after(10, update_frame)
        return
    
    flipped_frame = cv2.flip(frame, 1) # 좌우 반전

    if reversal == 1: # 좌우 반전 여부 확인
        setting_frame = flipped_frame
    else:
        setting_frame = frame
    
    #rotated_frame = imutils.rotate(setting_frame, 45)  # 45도로 회전

    # 프레임 변환 및 객체 감지
    image = Image.fromarray(cv2.cvtColor(setting_frame, cv2.COLOR_BGR2RGB))
    results = model(image)

    # 객체 감지 결과 추출
    bboxes = results.xyxy[0].numpy()
    class_indices = bboxes[:, 5].astype(int)  # 클래스 인덱스 추출
    confidences = bboxes[:, 4]  # 신뢰도 추출
    class_names = [model.names[i] for i in class_indices]  # 클래스 이름 추출

    object_list = [] # 리스트 초기화

    ran1 = random.randrange(100,256)
    ran2 = random.randrange(100,256)
    ran3 = random.randrange(100,256)
    # 객체 감지 결과를 위한 반복문
    for bbox, class_name, confidence in zip(bboxes, class_names, confidences):

        color_b = 0
        color_g = 255
        color_r = 0

        if str(class_name) == "person":
            color_b = 0
            color_g = 0
            color_r = 255
        elif str(class_name) == "cell phone":
            color_b = 255
            color_g = 255
            color_r = 0
        elif str(class_name) == "cup":
            color_b = 255
            color_g = 0
            color_r = 255
        elif str(class_name) == "bottle":
            color_b = ran1
            color_g = ran2
            color_r = ran3

        x1, y1, x2, y2 = bbox[:4].astype(int)

        area = max(abs(x1 - x2) * abs(y1 - y2), 1)
        sound_size = min(max(int(100 / (area / 30)), 0), 100)
        try:
            playsound(audio_file, block=False)
        except Exception:
            pass

        if os.name == "posix":
            os.system(f"amixer set Master {sound_size}%")

        # 경계 상자 그리기
        if boxing == 1:
            cv2.rectangle(setting_frame, (x1, y1), (x2, y2), (color_b, color_g, color_r), 2)

        # 클래스 이름과 신뢰도 표시
        if texting == 1:
            acc = f": {confidence:.2f}"
            if accuracy == 1:
                acc = ''
            label = f'{class_name}{acc}'
            cv2.putText(setting_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (color_b, color_g, color_r), 2)

        object_list.append(class_name)
        object_list = list(dict.fromkeys(object_list))

    object_text.config(text=f"{object_list}", font=('맑은 고딕', 25), height=3) # 오브젝트 이름 리스트

    # OpenCV 이미지를 PIL 이미지로 변환
    img = Image.fromarray(cv2.cvtColor(setting_frame, cv2.COLOR_BGR2RGB))

    # 이미지를 Tkinter Canvas에 표시
    img_tk = ImageTk.PhotoImage(image=img)
    canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
    canvas.img_tk = img_tk  # 참조를 유지하기 위해 이미지 객체를 변수에 할당

    # 다음 프레임 업데이트를 위해 호출
    window.after(1, update_frame)


    end_time = time.time()

    elapsed_time = max(end_time - start_time, 1e-6)

    fps_text["text"] = f"FPS:({int(1/elapsed_time)+1})"

# 프로그램 시작 시 영상 업데이트 함수 호출
update_frame()

# Tkinter 이벤트 루프 시작
window.mainloop()

# 비디오 캡처 객체 및 창 해제
cap.release()
cv2.destroyAllWindows()

master = "1321C2C"
