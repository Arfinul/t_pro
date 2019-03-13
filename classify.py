import os, shutil
import glob
import PIL.Image as Image
from PIL import ImageFile

import display_results

ImageFile.LOAD_TRUNCATED_IMAGES = True
images = None
fine_count = 0


cropped_path = '/home/arfin/Documents/GitHub/tea/Flc/test_data/2_cropped_images'  # gcp image path
# cropped_path = '/test_data/2_cropped_images'  # KGP GPU image path

trapped_images_path = '/home/arfin/Documents/GitHub/tea/Flc/test_data/6_trapped_images'  # gcp image path

test_list_path = r'/home/arfin/Documents/GitHub/tea/Flc/test'  # gcp test list path
# test_list_path = r'/home/agnext-kgp/Documents/tea/Flc/test'  # KGP GPU test list path

trap_list_path = r'/home/arfin/Documents/GitHub/tea/Flc/trap'  # gcp test list path

result_image_path = '/home/arfin/Documents/GitHub/tea/Flc/test_data/3_resulted_images'  # gcp result image path
# result_image_path = '/home/agnext-kgp/Documents/tea/Flc/test_data/3_resulted_images'  # KGP GPU gcp result image path

augmented_path = '/home/arfin/Documents/GitHub/tea/Flc/test_data/4_augmented'

command_classify_full = './darknet detector test cfg/obj.data cfg/yolo-obj_11500.cfg yolo-obj_11500.weights -dont_show<test.list>result.list'
# command_classify_full = './darknet detector test cfg/obj.data cfg/yolo-obj_15700.cfg yolo-obj_15700_36000.weights -dont_show<test.list>result.list'

command_classify_one_by_one = './darknet detector test cfg/obj.data cfg/yolo-obj_11500.cfg yolo-obj_11500.weights ''-dont_show '

# command_classify_one_by_one = './darknet detector test cfg/obj.data cfg/yolo-obj_15700.cfg yolo-obj_15700_36000.weights ''-dont_show '


def create_test_list():
    # command_create_list = 'find `pwd`' + cropped_path + ' -name \*.jpg > test.list'  # gcp path of cropped images
    # os.system(command_create_list)

    files = glob.glob(cropped_path + '/*.jpg')
    with open('test.list', 'w') as in_files:
        for eachfile in sorted(files): in_files.write(eachfile + '\n')


def create_trapped_list():
    # command_create_list = 'find `pwd`' + cropped_path + ' -name \*.jpg > test.list'  # gcp path of cropped images
    # os.system(command_create_list)

    files = glob.glob(trapped_images_path + '/*.jpg')
    with open('trap.list', 'w') as in_files:
        for eachfile in sorted(files): in_files.write(eachfile + '\n')


def yolo_classify_full():
    os.system(command_classify_full)


def count():
    # k = 0
    # F = 0
    # fname = 'result.list'
    # with open(fname, 'r') as f:
    #    for line in f:
    #        words = line.split()
    #        for i in words:
    #            if i == "Coarse":
    #                k = k + 1
    #            if i == "Fine":
    #                F = F + 1
    # print("Coarse count - : %d" % k)
    # print("Fine count - : %d" % F)

    # return k, F

    # filename = 'result.list'

    filename = 'result.list'

    n = 0
    fine_count = 0
    lines = []
    with open(filename, 'r') as file:
        for line in file:
            lines.append(line)
        chunks = [lines[x:x + 7] for x in range(0, len(lines), 7)]
        # print(chunks)
        for chunk in chunks:
            f = 0
            # print(chunk)
            for line in chunk:
                words = line.split()
                for i in words:
                    if i == "Fine":
                        f = f + 1
                        break
                if f != 0:
                    break
            else:
                continue
            if f != 0:
                fine_count = fine_count + 1
    coarse = len(chunks) - fine_count
    print("Coarse count - : %d" % coarse)
    print("Fine count - : %d" % fine_count)

    return coarse, fine_count


def yolo_classify_one_by_one():
    image_List = []
    test_list_Path = test_list_path
    with open((test_list_Path + '.list'), 'r') as fobj:
        for line in fobj:
            image_List.append([i for i in line.strip("\n").split(":")])
            image_List.sort(key=lambda x: x[0])
            # image_List = [[num for num in line.split()] for line in fobj]
        for images in image_List:
            commands = [command_classify_one_by_one, images[0]]
            os.system(' '.join(commands))
            predicted_image = Image.open("predictions.jpg")
            output = result_image_path + '/predicted_image_%s' % os.path.basename(os.path.normpath(images[0]))
            predicted_image.save(output)
    # os.system('rm ' + result_image_path + '/*')


def yolo_classify_trap_one_by_one():
    image_List = []
    with open((trap_list_path + '.list'), 'r') as fobj:
        for line in fobj:
            image_List.append([i for i in line.strip("\n").split(":")])
            image_List.sort(key=lambda x: x[0])
            # image_List = [[num for num in line.split()] for line in fobj]
        for images in image_List:
            commands = [command_classify_one_by_one, images[0]]
            os.system(' '.join(commands))
            predicted_image = Image.open("predictions.jpg")
            output = result_image_path + '/predicted_image_%s' % os.path.basename(os.path.normpath(images[0]))
            predicted_image.save(output)
    # os.system('rm ' + result_image_path + '/*')


# def trap_images_to_test():
#     filename = 'result.list'
#     image_file = 'test.list'
#     fine_count = 0
#     lines = []
#     lines_traped = []
#     index_trapped = []
#
#     print("Trapping the images to test.. ")
#     with open(filename, 'r') as file:
#         for line in file:
#             lines.append(line)
#         chunks = [lines[x:x + 7] for x in range(0, len(lines), 7)]
#         for chunk in chunks:
#             f = 0
#             coarse_list_chunk = []
#             for line in chunk:
#                 words = line.split()
#                 for i in words:
#                     if i == "Fine":
#                         f = f + 1
#                         # print(f, line)
#                         lines_traped.append(line)
#                         break
#                     if i == "Coarse":
#                         coarse_list_chunk.append(line)
#                 if f != 0:
#                     break
#             else:
#                 lines_traped.append(coarse_list_chunk[0])
#                 continue
#             if f != 0:
#                 # print("arfin", f)
#                 fine_count = fine_count + 1
#                 # print(fine_count)
#     # print("Fine count - : %d" % fine_count)
#     # print(lines_traped)
#     with open(filename) as file_again:
#         for num, line in enumerate(file_again, 1):
#             for each in lines_traped:
#                 if each in line:
#                     print('found at line:', num)
#                     index_trapped.append(num)
#
#     for i, line in enumerate(open(image_file), 1):
#         if i in index_trapped:
#             line = line.strip('\n')
#             # print(line)
#             shutil.move(line, trapped_images_path)


def trap_images_to_test():
    filename = 'result.list'
    image_file = 'test.list'
    fine_count = 0
    lines = []
    fine_lines_trapped = []
    fine_index_trapped = []
    coarse_index_trapped = []
    coarse_lines_trapped = []

    print("Trapping the images to test.. ")
    with open(filename, 'r') as file:
        for line in file:
            lines.append(line)
        chunks = [lines[x:x + 7] for x in range(0, len(lines), 7)]
        for chunk in chunks:
            f = 0
            coarse_list_chunk = []
            for line in chunk:
                words = line.split()
                for i in words:
                    if i == "Fine":
                        f = f + 1
                        fine_lines_trapped.append(line)
                        break
                    if i == "Coarse":
                        coarse_list_chunk.append(line)
                if f != 0:
                    break
            else:
                coarse_lines_trapped.append(coarse_list_chunk[0])
                continue
            if f != 0:
                # print("arfin", f)
                fine_count = fine_count + 1
                # print(fine_count)
    # print("Fine count - : %d" % fine_count)
    # print(fine_lines_trapped)
    # print(coarse_lines_trapped)
    with open(filename) as file_again:
        for num, line in enumerate(file_again, 1):
            for each in fine_lines_trapped:
                if each in line:
                    # print('found at line:', num)
                    fine_index_trapped.append(num)
            for each in coarse_lines_trapped:
                if each in line:
                    # print('found at line:', num)
                    coarse_index_trapped.append(num)

    # print(fine_index_trapped)
    # print(coarse_index_trapped)

    fine_and_coarse = [fine_index_trapped, coarse_index_trapped]
    print(fine_and_coarse)
    report_count = 1
    for each in fine_and_coarse:
        print("ENTERED")
        for i, line in enumerate(open(image_file), 1):
            if i in each:
                line = line.strip('\n')
                print(line)
                shutil.move(line, trapped_images_path)
        create_trapped_list()
        yolo_classify_trap_one_by_one()
        display_results.merge_test_and_result()
        display_results.make_files_list()
        display_results.merge_pdf(report_count)
        if report_count == 1:
            display_results.write_counts('Fine counts = ' + str(fine_count), report_count)
        if report_count == 2:
            display_results.write_counts('Coarse counts = ' + str(len(chunks) - fine_count), report_count)
        report_count = report_count + 1
    os.system('rm ' + augmented_path + '/*.pdf')
    display_results.final_report_pdf()

