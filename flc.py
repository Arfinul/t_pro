import glob
import os
import cv2
import imutils, configparser, datetime
import classify, rotate, display_results
import logging, time

#logging.basicConfig(filename='test.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

config = configparser.ConfigParser()
config.read('flc.conf')
video_path = config.get('video_path', 'file')
root_folder = config.get('input_path', 'root_folder')
test_data_dir = root_folder + '/test_data'
input_images = test_data_dir + '/1_images/*'
cropped_path = test_data_dir + '/2_cropped_images'

'''Segmentation of bunches from a frame has been performed by finding the difference between the first
   frame(white frame or background) and current frame.

'''


def segmentation_and_rotation():
    firstFrame = None
    count = 0
    for file in sorted(glob.glob(input_images)):
        uploaded_file_name = os.path.basename(os.path.normpath(file))
        datetime.datetime.now().time()
        command_to_copy = 'cp ' + file + ' ' + root_folder + '/test_data_backup/' + str(
            datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()) + '_' + uploaded_file_name
        os.system(command_to_copy)

        # command_to_copy = 'cp ' + file + ' /home/agnext/Music/flc/test_data_backup/' + str(
        # datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()) + '_' + uploaded_file_name
        # os.system(command_to_copy)

        frame = cv2.imread(file)
        frame = cv2.addWeighted(frame, 2, frame, 0, 0)
        frame = imutils.resize(frame, width=1000)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)  # blurring to smooth our images.

        if firstFrame is None:  # assumption that the first frame of the video stream contains no motion and is a
            # good example of what our background looks like
            firstFrame = gray
            continue

        # compute the absolute difference between the current frame and
        frameDelta = cv2.absdiff(firstFrame, gray)  # absolute value of their corresponding pixel intensity
        # delta equal to background model minus current frame
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[
            1]  # reveal regions of the image that only
        # have significant changes in pixel intensity values

        # dilate the thresholded image to fill in holes, then find contours on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)  # size of foreground object increases

        # Find contours
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        seg_c = 0
        for c in cnts:
            seg_c = seg_c + 1  # if the contour is too small, ignore it
            if cv2.contourArea(c) < config.getint('segmentation', 'ignore_contour_area'):
                continue

            # compute the bounding box for the contour, draw it on the frame, and update the text
            (x, y, w, h) = cv2.boundingRect(c)

            if seg_c > 1:
                if (x != 0) & (y != 0) & ((x + w) != 1000) & ((y + h) != 562):
                    # print(count, x, y, x + w, y + h, count, seg_c, w * h)
                    # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    crop_img = frame[y:y + h, x:x + w]
                    cv2.imwrite(cropped_path + '/frame%d.%d_crop.jpg' % (count, seg_c), crop_img)  # Save Frames
            else:
                if (x != 0) & (y != 0) & ((x + w) != 1000) & ((y + h) != 562):
                    # print(count, x, y, x + w, y + h, count, w * h)
                    # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    crop_img = frame[y:y + h, x:x + w]
                    cv2.imwrite(cropped_path + '/frame%d_crop.jpg' % count, crop_img)  # Save Frames

        count += 1

    r = glob.glob(input_images)
    for i in r:
        os.remove(i)
    logging.debug("Total bunches = %d" % len(
        [name for name in os.listdir(cropped_path) if os.path.isfile(os.path.join(cropped_path, name))]))

    rotate.rotate_image()

    logging.debug("Total rotated bunches = %d" % len(
        [name for name in os.listdir(cropped_path) if os.path.isfile(os.path.join(cropped_path, name))]))


def video_segmentation():

    # cap = cv2.VideoCapture('/home/chiranjeevi/Pictures/tea/flc/test_data/1_images/input.mp4')
    cap = cv2.VideoCapture(video_path)
    firstFrame = None
    count = 0
    frame_count = 0

    while 1:
        ret, frame = cap.read()

        if frame_count % 4 == 0:
            if ret:
                frame = cv2.addWeighted(frame, 1.8, frame, 0, 0)
                frame = imutils.resize(frame, width=1000)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)  # blurring to smooth our images.

                if firstFrame is None:
                    # assumption that the first frame of the video stream contains no motion and is a
                    # good example of what our background looks like
                    firstFrame = gray
                    continue

                # compute the absolute difference between the current frame and
                frameDelta = cv2.absdiff(firstFrame, gray)  # absolute value of their corresponding pixel intensity
                # delta equal to background model minus current frame
                thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[
                    1]  # reveal regions of the image that only
                # have significant changes in pixel intensity values

                # dilate the thresholded image to fill in holes, then find contours on thresholded image
                thresh = cv2.dilate(thresh, None, iterations=2)  # size of foreground object increases

                # Find contours
                cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)

                seg_c = 0
                for c in cnts:
                    seg_c = seg_c + 1
                    # if the contour is too small, ignore it
                    if cv2.contourArea(c) < 800:  # args["min_area"]
                        continue
                    # compute the bounding box for the contour, draw it on the frame,
                    # and update the text
                    (x, y, w, h) = cv2.boundingRect(c)
                    # cv2.imwrite("/home/arfin/Documents/GitHub/tea/darknet-master/results/frame%d.jpg" % count,
                    #             frame)  # Save Frames
                    if seg_c > 1:
                        if (x != 0) & (y != 0) & ((x + w) != 1000) & ((y + h) != 562):
                            #logging.debug(count, x, y, x + w, y + h, count, seg_c, w * h)
                            print(count, x, y, x + w, y + h, count, seg_c, w * h)
                            # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            crop_img = frame[y:y + h, x:x + w]
                            cv2.imwrite(cropped_path + '/frame%d.%d_crop.jpg' % (count, seg_c), crop_img)  # Save Frames
                            # cv2.imwrite(
                            #     "/home/document/darknet-master-GCP/test_data/cropped_images/frame%d.%d_crop.jpg" % (
                            #         count, seg_c), crop_img)  # Save Frames gcp path
                    else:
                        if (x != 0) & (y != 0) & ((x + w) != 1000) & ((y + h) != 562):
                            #logging.debug(count, x, y, x + w, y + h, count, w * h)
                            print(count, x, y, x + w, y + h, count, w * h)
                            # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            crop_img = frame[y:y + h, x:x + w]
                            cv2.imwrite(
                                cropped_path + '/frame%d_crop.jpg' % count,
                                crop_img)  # Save Frames
                            # cv2.imwrite(
                            #     "/home/document/darknet-master-GCP/test_data/cropped_images/frame%d_crop.jpg" % count,
                            #     crop_img)  # Save Frames gcp path

                # out.write(frame)  # Save video file
                count += 1
                cv2.imshow('video', frame)
                if cv2.waitKey(33) == 27:
                    exit()
            else:
                break
        frame_count += 1
    cap.release()
    # out.release()  # Save video file
    cv2.destroyAllWindows()


'''classification of all images at a time it return only the fine and coarse count

'''


def flc_only():
    segmentation_and_rotation()
    os.chdir(root_folder)
    classify.create_test_list()
    logging.debug("Generating Fine Leaf count only ... wait !!!")
    classify.yolo_classify_full()

    os.system('rm ' + cropped_path + '/*')
    cc, fc = classify.count()

    r = glob.glob(input_images)
    for i in r:
        os.remove(i)

    return cc, fc


'''classification of each image, it will create pdf report

'''


def flc_with_report():
    segmentation_and_rotation()
    os.chdir(root_folder)
    classify.create_test_list()
    logging.debug("Generating FLC on report ... wait !!!")
    classify.yolo_classify_full()

    r = glob.glob(input_images)
    for i in r:
        os.remove(i)

    fc, cc = classify.yolo_classify_each_and_generate_report()
    logging.debug("Fine = ", fc, ", Coarse = ", cc)

    os.system('rm ' + cropped_path + '/*')

    return fc, cc


# Runs for all full flow with one by one image result
def flc_with_cropped_images():
    print("Total bunches = %d" % len(
        [name for name in os.listdir(cropped_path) if os.path.isfile(os.path.join(cropped_path, name))]))

    rotate.rotate_image()

    print("Total rotated bunches = %d" % len(
        [name for name in os.listdir(cropped_path) if os.path.isfile(os.path.join(cropped_path, name))]))

    os.chdir(root_folder)
    classify.create_test_list()
    print("Generating FLC on report ... wait !!!")
    classify.yolo_classify_full()
    cc, fc = classify.count()
    print("Fine = ", fc, ", Coarse = ", cc)
    # r = glob.glob(input_images)
    # for i in r:
    #     os.remove(i)

    fc1, cc1 = classify.yolo_classify_each_and_generate_report()
    os.system('rm ' + cropped_path + '/*')
    # os.system('rm ' + cropped_path + '/*')
    print("Fine = ", fc1, ", Coarse = ", cc1)
    #return fc1, cc1


# flc_only()

# # flc_with_report_without_filter()
# print("Fine = ", fc, ", Coarse = ", cc)
# video_segmentation()
# flc_with_cropped_images()
