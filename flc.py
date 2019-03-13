import glob
import os

import cv2
import imutils

import classify, rotate, display_results


# Runs in gcp server
def flc_only():
    print("Generating Fine Leaf count only")
    print("Segmenting...")

    root_folder = '/home/arfin/Documents/GitHub/tea/Flc'

    image_path = '/home/arfin/Documents/GitHub/tea/Flc/test_data/1_images/*'

    cropped_path = '/home/arfin/Documents/GitHub/tea/Flc/test_data/2_cropped_images'

    # fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Save video file
    # out = cv2.VideoWriter('out.avi', fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))  # Save video file

    firstFrame = None
    count = 0
    for file in sorted(glob.glob(image_path)):
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
    r = glob.glob(image_path)
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

    r = glob.glob(image_path)
    for i in r:
        os.remove(i)

    # classify.yolo_classify_one_by_one()
    return cc, fc


# def flc_with_report():
#     print("Segmenting...")
#
#     root_folder = '/home/arfin/Documents/GitHub/tea/Flc'
#
#     image_path = '/home/arfin/Documents/GitHub/tea/Flc/test_data/1_images/*'
#
#     cropped_path = '/home/arfin/Documents/GitHub/tea/Flc/test_data/2_cropped_images'
#
#     firstFrame = None
#     count = 0
#     for file in sorted(glob.glob(image_path)):
#         frame = cv2.imread(file)
#         frame = cv2.addWeighted(frame, 2, frame, 0, 0)
#         frame = imutils.resize(frame, width=1000)
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         gray = cv2.GaussianBlur(gray, (21, 21), 0)  # blurring to smooth our images.
#
#         if firstFrame is None:  # assumption that the first frame of the video stream contains no motion and is a
#             # good example of what our background looks like
#             firstFrame = gray
#             continue
#
#         # compute the absolute difference between the current frame and
#         frameDelta = cv2.absdiff(firstFrame, gray)  # absolute value of their corresponding pixel intensity
#         # delta equal to background model minus current frame
#         thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[
#             1]  # reveal regions of the image that only
#         # have significant changes in pixel intensity values
#
#         # dilate the thresholded image to fill in holes, then find contours on thresholded image
#         thresh = cv2.dilate(thresh, None, iterations=2)  # size of foreground object increases
#
#         # Find contours
#         cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#         cnts = imutils.grab_contours(cnts)
#
#         seg_c = 0
#         for c in cnts:
#             seg_c = seg_c + 1
#             # if the contour is too small, ignore it
#
#             if cv2.contourArea(c) < 500:  # args["min_area"]
#                 continue
#
#             # compute the bounding box for the contour, draw it on the frame,
#             # and update the text
#             (x, y, w, h) = cv2.boundingRect(c)
#
#             if seg_c > 1:
#                 if (x != 0) & (y != 0) & ((x + w) != 1000) & ((y + h) != 562):
#                     # print(count, x, y, x + w, y + h, count, seg_c, w * h)
#                     #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
#                     crop_img = frame[y:y + h, x:x + w]
#                     cv2.imwrite(cropped_path + '/frame%d.%d_crop.jpg' % (count, seg_c), crop_img)  # Save Frames
#             else:
#                 if (x != 0) & (y != 0) & ((x + w) != 1000) & ((y + h) != 562):
#                     # print(count, x, y, x + w, y + h, count, w * h)
#                     #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
#                     crop_img = frame[y:y + h, x:x + w]
#                     cv2.imwrite(cropped_path + '/frame%d_crop.jpg' % count, crop_img)  # Save Frames
#
#         count += 1
#
#     r = glob.glob(image_path)
#     for i in r:
#         os.remove(i)
#     print("Total bunches = %d" % len(
#         [name for name in os.listdir(cropped_path) if os.path.isfile(os.path.join(cropped_path, name))]))
#
#     rotate.rotate_image()
#
#     print("Total rotated bunches = %d" % len(
#         [name for name in os.listdir(cropped_path) if os.path.isfile(os.path.join(cropped_path, name))]))
#
#     os.chdir(root_folder)
#     classify.create_test_list()
#     classify.yolo_classify_full()
#     cc, fc = classify.count()
#
#     r = glob.glob(image_path)
#     for i in r:
#         os.remove(i)
#
#     print("Fine = ", fc, ", Coarse = ", cc)
#
#     classify.trap_images_to_test()
#     os.system('rm ' + cropped_path + '/*')
#
#     classify.create_trapped_list()
#     classify.yolo_classify_trap_one_by_one()
#     display_results.merge_test_and_result()
#     display_results.make_files_list()
#     display_results.merge_pdf()
#
#     return cc, fc


def flc_with_report():
    print("Segmenting...")

    root_folder = '/home/arfin/Documents/GitHub/tea/Flc'

    image_path = '/home/arfin/Documents/GitHub/tea/Flc/test_data/1_images/*'

    cropped_path = '/home/arfin/Documents/GitHub/tea/Flc/test_data/2_cropped_images'

    firstFrame = None
    count = 0
    for file in sorted(glob.glob(image_path)):
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

    r = glob.glob(image_path)
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
    cc, fc = classify.count()

    r = glob.glob(image_path)
    for i in r:
        os.remove(i)

    print("Fine = ", fc, ", Coarse = ", cc)

    classify.trap_images_to_test()
    os.system('rm ' + cropped_path + '/*')

    return cc, fc


# Runs for all full flow with one by one image result
def one_and_all_testing():
    print("full flow")
    root_folder = '/home/arfin/Documents/GitHub/tea/Flc'  # mohali path
    # root_folder = '/home/agnext-kgp/Documents/tea/Flc'  # KGP GPU image path

    image_path = '/home/arfin/Documents/GitHub/tea/Flc/test_data/1_images/*'  # mohali image path
    # image_path = '/home/agnext-kgp/Documents/tea/Flc/test_data/1_images/*'  # KGP GPU image path

    cropped_path = '/home/arfin/Documents/GitHub/tea/Flc/test_data/2_cropped_images'  # mohali image path
    # cropped_path = '/home/agnext-kgp/Documents/tea/Flc/test_data/2_cropped_images'  # KGP GPU image path

    # fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Save video file
    # out = cv2.VideoWriter('out.avi', fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))  # Save video file

    firstFrame = None
    count = 0
    for file in sorted(glob.glob(image_path)):
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

            if cv2.contourArea(c) < 500:  # args["min_area"]
                continue

            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)

            if seg_c > 1:
                if (x != 0) & (y != 0) & ((x + w) != 1000) & ((y + h) != 562):
                    # print(count, x, y, x + w, y + h, count, seg_c, w * h)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    crop_img = frame[y:y + h, x:x + w]
                    cv2.imwrite(cropped_path + '/frame%d.%d_crop.jpg' % (count, seg_c), crop_img)  # Save Frames
            else:
                if (x != 0) & (y != 0) & ((x + w) != 1000) & ((y + h) != 562):
                    # print(count, x, y, x + w, y + h, count, w * h)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
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

    # rotate.rotate_image()

    print("Total rotated bunches = %d" % len(
        [name for name in os.listdir(cropped_path) if os.path.isfile(os.path.join(cropped_path, name))]))

    os.chdir(root_folder)
    classify.create_test_list()
    classify.yolo_classify_full()

    # os.system('rm ' + cropped_path + '/*')

    cc, fc = classify.count()

    # r = glob.glob(image_path)
    # for i in r:
    #     os.remove(i)

    classify.yolo_classify_one_by_one()
    display_results.merge_test_and_result()
    display_results.make_files_list()
    display_results.merge_pdf()

    return cc, fc


cc, fc = flc_with_report()
print("Fine = ", fc, ", Coarse = ", cc)
