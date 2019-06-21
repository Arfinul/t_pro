import os

import PIL.Image as Image
from PIL import ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True


def create_test_list():
    commands = 'find `pwd`/roated_result -name \*.jpg > test.list'  # path of cropped images
    os.system(commands)


def yolo_classify_full():
    # command = './darknet detector test cfg/obj_3_class.data cfg/yolo-obj_3_class.cfg backup/yolo-obj_3_class_11500.weights -dont_show<test.list>result.list'
    command = './darknet detector test cfg/obj.data cfg/yolo-obj.cfg yolo-obj_11500.weights -dont_show<test.list>result.list'
    # command = './darknet detector test cfg/obj.data cfg/yolo-obj.cfg yolo-obj_11500.weights -dont_show<test.list>result.list'  # gcp path to test
    os.system(command)


def yolo_classify_one_by_one():
    image_List = []
    test_Path = r'/home/agnext/Documents/Flc_copy/test'
    with open((test_Path + '.list'), 'r') as fobj:
        for line in fobj:
            image_List.append([i for i in line.strip("\n").split(":")])
            image_List.sort(key=lambda x: x[0])
            # image_List = [[num for num in line.split()] for line in fobj]
        for images in image_List:
            commands = [
                './darknet detector test cfg/obj.data cfg/yolo-obj.cfg yolo-obj_11500.weights ''-dont_show',
                images[0]]
            os.system(' '.join(commands))
            predicted_image = Image.open("/home/agnext/Documents/Flc_copy/predictions.jpg")
            output = "/home/agnext/Documents/Flc_copy/rotated_results/predicted_image_%s" % os.path.basename(
                os.path.normpath(images[0]))
            predicted_image.save(output)


def count():
    k = 0
    F = 0
    fname = 'result.list'
    with open(fname, 'r') as f:
        for line in f:
            words = line.split()
            for i in words:
                if i == "Coarse":
                    k = k + 1
                if i == "Fine":
                    F = F + 1
    print("Coarse count - :")
    print(k)
    print("Fine count - :")
    print(F)


create_test_list()
yolo_classify_full()
count()
yolo_classify_one_by_one()


