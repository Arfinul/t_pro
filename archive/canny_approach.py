import cv2
import os
import time
import imutils
import numpy as np

# ============================================================
#                     Hyper-parameters
# ============================================================

CONTRAST = 0
DEBUG = 0
DENOISING = 0
MEDIAN_BLUR = 0
BOUNDING_BOX = False
CONTOUR_AREA = 700
BILATERAL = 0

xz = 0
yz = xz
folder_path = './input/'
cropped_path = './2Aug_box/box1 -{} -{} -C({})/'.format(xz, CONTOUR_AREA, CONTRAST)
# Change Result path
result_image_folder = 'mask5'

if not os.path.isdir(result_image_folder):
    os.mkdir(result_image_folder)


# ============================================================

def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)

    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)

    # return the edged image
    return edged


# ============================================================


def extract(o_image, path, frame_count, img_name, category, xz=0, yz=0):
    print("\n==================== Image {}=================\n".format(frame_count))
    o_image = cv2.imread(o_image)
    # o_image = imutils.resize(o_image, 1000)
    # o_image = cv2.addWeighted(o_image,2,o_image,0,0)

    image = cv2.medianBlur(o_image, 3)
    output = auto_canny(image)
    output = cv2.dilate(output, None, iterations=3)
    thresh = cv2.threshold(output, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    _, contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    print(len(contours))

    if not os.path.exists(cropped_path):
        os.makedirs(cropped_path)

    o_img = o_image.copy()
    count = 1

    i = 0
    for c in contours:

        if cv2.contourArea(c) >= CONTOUR_AREA:

            epsilon = 0.01 * cv2.arcLength(c, True)
            approx_polygon = cv2.approxPolyDP(c, epsilon, True)
            x, y, w, h = cv2.boundingRect(c)
            roi = o_img[y - yz:y + h + yz, x - xz:x + w + xz]
            if BOUNDING_BOX: cv2.rectangle(o_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            mask = np.zeros((o_image.shape[0], o_image.shape[1], 1), np.uint8)
            # mask.fill(255)

            cv2.fillConvexPoly(mask, approx_polygon, 255, 1)
            # cv2.fillConvexPoly(mask, c, 255, 1)

            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.dilate(mask, kernel, iterations=2)
            out = cv2.bitwise_and(o_image, o_image, mask=mask)

            out = out[y:y + h, x:x + w]
            print(out.shape)
            out[out[:, :, 0] == 0] = 255
            out[out[:, :, 1] == 0] = 255
            out[out[:, :, 2] == 0] = 255
            outfile = result_image_folder + '/' + "image%d.png" % (i + 1)
            cv2.imwrite(outfile, out)
            i += 1

    if BOUNDING_BOX:
        crop_path = cropped_path + '{}_{}.jpg'.format(category, frame_count)
        # o_img = imutils.resize(o_img, width=500)
        cv2.imwrite(crop_path, o_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# ============================================================

start = time.time()
list_dir = os.listdir(folder_path)
print("Grains categories:", list_dir, '\n')
f_cnt = 0

for category in sorted(list_dir):

    crop_path = cropped_path
    file = folder_path + category + '/'
    crop_path = crop_path + category + '/'

    for image in sorted(os.listdir(file)):
        img_name = image
        image = os.path.join(file, image)
        path = crop_path + img_name.split('.')[0]
        crop_path = crop_path
        f_cnt += 1
        extract(image, path, f_cnt, img_name, category, xz, yz)

end = time.time()
print("Extraction Time:", end - start, 's')
print("Cropping Done!")