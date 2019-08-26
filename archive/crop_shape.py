import cv2
import numpy as np
import time
import os

# ============================================================
#                     Config
# ============================================================

CONTOUR_AREA = 700
image_path = '/home/agnext/Music/flc_without_ref/21.jpg'
result_image_folder = 'result'

# ============================================================

image = cv2.imread(image_path)
print(image.shape)
image = cv2.resize(image, (960, 540))
# image = cv2.addWeighted(image,2,image,0,0)
# image = cv2.addWeighted(image,1.8,image,0,0)
hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

green_low = np.array([45, 100, 50])
green_high = np.array([75, 255, 255])
curr_mask = cv2.inRange(hsv_img, green_low, green_high)
hsv_img[curr_mask > 0] = ([75, 255, 200])

# converting the HSV image to Gray in order to be able to apply contouring
RGB_again = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)
gray = cv2.cvtColor(RGB_again, cv2.COLOR_RGB2GRAY)
print(gray.shape)
# cv2.imshow('gray',gray)
ret, threshold = cv2.threshold(gray, 90, 255, 0)
# cv2.floodFill(threshold,)
# cv2.imshow('thresh',threshold)
_,contours,_ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
print(len(contours))

if not os.path.isdir(result_image_folder):
    os.mkdir(result_image_folder)

# ============================================================

i = 0
for c in contours:
    # epsilon = 0.01 * cv2.arcLength(c, True)
    # approx_polygon = cv2.approxPolyDP(c, epsilon, True)

    if cv2.contourArea(c) >= 400:
        # cv2.drawContours(image, [approx_polygon], -1, (0,255, 0), 3)
        # cv2.drawContours(mask, c, -1, (255,255,255), 1)
        x, y, w, h = cv2.boundingRect(c)
        print('Image {}: x: {}, y: {}, w: {}, h: {}'.format(i, x, y, w, h))
        mask = np.zeros((image.shape[0], image.shape[1], 1), np.uint8)
        # Uncomment below line for white background
        # mask.fill(255)

        cv2.fillConvexPoly(mask, c, 255, 1)
        # cv2.fillConvexPoly(mask, approx_polygon, 255, 1)
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=2)
        out = cv2.bitwise_and(image, image, mask=mask)

        out = out[y:y + h + 25, x:x + w + 25]
        outfile = result_image_folder + '/' + "image%d.png" % (i + 1)
        cv2.imwrite(outfile, out)
        i += 1

cv2.waitKey(0)
cv2.destroyAllWindows()