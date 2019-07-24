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
def segmentation_and_rotation_without_white_image(userId, sectionId):
    DENOISING = False
    CONTOUR_AREA = 700
    frame_count = 0

    user_dir = test_data_dir + '/u-' + str(userId) + '/s-' + str(sectionId)
    cropped_path = user_dir + cropped_dir
    input_images = user_dir + image_dir + '/*'

    for file in sorted(glob.glob(input_images)):
        uploaded_file_name = os.path.basename(os.path.normpath(file))
        datetime.datetime.now().time()
        command_to_copy = 'cp ' + file + ' ' + test_data_backup_dir + '/' + str(
            datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()) + '_' + str(userId) + '_' + str(sectionId) + '_' + uploaded_file_name
        os.system(command_to_copy)
        frame_count += 1
        print("\n==================== Image {}=================\n".format(frame_count))
        orig_img = cv2.imread(file)
        orig_img = cv2.addWeighted(orig_img, 2, orig_img, 0, 0)
        frame = orig_img.copy()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)  # Change colorspace to HLS

        if DENOISING:
            frame = cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        thresh = cv2.dilate(thresh, None, iterations=3)
        _, contours, hier = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        count = 1

        for c in contours:
            if cv2.contourArea(c) >= CONTOUR_AREA:
                x, y, w, h = cv2.boundingRect(c)
                if (x != 0) & (y != 0) & (w > 40) & (h > 60):
                    # & ((x + w) != 960/3120)
                    print(x, y, w, h)
                    print(x, y, (x + w), (y + h))
                    roi = orig_img[y:y + h, x:x + w]

                    if 0 not in roi.shape:
                        print(
                        "[INFO]: Image {}: Shape: {} Area: ({}) Location: ({},{},{},{})...".format(count, roi.shape,
                                                                                                   cv2.contourArea(c),
                                                                                                   x,
                                                                                                   y, w, h))
                        if count < 10:
                            cv2.imwrite(cropped_path + '/frame_0%d.jpg' % (count), roi)  # % count,roi
                            count += 1
                        else:
                            cv2.imwrite(cropped_path + '/frame_%d.jpg' % (count), roi)  # % count,roi
                            count += 1

    r = glob.glob(input_images)
    for i in r:
        os.remove(i)
    print("Total bunches = %d" % len(
        [name for name in os.listdir(cropped_path) if os.path.isfile(os.path.join(cropped_path, name))]))

    rotate.rotate_image(user_dir)

    print("Total rotated bunches = %d" % len(
        [name for name in os.listdir(cropped_path) if os.path.isfile(os.path.join(cropped_path, name))]))

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
    # segmentation_and_rotation_without_white_image(userId, sectionId)
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
    #print(lb_1, lb_2, lb_3, lbj_1, b_1, total)
    return lb_1, lb_2, lb_3, lbj_1, b_1, total


'''classification of each image, it will create pdf report

'''


def flc_as_per_best_among_7_rotation_by_priotising_leaf_def(userId, sectionId):
    segmentation_and_rotation(userId, sectionId)
    # segmentation_and_rotation_without_white_image(userId, sectionId)
    os.chdir(root_folder)
    classify.create_test_list(userId, sectionId)
    print("Generating Fine Leaf count only ... wait !!!")
    classify.yolo_classify_full(userId, sectionId)
    lb_1, lb_2, lb_3, lbj_1, lbj_2, lbj_3, b_1, bj_1, l_1, l_2, l_3, total = classify.get_fine_count_as_per_best_among_7_rotation_by_priotising_leaf_def(userId, sectionId)

    shutil.rmtree(test_data_dir + '/u-' + userId + '/s-' + sectionId + '/')

    #r = glob.glob(input_images)
    #for i in r:
        #os.remove(i)

    return lb_1, lb_2, lb_3, lbj_1, lbj_2, lbj_3, b_1, bj_1, l_1, l_2, l_3, total



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

def flc_with_report_as_per_best_among_7_rotation_by_priotising_leaf_def(userId, sectionId):
    segmentation_and_rotation(userId, sectionId)
    os.chdir(root_folder)
    classify.create_test_list(userId, sectionId)
    print("Generating FLC on report ... wait !!!")
    classify.yolo_classify_full(userId, sectionId)
    print("classification Done")

    fc, cc = classify.yolo_classify_each_and_generate_report_as_per_best_among_7_rotation_by_priotising_leaf_def(userId, sectionId)
    print("Fine = ", fc, ", Coarse = ", cc)

    shutil.rmtree(test_data_dir + '/u-' + userId + '/s-' + sectionId + '/')

    #os.system('rm ' + cropped_path + '/*')

    return fc, cc


# Runs for all full flow with one by one image result
def flc_with_report_without_filter(userId, sectionId):
    rotation(userId, sectionId)
    os.chdir(root_folder)
    classify.create_test_list(userId, sectionId)
    #r = glob.glob(input_images)
    #for i in r:
       # os.remove(i)
    classify.yolo_classify_one_by_one(userId, sectionId)
    display_results.merge_test_and_result_without_fil(userId, sectionId)
    display_results.make_files_list_without_r(userId, sectionId)
    display_results.merge_pdf_without_r(userId, sectionId)
    display_results.final_report_pdf(userId, sectionId)
    shutil.rmtree(test_data_dir + '/u-' + userId + '/s-' + sectionId + '/')


def rotation(userId, sectionId):
    firstFrame = None
    count = 0
    user_dir = test_data_dir + '/u-' + userId + '/s-' + sectionId

    cropped_path = user_dir + cropped_dir
    input_images = user_dir + image_dir + '/*'

    print("Total bunches = %d" % len(
        [name for name in os.listdir(cropped_path) if os.path.isfile(os.path.join(cropped_path, name))]))

    rotate.rotate_image(user_dir)

    print("Total rotated bunches = %d" % len(
        [name for name in os.listdir(cropped_path) if os.path.isfile(os.path.join(cropped_path, name))]))



def flc_with_report_for_cropped(userId, sectionId):
    rotation(userId, sectionId)
    os.chdir(root_folder)
    classify.create_test_list(userId, sectionId)
    print("Generating FLC on report ... wait !!!")
    classify.yolo_classify_full(userId, sectionId)
    print("classification Done")

    fc, cc = classify.yolo_classify_each_and_generate_report(userId, sectionId)
    #print("Fine = ", fc, ", Coarse = ", cc)
    shutil.rmtree(test_data_dir + '/u-' + userId + '/s-' + sectionId + '/')

    #os.system('rm ' + cropped_path + '/*')

    return fc, cc

# flc_only()
# cc, fc = flc_with_report()
#flc_with_report_without_filter(userId='salil', sectionId='1')
# print("Fine = ", fc, ", Coarse = ", cc)
#flc_with_report_for_cropped(userId='salil', sectionId='1')
# flc_only(userId='salil', sectionId='3')