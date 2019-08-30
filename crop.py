import cv2
import numpy as np
import os, imutils
import tensorflow as tf
# ============================================================
#                     Config
# ============================================================

CONTOUR_AREA = 700


# ============================================================
def as_per_shape(image_path, frame_count, cropped_path):
    image = cv2.imread(image_path)
    image = imutils.resize(image, width=1000)
    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    green_low = np.array([45, 100, 50])
    green_high = np.array([75, 255, 255])
    curr_mask = cv2.inRange(hsv_img, green_low, green_high)
    hsv_img[curr_mask > 0] = ([75, 255, 200])

    # converting the HSV image to Gray in order to be able to apply contouring
    RGB_again = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)
    gray = cv2.cvtColor(RGB_again, cv2.COLOR_RGB2GRAY)
    # ret, threshold = cv2.threshold(gray, 120, 255, 0)
    ret, threshold = cv2.threshold(gray, 130, 255, cv2.THRESH_OTSU)
    _, contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # ============================================================

    first_image = -1
    i = 0
    for c in contours:
        if cv2.contourArea(c) >= CONTOUR_AREA:
            first_image += 1
            if first_image == 0:
                continue
            x, y, w, h = cv2.boundingRect(c)
            if (x != 0) & (y != 0) & ((x + w) != 1000) & ((y + h) != 562):
                print('Image {}: x: {}, y: {}, w: {}, h: {}'.format(i + 1, x, y, w, h))
                mask = np.zeros((image.shape[0], image.shape[1], 1), np.uint8)

                cv2.fillConvexPoly(mask, c, 255, 1)
                kernel = np.ones((6, 6), np.uint8)
                mask = cv2.dilate(mask, kernel, iterations=8)
                out = cv2.bitwise_and(image, image, mask=mask)
                out = out[y:y + h, x:x + w]
                out[np.where((out == [0, 0, 0]).all(axis=2))] = [255, 255, 255]
                # outfile = cropped_path + '/' + '/frame%d_%d.jpg' % (frame_count, (i+1))
                i += 1

                if (i > 0) & (i < 10):
                    outfile = cropped_path + '/' + '/frame%d_000%d.jpg' % (frame_count, i)
                if (i > 9) & (i < 100):
                    outfile = cropped_path + '/' + '/frame%d_00%d.jpg' % (frame_count, i)
                if (i > 99) & (i < 1000):
                    outfile = cropped_path + '/' + '/frame%d_0%d.jpg' % (frame_count, i)
                if (i > 999) & (i < 10000):
                    outfile = cropped_path + '/' + '/frame%d_%d.jpg' % (frame_count, i)


                out = cv2.addWeighted(out, 2, out, 0, 0)
                cv2.imwrite(outfile, out)


print(tf.Session(config=tf.ConfigProto(log_device_placement=True)))
