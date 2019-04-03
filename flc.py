import glob
import os
import cv2
import imutils, ConfigParser
import classify, rotate, display_results


config = ConfigParser.ConfigParser()
config.read('flc.conf')
root_folder = config.get('input_path', 'root_folder')
test_data_dir = root_folder + '/test_data'
input_images = test_data_dir + '/1_images/*'
cropped_path = test_data_dir + '/2_cropped_images'





# Runs in gcp server
def flc_only():
    print("Generating Fine Leaf count only ... wait !!!")
    firstFrame = None
    count = 0
    print(sorted(glob.glob(input_images)))
    for file in sorted(glob.glob(input_images)):
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

        # Find contoussrs
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        seg_c = 0
        for c in cnts:
            seg_c = seg_c + 1
            # if the contour is too small, ignore it

            if cv2.contourArea(c) < 500:  # args["min_area"]
                continue

            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
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

        # out.write(frame)  # Save video file

        count += 1
        # cv2.imshow('video', frame)
        # cv2.imshow('gray', thresh)
        # if cv2.waitKey(1) == 27:
        #     exit()

    # out.release()  # Save video file
    # cv2.destroyAllWindows()
    r = glob.glob(input_images)
    for i in r:
        os.remove(i)
    print("Total bunches = %d" % len(
        [name for name in os.listdir(cropped_path) if os.path.isfile(os.path.join(cropped_path, name))]))

    rotate.rotate_image()

    print("Total rotated bunches = %d" % len(
        [name for name in os.listdir(cropped_path) if os.path.isfile(os.path.join(cropped_path, name))]))

    os.chdir(root_folder)
    classify.create_test_list()
    classify.yolo_classify_full()
    os.system('rm ' + cropped_path + '/*')
    cc, fc = classify.count()

    r = glob.glob(input_images)
    for i in r:
        os.remove(i)

    # classify.yolo_classify_one_by_one()
    return cc, fc


def flc_with_report():
    print("Segmenting...")

    firstFrame = None
    count = 0
    for file in sorted(glob.glob(input_images)):
        frame = cv2.imread(file)
        print frame
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
            seg_c = seg_c + 1
            # if the contour is too small, ignore it

            if cv2.contourArea(c) < 500:  # args["min_area"]
                continue

            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
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

    rotate.rotate_image()

    print("Total rotated bunches = %d" % len(
        [name for name in os.listdir(cropped_path) if os.path.isfile(os.path.join(cropped_path, name))]))

    os.chdir(root_folder)
    classify.create_test_list()
    classify.yolo_classify_full()
    # cc, fc = classify.count()

    r = glob.glob(input_images)
    for i in r:
        os.remove(i)

    fc, cc = classify.trap_images_to_test_2()
    print("Fine = ", fc, ", Coarse = ", cc)

    os.system('rm ' + cropped_path + '/*')

    return fc, cc


# Runs for all full flow with one by one image result
def flc_with_report_without_filter():
    print("full flow")

    # fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Save video file
    # out = cv2.VideoWriter('out.avi', fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))  # Save video file

    firstFrame = None
    count = 0
    for file in sorted(glob.glob(input_images)):
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
            seg_c = seg_c + 1
            # if the contour is too small, ignore it

            if cv2.contourArea(c) < 800:  # args["min_area"]
                continue

            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
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

        # out.write(frame)  # Save video file

        count += 1
        # cv2.imshow('video', frame)
        # cv2.imshow('gray', thresh)
        # if cv2.waitKey(1) == 27:
        #     exit()

    # out.release()  # Save video file
    # cv2.destroyAllWindows()

    # r = glob.glob(image_path)
    # for i in r:
    #     os.remove(i)

    print("Total bunches = %d" % len(
        [name for name in os.listdir(cropped_path) if os.path.isfile(os.path.join(cropped_path, name))]))

    rotate.rotate_image()

    print("Total rotated bunches = %d" % len(
        [name for name in os.listdir(cropped_path) if os.path.isfile(os.path.join(cropped_path, name))]))

    os.chdir(root_folder)
    classify.create_test_list()
    # classify.yolo_classify_full()
    # cc, fc = classify.count()

    r = glob.glob(input_images)
    for i in r:
        os.remove(i)

    # print("Fine = ", fc, ", Coarse = ", cc)

    classify.yolo_classify_one_by_one()
    display_results.merge_test_and_result_without_fil()
    display_results.make_files_list_without_r()
    display_results.merge_pdf_without_r()
    # os.system('rm ' + cropped_path + '/*')

    # return cc, fc

# flc_only()
# cc, fc = flc_with_report()
# flc_with_report_without_filter()
# print("Fine = ", fc, ", Coarse = ", cc)
