import cv2
import numpy as np
import time


# 사각형을 그리는 마우스 콜백
def mouse_callback(event, x, y, flags, param):
    global frame_show, s_x, s_y, e_x, e_y, mouse_pressed

    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_pressed = True
        s_x, s_y = x, y
        frame_show = np.copy(frame)

    elif event == cv2.EVENT_MOUSEMOVE:
        if mouse_pressed:
            frame_show = np.copy(frame)
            cv2.rectangle(frame_show, (s_x, s_y), (x, y), (0, 255, 0), 1)

    elif event == cv2.EVENT_LBUTTONUP:
        mouse_pressed = False
        e_x, e_y = x, y


# 추적기 함수
def tracking(input_bbox, input_tracker):
    global frame, frame_show, cap, frame_width, frame_height

    tracker = input_tracker()
    tracked = tracker.init(frame, input_bbox)

    position = cap.get(cv2.CAP_PROP_POS_FRAMES)

    bbox = input_bbox

    while True:
        t0 = time.time()
        has_frame, frame = cap.read()
        frame = cv2.resize(frame, (frame_width, frame_height))

        frame_show = np.copy(frame)
        position = cap.get(cv2.CAP_PROP_POS_FRAMES)

        if not has_frame:
            break

        # 프레임이 있으면 추적기 업데이트
        if has_frame:
            t0 = time.time()
            tracked, bbox = tracker.update(frame_show)
        # 추적기 업데이트해서 추적이 되었으면 해당 영역에 사각형 그리고 이미지 저장
        if tracked:
            x, y, w, h = [int(i) for i in bbox]
            # 검출된 이미지 영역 저장
            name_to_save = './data/'+str(int(position))+'.jpg'
            if w > h and (y + w) <= frame_height:
                cv2.imwrite(name_to_save, frame[y:y+w, x:x+w])
            elif w > h and (y + w) >= frame_height:
                cv2.imwrite(name_to_save, frame[y:frame_width, x:frame_width])
            elif w < h and (x + h) <= frame_width:
                cv2.imwrite(name_to_save, frame[y:y+h, x:x+h])
            elif w < h and (x + h) >= frame_width:
                cv2.imwrite(name_to_save, frame[y:y+h, x:frame_width])

            #cv2.imwrite(name_to_save, frame[y:y+h, x:x+w])
            # 검출된 영역에 사각형 그리기
            cv2.rectangle(frame_show, (x, y), (x + w, y + h), (0, 255, 0), 1)
            fps = 1 / (time.time() - t0)
            cv2.putText(frame_show, "Detected!!! FPS : %.0f" % fps, (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        else:
            break

        cv2.imshow(video_name, frame_show)

        # s를 누르면 중간에 빠져나옴
        k = cv2.waitKey(1)
        if k == ord('s'):
            break


# 여기서부터 메인함수 ---------------------------------------

video_name = input("동영상 이름 : ")
print("a키를 누르면 10프레임씩 이동, 마우스 드래그로 객체 추적 및 저장 (s를 눌러 실행)\ns키를 누르면 추적 중지")

# 한번에 스킵할 프레임 개수, default = 1920 * 1080
num_skip = 10
frame_width = 960
frame_height = 540

# 추적기 종류
# tracker = cv2.TrackerMedianFlow_create
tracker = cv2.TrackerKCF_create
# tracker = cv2.TrackerMIL_create
# tracker = cv2.TrackerTLD_create


cap = cv2.VideoCapture(video_name)
_, frame = cap.read()
frame = cv2.resize(frame, (frame_width, frame_height))

frame_show = np.copy(frame)

mouse_pressed = False
s_x = s_y = e_x = e_y = -1


cv2.namedWindow(video_name)
cv2.setMouseCallback(video_name, mouse_callback)

frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

while True:
    cv2.imshow(video_name, frame_show)
    k = cv2.waitKey(1)

    # a 누르면 num_skip 프레임 개수만큼 넘기기
    if k == ord('a'):
        position = cap.get(cv2.CAP_PROP_POS_FRAMES)
        # 스킵하려는데 영상 길이 넘어가면 반복문 종료
        if position + num_skip > frame_count:
            print("동영상이 끝났습니다 ~")
            break
        else:
            cap.set(cv2.CAP_PROP_POS_FRAMES, position + num_skip)
            _, frame = cap.read()
            frame = cv2.resize(frame, (frame_width, frame_height))
            frame_show = np.copy(frame)

    elif k == ord('s'):
        if s_y > e_y:
            s_y, e_y = e_y, s_y
        if s_x > e_x:
            s_x, e_x = e_x, s_x

        if e_y - s_y > 0 and e_x - s_x > 0:
            tracking((s_x, s_y, e_x - s_x, e_y - s_y), tracker)

    elif k == 27:
        break

cv2.destroyAllWindows()






