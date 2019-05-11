import cv2
import time
import argparse
import os
import imutils, configparser

import flc

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--output", dest='output', help="path to output video file")
parser.add_argument("-f", "--fps", dest='fps', type=int, default=50, help="FPS of output video")
parser.add_argument("-c", "--codec", dest='codec', type=str, default="MJPG", help="codec of output video")
parser.add_argument("-v", "--videocam", dest='videocam', type=int, default=0, help="number of video camara to use")
parser.add_argument("-l", "--learn", dest='learn', type=int, default=5,
                    help="learn time of background subtractor (in seconds)")
args_input = parser.parse_args()

config = configparser.ConfigParser()
config.read('flc.conf')
video_path = config.get('video_path', 'file')

root_folder = config.get('input_path', 'root_folder')
test_data_dir = root_folder + '/test_data'
cropped_path = test_data_dir + '/2_cropped_images'


def finding_contours(thresh_value):
    """finding countours"""

    try:
        #     thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        #     thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh_value.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

    except Exception as error:
        print(error)

    return cnts


def finding_right_contour(img, cnts, frame_counter, img_name):
    """finding the right contour"""

    seg_c = 0
    for c in cnts:
        seg_c = seg_c + 1
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < 800:  # args["min_area"]
            continue
        # compute the bounding box for the contour, draw it on the frame, and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        # cv2.imwrite("/home/arfin/Documents/GitHub/tea/darknet-master/results/frame%d.jpg" % count,
        #             frame)  # Save Frames
        if seg_c > 1:
            if (x != 0) & (y != 0) & ((x + w) != 1000) & ((y + h) != 562):
                crop_img = img[y:y + h, x:x + w]
                crop_img = cv2.addWeighted(crop_img, 1.8, crop_img, 0, 0)
                cv2.imwrite(os.path.join(img_name, '{}.jpg'.format(frame_counter)), crop_img)

        else:
            if (x != 0) & (y != 0) & ((x + w) != 1000) & ((y + h) != 562):
                crop_img = img[y:y + h, x:x + w]
                crop_img = cv2.addWeighted(crop_img, 1.8, crop_img, 0, 0)
                cv2.imwrite(os.path.join(img_name, '{}.jpg'.format(frame_counter)), crop_img)


def main():
    for file in os.listdir(video_path):
        if file.endswith(".MTS"):
            path = os.path.join(video_path, file)
            cap = cv2.VideoCapture(path)
            bgSubtractor = cv2.bgsegm.createBackgroundSubtractorMOG()
            # fouorcc = cv2.VideoWriter_fourcc(*args_input.codec)

            hasFrame, frame = cap.read()
            # vid_writer = cv2.VideoWriter(args_input.output, fouorcc, args_input.fps, (frame.shape[1], frame.shape[0])) # black frame init
            # vid_writer2 = cv2.VideoWriter("normal.avi", fouorcc, args_input.fps, (frame.shape[1], frame.shape[0])) #normal frame

            calibrateFlag = False
            initTime = time.time()
            calibratingText = "Segmenting....wait !!!"
            print(calibratingText)
            # calibratingTextsize = cv2.getTextSize(calibratingText, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]

            counter = 0
            while True:
                _, frame = cap.read()

                if calibrateFlag == False:
                    bgSubtractor.apply(frame, learningRate=0.5)
                    # calibratingTextX = int((frame.shape[1] - calibratingTextsize[0]) / 2)
                    # calibratingTextY = int((frame.shape[0] + calibratingTextsize[1]) / 2)
                    # cv2.putText(frame, calibratingText, (calibratingTextX, calibratingTextY), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    #             (0, 255, 0), 2)

                    # timeStr = "Time elapsed: {:.1f} s".format(time.time() - initTime)
                    # timeTextsize = cv2.getTextSize(timeStr, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
                    # timeTextX = int(frame.shape[1] - timeTextsize[0])
                    # timeTextY = int(frame.shape[0] - timeTextsize[1])
                    # cv2.putText(frame, timeStr, (timeTextX, timeTextY), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                else:
                    if counter % 4 == 0:
                        fgMask = bgSubtractor.apply(frame, learningRate=0.2)
                        img_fg = cv2.bitwise_and(frame, frame, mask=fgMask)
                        img_fg[img_fg == 0] = 255
                        # -------------------------------------------------------------------------#
                        cnts = finding_contours(fgMask)
                        img_name = cropped_path
                        finding_right_contour(img_fg, cnts, counter, img_name)
                        # -------------------------------------------------------------------------#
                        # cv2.imshow('BGSUB', img_fg)
                        # vid_writer.write(img_fg) # black blackground write
                        counter += 1
                        #print('current_frame: {}'.format(counter))

                    else:
                        counter += 1
                        #print('current_frame: {}'.format(counter))

                # cv2.imshow('Video', frame)
                # vid_writer2.write(frame)

                calibrateFlag = True if (time.time() - initTime > args_input.learn) else False

                # if (cv2.waitKey(1) & 0xFF == ord('q')):
                #     break
            # vid_writer.release()
            # vid_writer2.release()
            cap.release()
            cv2.destroyAllWindows()


if __name__ == '__main__':
    try:
        main()
    except:
        flc.flc_with_cropped_images()
