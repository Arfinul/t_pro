import cv2
cap = cv2.VideoCapture(0)
i = 1
writer = cv2.VideoWriter("opencv_video.mp4", cv2.VideoWriter_fourcc(*'MP4V'), 35, (640, 480), True)
#writer = cv2.VideoWriter("opencv_video.mp4", cv2.VideoWriter_fourcc(*'MP4V'), 120, (1280, 720), True)
while True:
    ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (640, 480))
	#frame = cv2.resize(frame, (1280, 720))
        writer.write(frame)
        cv2.imshow("frame", frame)
        i += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        
cap.release()
cv2.destroyAllWindows()
writer.release()

