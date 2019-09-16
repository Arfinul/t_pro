# importing libraries:
import os
import cv2
import time
import imutils


# defining functions:
def disp_img(img, img_name='img', img_hold=250):  # displaying images
    cv2.namedWindow(img_name, cv2.WINDOW_NORMAL)
    cv2.imshow(img_name, img)
    cv2.waitKey(img_hold)
    cv2.destroyAllWindows()


def img_pre(img):  # step2 - converting rgb to color and making mask out of it.
    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(img, (36, 25, 50), (72, 255, 255))
    return mask


def finding_contours(thresh_value):  # step2 - using mask find the actual image.
    cnts = cv2.findContours(thresh_value.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    return cnts


def identifying_contours(cnts, frame):  # step2 - creating a bounding box around it.
    cnts_counter = 0
    for idx in cnts:
        if cv2.contourArea(idx) <= 5000:
            cnts_counter += 1
            continue
        else:
            x, y, w, h = cv2.boundingRect(idx)
            cv2.rectangle(img=frame, pt1=(x, y), pt2=(x + w, y + h), color=(255, 255, 255), thickness=2)
            print('passed_contour --> x_cord: {}, y_cord: {}, height: {}, width: {}'.format(x, y, h, w))
            cnts_counter += 1


def main():  # main function
    video_dir = '/home/agnext/Music/flc_video/4_100.MTS'
    temp_dir = '/home/agnext/Music/flc_video/results'

    video = cv2.VideoCapture(video_dir)
    frame_counter = 0
    while video.isOpened():
        ret, frame = video.read()
        if ret:
            mask = img_pre(frame)
            cnts = finding_contours(mask)
            leaf_ls = identifying_contours(cnts, frame)
            temp_name = os.path.join(temp_dir, str(frame_counter) + '.png')
            cv2.imwrite(temp_name, frame)
            frame_counter += 1
        else:
            break

    video.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
