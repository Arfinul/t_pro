import glob, shutil
import os
import cv2
import imutils, configparser, datetime
import classify, rotate, display_results


config = configparser.ConfigParser()
config.read('flc.conf')
root_folder = config.get('input_path', 'root_folder')
test_data_dir = root_folder + '/test_data'
test_data_backup_dir = root_folder + '/test_data_backup'

image_dir = '/1_images'
cropped_dir = '/2_cropped_images'


'''Segmentation of bunches from a frame has been performed by finding the difference between the first
   frame(white frame or background) and current frame.

'''


def segmentation_and_rotation(userId, sectionId):
    firstFrame = None
    count = 0
    user_dir = test_data_dir + '/u-' + userId + '/s-' + sectionId

    cropped_path = user_dir + cropped_dir
    input_images = user_dir + image_dir + '/*'

    for file in sorted(glob.glob(input_images)):
        uploaded_file_name = os.path.basename(os.path.normpath(file))
        datetime.datetime.now().time()
        command_to_copy = 'cp ' + file + ' ' + test_data_backup_dir + '/' + str(
            datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()) + '_' + userId + '_' + sectionId + '_' + uploaded_file_name
        os.system(command_to_copy)

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
    print("Total bunches = %d" % len(
        [name for name in os.listdir(cropped_path) if os.path.isfile(os.path.join(cropped_path, name))]))

    rotate.rotate_image(user_dir)

    print("Total rotated bunches = %d" % len(
        [name for name in os.listdir(cropped_path) if os.path.isfile(os.path.join(cropped_path, name))]))


'''classification of all images at a time it return only the fine and coarse count

'''


def flc_only(userId, sectionId):
    segmentation_and_rotation(userId, sectionId)
    os.chdir(root_folder)
    classify.create_test_list(userId, sectionId)
    print("Generating Fine Leaf count only ... wait !!!")
    classify.yolo_classify_full(userId, sectionId)
    lb_1, lb_2, lb_3, lbj_1, b_1, total = classify.find_each_class_count(userId, sectionId)
    #cc, fc = classify.count(userId, sectionId)
    shutil.rmtree(test_data_dir + '/u-' + userId + '/s-' + sectionId + '/')

    #r = glob.glob(input_images)
    #for i in r:
        #os.remove(i)

    return lb_1, lb_2, lb_3, lbj_1, b_1, total


'''classification of each image, it will create pdf report

'''


def flc_with_report(userId, sectionId):
    segmentation_and_rotation(userId, sectionId)
    os.chdir(root_folder)
    classify.create_test_list(userId, sectionId)
    print("Generating FLC on report ... wait !!!")
    classify.yolo_classify_full(userId, sectionId)
    print("classification Done")

    fc, cc = classify.yolo_classify_each_and_generate_report(userId, sectionId)
    print("Fine = ", fc, ", Coarse = ", cc)

    #os.system('rm ' + cropped_path + '/*')

    return fc, cc


# Runs for all full flow with one by one image result
def flc_with_report_without_filter(userId, sectionId):
    segmentation_and_rotation(userId, sectionId)
    os.chdir(root_folder)
    classify.create_test_list(userId, sectionId)

    r = glob.glob(input_images)
    for i in r:
        os.remove(i)

    classify.yolo_classify_one_by_one()
    display_results.merge_test_and_result_without_fil()
    display_results.make_files_list_without_r()
    display_results.merge_pdf_without_r()

# flc_only()
# cc, fc = flc_with_report()
# flc_with_report_without_filter()
# print("Fine = ", fc, ", Coarse = ", cc)
