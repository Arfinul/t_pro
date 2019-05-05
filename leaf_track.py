import cv2
import time
import imutils
#mport run


def segmentation():
    cap = cv2.VideoCapture('/home/chiranjeevi/Documents/Tea/test_videos/02_05_4 LED Side and Bottom board and Front near camera.MTS')
    time.sleep(2)

    # fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Save video file
    # out = cv2.VideoWriter('out.avi', fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))  # Save video file

    firstFrame = None
    count = 0
    frame_count = 0
    while 1:
        ret, frame = cap.read()

        #if frame_count % 4 == 0:
        if ret:
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
                    # cv2.imwrite("/home/arfin/Documents/GitHub/tea/darknet-master/results/frame%d.jpg" % count,
                    #             frame)  # Save Frames
                    if seg_c > 1:
                        if (x != 0) & (y != 0) & ((x + w) != 1000) & ((y + h) != 562):
                            print(count, x, y, x + w, y + h, count, seg_c, w * h)
                            #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            crop_img = frame[y:y + h, x:x + w]
                            cv2.imwrite(
                                "/home/chiranjeevi/Documents/Tea/Images_cropped/frame%d.%d_crop.jpg" % (
                                    count, seg_c), crop_img)  # Save Frames
                            # cv2.imwrite(
                            #     "/home/document/darknet-master-GCP/test_data/cropped_images/frame%d.%d_crop.jpg" % (
                            #         count, seg_c), crop_img)  # Save Frames gcp path
                    else:
                        if (x != 0) & (y != 0) & ((x + w) != 1000) & ((y + h) != 562):
                            
                            print(count, x, y, x + w, y + h, count, w * h)
                            #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            crop_img = frame[y:y + h, x:x + w]
                            cv2.imwrite(
                                "/home/chiranjeevi/Documents/Tea/Images_cropped/frame%d_crop.jpg" % count,
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
        #frame_count += 1
    cap.release()
    # out.release()  # Save video file
    cv2.destroyAllWindows()


segmentation()











