import cv2
import os, numpy as np
import imutils, configparser

config = configparser.ConfigParser()
config.read('flc.conf')

root_folder = config.get('input_path', 'root_folder')
test_data_dir = root_folder + '/test_data'
cropped_path = test_data_dir + '/2_cropped_images'
video_path = root_folder + '/video_data'
image_dir = '/1_images'
cropped_dir = '/2_cropped_images'
result_dir = '/3_resulted_images'
augmented_dir = '/4_augmented'
join_dir = '/5_join'
tracked_image_dir = '/6_trapped_images'
pdf_dir = '/7_pdf_files'

user_dir = test_data_dir
test_images = user_dir + image_dir
os.makedirs(test_images, exist_ok=True)
cropped_path = user_dir + cropped_dir
os.makedirs(cropped_path, exist_ok=True)
result_image_path = user_dir + result_dir
os.makedirs(result_image_path, exist_ok=True)
augmented_path = user_dir + augmented_dir
os.makedirs(augmented_path, exist_ok=True)
join_path = user_dir + join_dir
os.makedirs(join_path, exist_ok=True)
tracked_images_path = user_dir + tracked_image_dir
os.makedirs(tracked_images_path, exist_ok=True)
pdf_path = user_dir +pdf_dir
os.makedirs(pdf_path, exist_ok=True)


def main():
    video_number = 0
    for file in os.listdir(video_path):
        video_number += 1
        if file.endswith(".MTS"):
            path = os.path.join(video_path, file)
            cap = cv2.VideoCapture(path)
            calibratingText = "Segmenting....wait !!!"
            print(calibratingText)
            frame_number = 0
            while True:
                frame_number += 1
                ret, frame = cap.read()
                if ret == True:
                    org_image = cv2.addWeighted(frame, 2, frame, 0, 0)
                    org_image = imutils.resize(org_image, width=1000)
                    frame = org_image.copy()
                    hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                    green_low = np.array([45, 100, 50])
                    green_high = np.array([75, 255, 255])
                    curr_mask = cv2.inRange(hsv_img, green_low, green_high)
                    hsv_img[curr_mask > 0] = ([75, 255, 200])

                    # converting the HSV image to Gray in order to be able to apply contouring
                    RGB_again = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)
                    gray = cv2.cvtColor(RGB_again, cv2.COLOR_RGB2GRAY)
                    # ret, threshold = cv2.threshold(gray, 120, 255, 0)

                    blur = cv2.GaussianBlur(gray, (5, 5), 0)
                    ret, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_OTSU)
                    # thresh = cv2.dilate(thresh, None, iterations=3)
                    _, contours, hier = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

                    # ============================================================

                    # first_image = -1
                    i = 0
                    for c in contours:
                        if cv2.contourArea(c) >= float(config.get('segmentation', 'ignore_contour_area')):
                            i += 1
                            # if first_image == 0:
                            #     continue
                            x, y, w, h = cv2.boundingRect(c)
                            if (x != 0) & (y != 0) & ((x + w) != 1000) & ((y + h) != 562) & (w > 70):
                                mask = np.zeros((org_image.shape[0], org_image.shape[1], 1), np.uint8)
                                cv2.fillConvexPoly(mask, c, 255, 1)
                                kernel = np.ones((6, 6), np.uint8)
                                mask = cv2.dilate(mask, kernel, iterations=8)
                                out = cv2.bitwise_and(org_image, org_image, mask=mask)
                                out = out[y:y + h, x:x + w]
                                out[np.where((out == [0, 0, 0]).all(axis=2))] = [255, 255, 255]

                                if (frame_number > 0) & (frame_number < 10) & (i > 0) & (i < 10):
                                    print(ret)
                                    print('V{}_F000{}_B0{}: x: {}, y: {}, w: {}, h: {}'.format(video_number, frame_number, i, x, y, w, h))
                                    outfile = cropped_path + '/' + '/V%d_F000%d_B0%d.jpg' % (video_number, frame_number, i)
                                if (frame_number > 0) & (frame_number < 10) & (i > 9) & (i < 100):
                                    print(ret)
                                    print('V{}_F000{}_B{}: x: {}, y: {}, w: {}, h: {}'.format(video_number, frame_number, i, x, y, w, h))
                                    outfile = cropped_path + '/' + '/V%d_F000%d_B%d.jpg' % (video_number, frame_number, i)

                                if (frame_number > 9) & (frame_number < 100) & (i > 0) & (i < 10):
                                    print(ret)
                                    print('V{}_F00{}_B0{}: x: {}, y: {}, w: {}, h: {}'.format(video_number, frame_number, i, x, y, w, h))
                                    outfile = cropped_path + '/' + '/V%d_F00%d_B0%d.jpg' % (video_number, frame_number, i)
                                if (frame_number > 9) & (frame_number < 100) & (i > 9) & (i < 100):
                                    print(ret)
                                    print('V{}_F00{}_B{}: x: {}, y: {}, w: {}, h: {}'.format(video_number, frame_number, i, x, y, w, h))
                                    outfile = cropped_path + '/' + '/V%d_F00%d_B%d.jpg' % (video_number, frame_number, i)

                                if (frame_number > 99) & (frame_number < 1000) & (i > 0) & (i < 10):
                                    print(ret)
                                    print('V{}_F0{}_B0{}: x: {}, y: {}, w: {}, h: {}'.format(video_number, frame_number, i, x, y, w, h))
                                    outfile = cropped_path + '/' + '/V%d_F0%d_B0%d.jpg' % (video_number, frame_number, i)
                                if (frame_number > 99) & (frame_number < 1000) & (i > 9) & (i < 100):
                                    print(ret)
                                    print('V{}_F0{}_B{}: x: {}, y: {}, w: {}, h: {}'.format(video_number, frame_number, i, x, y, w, h))
                                    outfile = cropped_path + '/' + '/V%d_F0%d_B%d.jpg' % (video_number, frame_number, i)

                                if (frame_number > 999) & (frame_number < 10000) & (i > 0) & (i < 10):
                                    print(ret)
                                    print('V{}_F{}_B0{}: x: {}, y: {}, w: {}, h: {}'.format(video_number, frame_number, i, x, y, w, h))
                                    outfile = cropped_path + '/' + '/V%d_F%d_B0%d.jpg' % (video_number, frame_number, i)
                                if (frame_number > 999) & (frame_number < 10000) & (i > 9) & (i < 100):
                                    print(ret)
                                    print('V{}_F{}_B{}: x: {}, y: {}, w: {}, h: {}'.format(video_number, frame_number, i, x, y, w, h))
                                    outfile = cropped_path + '/' + '/V%d_F%d_B%d.jpg' % (video_number, frame_number, i)

                                # out = cv2.addWeighted(out, 2, out, 0, 0)
                                cv2.imwrite(outfile, out)
                                cv2.drawContours(org_image, c, -1, (0,255,255), 3)
                                cv2.imshow('show', org_image)
                                cv2.waitKey(1)
                else:
                    break


            cap.release()
            # cv2.destroyAllWindows()


# if __name__ == '__main__':
#     try:
#         main()
#     except:
#         flc.flc_with_cropped_images()
#         shutil.rmtree(test_data_dir + image_dir + '/' )
#         # shutil.rmtree(test_data_dir + cropped_dir + '/')
#         shutil.rmtree(test_data_dir + result_dir + '/')
#         shutil.rmtree(test_data_dir + augmented_dir + '/')
#         shutil.rmtree(test_data_dir + join_dir + '/')
#         shutil.rmtree(test_data_dir + tracked_image_dir + '/')
#         shutil.rmtree(test_data_dir + pdf_dir + '/')


main()

