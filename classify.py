import os, shutil
import glob, configparser
import PIL.Image as Image
from PIL import ImageFile
import display_results

ImageFile.LOAD_TRUNCATED_IMAGES = True
images = None
fine_count = 0
config = configparser.ConfigParser()
config.read('flc.conf')
root_folder = config.get('input_path', 'root_folder')
test_data_dir = root_folder + '/test_data'

cropped_dir = '/2_cropped_images'
tracked_image_dir = '/6_trapped_images'
augmented_dir = '/4_augmented'
result_dir = '/3_resulted_images'
test_list_path = root_folder + '/test'
trap_list_path = root_folder + '/trap'


def create_test_list(userId, sectionId):
    types = ('/*.jpg', '/*.png', '/*.jpeg')
    files_grabbed = []
    user_dir = test_data_dir + '/u-' + userId + '/s-' + sectionId
    cropped_path = user_dir + cropped_dir
    for files in types:
        files_grabbed.extend(glob.glob(cropped_path + files))
    #print(files_grabbed)
    with open(user_dir + '/test.list', 'w') as in_files:
        for eachfile in sorted(files_grabbed): in_files.write(eachfile + '\n')


def create_trapped_list(userId, sectionId):
    types = ('/*.jpg', '/*.png', '/*.jpeg')
    files_grabbed = []
    user_dir = test_data_dir + '/u-' + userId + '/s-' + sectionId
    tracked_images_path = user_dir + tracked_image_dir
    for files in types:
        files_grabbed.extend(glob.glob(tracked_images_path + files))
    with open(root_folder + '/trap.list', 'w') as in_files:
        for eachfile in sorted(files_grabbed): in_files.write(eachfile + '\n')


    #user_dir = test_data_dir + '/u-' + userId + '/s-' + sectionId
    #tracked_images_path = user_dir + tracked_image_dir
    #files = glob.glob(tracked_images_path + '/*.jpg')
    #with open('trap.list', 'w') as in_files:
        #for eachfile in sorted(files): in_files.write(eachfile + '\n')


def yolo_classify_full(userId, sectionId):
    user_dir = test_data_dir + '/u-' + userId + '/s-' + sectionId
    testing_command = config.get('testing_command', 'command_classify')
    os.system(testing_command + '<' + user_dir + '/test.list' + '>' + user_dir + '/result.list')


def count(userId, sectionId):
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

    user_dir = test_data_dir + '/u-' + userId + '/s-' + sectionId
    filename = user_dir + '/result.list'
    fine_count = 0
    lines = []
    with open(filename, 'r') as file:
        for line in file:
            lines.append(line)
        chunks = [lines[x:x + 7] for x in range(0, len(lines), 7)]
        for chunk in chunks:
            f = 0
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


def find_each_class_count(userId, sectionId):
    from collections import defaultdict

    user_dir = test_data_dir + '/u-' + userId + '/s-' + sectionId
    filename = user_dir + '/result.list'

    lines = []
    fine_lines_trapped = []
    coarse_lines_trapped = []
    fine_index_trapped = []
    coarse_index_trapped = []
    lb_1 = lb_2 = lb_3 = lbj_1 = b_1 = 0
    with open(filename, 'r') as file:
        for line in file:
            lines.append(line)
        chunks = [lines[x:x + 7] for x in range(0, len(lines), 7)]
        for chunk in chunks:
            fine_cases_in_7 = []
            all_coarse_in_7 = []
            for line in chunk:
                words = line.split()
                if words[-2] in ['3lb', '2lb', '1lb', '1b', '1lbj']:
                    fine_cases_in_7.append(words[-2])
                else:
                    all_coarse_in_7.append(line)
            #print(fine_cases_in_7)

            if len(all_coarse_in_7) == 7:
                coarse_lines_trapped.append(all_coarse_in_7[0])
                continue
            else:
                if fine_cases_in_7:
                    d = defaultdict(int)
                    for i in fine_cases_in_7:
                        d[i] += 1
                    result = max(d.items(), key=lambda x: x[1])

            frequent_fine_cases_conf = []
            conf = 0
            for line in chunk:
                words = line.split()
                if words[-2] == result[0]:
                    if words[-2] == '3lb':
                        conf = (int(words[1]) + int(words[2]) + int(words[3]) + int(words[4])) / 4
                    if words[-2] == '2lb':
                        conf = (int(words[1]) + int(words[2]) + int(words[3])) / 3
                    if words[-2] == '1lb':
                        conf = (int(words[1]) + int(words[2])) / 2
                    if words[-2] == '1lbj':
                        conf = (int(words[1]) + int(words[2])) / 2
                    if words[-2] == '1b':
                        conf = int(words[1])
                    frequent_fine_cases_conf.append(conf)

            for line in chunk:
                words = line.split()
                if words[-2] == result[0]:
                    if words[-2] == '3lb':
                        confd = (int(words[1]) + int(words[2]) + int(words[3]) + int(words[4])) / 4
                        if confd == max(frequent_fine_cases_conf):
                            lb_3 = lb_3 + 1
                            fine_lines_trapped.append(line)
                            break
                    if words[-2] == '2lb':
                        confd = (int(words[1]) + int(words[2]) + int(words[3])) / 3
                        if confd == max(frequent_fine_cases_conf):
                            lb_2 = lb_2 + 1
                            fine_lines_trapped.append(line)
                            break
                    if words[-2] == '1lb':
                        confd = (int(words[1]) + int(words[2])) / 2
                        if confd == max(frequent_fine_cases_conf):
                            lb_1 = lb_1 + 1
                            fine_lines_trapped.append(line)
                            break
                    if words[-2] == '1lbj':
                        confd = (int(words[1]) + int(words[2])) / 2
                        if confd == max(frequent_fine_cases_conf):
                            fine_lines_trapped.append(line)
                            lbj_1 = lbj_1 + 1
                            break
                    if words[-2] == '1b':
                        confd = int(words[1])
                        if confd == max(frequent_fine_cases_conf):
                            b_1 = b_1 + 1
                            fine_lines_trapped.append(line)
                            break


    with open(filename) as file_again:
        for num, line in enumerate(file_again, 1):
            for each in fine_lines_trapped:
                if each in line:
                    fine_index_trapped.append(num)
            for each in coarse_lines_trapped:
                if each in line:
                    coarse_index_trapped.append(num)
    fine_and_coarse = [fine_index_trapped, coarse_index_trapped]
    print(fine_and_coarse)
    print('Fine = ', len(fine_index_trapped))
    print('Coarse = ', len(coarse_index_trapped))
    print("lb_1 = %d" % lb_1)
    print("lb_2 = %d" % lb_2)
    print("lb_3 = %d" % lb_3)
    print("lbj_1 = %d" % lbj_1)
    print("b_1 = %d" % b_1)
    print("total = %d" % (len(fine_index_trapped) + len(coarse_index_trapped)))
    return lb_1, lb_2, lb_3, lbj_1, b_1, (len(fine_index_trapped) + len(coarse_index_trapped))


def get_fine_count_as_per_best_among_7_rotation_by_priotising_leaf_def(userId, sectionId):
    from collections import defaultdict
    priority_list = ['3lbj', '3lb', '3l', '2lbj', '2lb', '2l', '1lbj', '1lb', '1l', '1bj', '1b']
    user_dir = test_data_dir + '/u-' + userId + '/s-' + sectionId
    filename = user_dir + '/result.list'

    lines = []
    fine_lines_trapped = []
    coarse_lines_trapped = []
    fine_index_trapped = []
    coarse_index_trapped = []
    lb_1 = lb_2 = lb_3 = lbj_1 = lbj_2 = lbj_3 = b_1 = bj_1 = l_1 = l_2 = l_3 = 0
    with open(filename, 'r') as file:
        for line in file:
            lines.append(line)
        chunks = [lines[x:x + 7] for x in range(0, len(lines), 7)]
        for chunk_p in chunks:
            fine_cases_in_7 = []
            all_coarse_in_7 = []
            for line in chunk_p:
                words = line.split()
                if words[-2] in priority_list:
                    fine_cases_in_7.append(words[-2])
                else:
                    all_coarse_in_7.append(line)
            if len(all_coarse_in_7) == 7:
                coarse_lines_trapped.append(all_coarse_in_7[0])
                continue
            else:
                if fine_cases_in_7:
                    for i in range(len(priority_list)):
                        if (priority_list[i] or priority_list[i + 1] or priority_list[i + 2]) in fine_cases_in_7:
                            result = priority_list[i]
                            break
                        else:
                            continue
            frequent_fine_cases_conf = []
            conf = 0
            chunk = [i.replace("%", '') for i in chunk_p]
            for line in chunk:
                words = line.split()
                if words[-2] == result:
                    if (words[-2] == '3lb') or (words[-2] == '3lbj'):
                        conf = (int(words[1]) + int(words[2]) + int(words[3]) + int(words[4])) / 4
                    if (words[-2] == '2lb') or (words[-2] == '2lbj') or (words[-2] == '3l'):
                        conf = (int(words[1]) + int(words[2]) + int(words[3])) / 3
                    if (words[-2] == '1lb') or (words[-2] == '1lbj' or (words[-2] == '2l')):
                        conf = (int(words[1]) + int(words[2])) / 2
                    if (words[-2] == '1b') or (words[-2] == '1bj') or (words[-2] == '1l'):
                        conf = int(words[1])
                    frequent_fine_cases_conf.append(conf)
            for line in chunk:
                words = line.split()
                if words[-2] == result:
                    if words[-2] == '3lb':
                        confd = (int(words[1]) + int(words[2]) + int(words[3]) + int(words[4])) / 4
                        if confd == max(frequent_fine_cases_conf):
                            lb_3 = lb_3 + 1
                            fine_lines_trapped.append(line)
                            break
                    if words[-2] == '3lbj':
                        confd = (int(words[1]) + int(words[2]) + int(words[3]) + int(words[4])) / 4
                        if confd == max(frequent_fine_cases_conf):
                            lbj_3 = lbj_3 + 1
                            coarse_lines_trapped.append(line)
                            break
                    if words[-2] == '2lb':
                        confd = (int(words[1]) + int(words[2]) + int(words[3])) / 3
                        if confd == max(frequent_fine_cases_conf):
                            lb_2 = lb_2 + 1
                            fine_lines_trapped.append(line)
                            break
                    if words[-2] == '2lbj':
                        confd = (int(words[1]) + int(words[2]) + int(words[3])) / 3
                        if confd == max(frequent_fine_cases_conf):
                            lbj_2 = lbj_2 + 1
                            coarse_lines_trapped.append(line)
                            break
                    if words[-2] == '1lb':
                        confd = (int(words[1]) + int(words[2])) / 2
                        if confd == max(frequent_fine_cases_conf):
                            lb_1 = lb_1 + 1
                            fine_lines_trapped.append(line)
                            break
                    if words[-2] == '1lbj':
                        confd = (int(words[1]) + int(words[2])) / 2
                        if confd == max(frequent_fine_cases_conf):
                            fine_lines_trapped.append(line)
                            lbj_1 = lbj_1 + 1
                            break
                    if words[-2] == '1b':
                        confd = int(words[1])
                        if confd == max(frequent_fine_cases_conf):
                            b_1 = b_1 + 1
                            fine_lines_trapped.append(line)
                            break
                    if words[-2] == '1bj':
                        confd = int(words[1])
                        if confd == max(frequent_fine_cases_conf):
                            bj_1 = bj_1 + 1
                            fine_lines_trapped.append(line)
                            break
                    if words[-2] == '1l':
                        confd = int(words[1])
                        if confd == max(frequent_fine_cases_conf):
                            l_1 = l_1 + 1
                            coarse_lines_trapped.append(line)
                            break
                    if words[-2] == '2l':
                        confd = (int(words[1]) + int(words[2])) / 2
                        if confd == max(frequent_fine_cases_conf):
                            l_2 = l_2 + 1
                            coarse_lines_trapped.append(line)
                            break
                    if words[-2] == '3l':
                        confd = (int(words[1]) + int(words[2]) + int(words[3])) / 3
                        if confd == max(frequent_fine_cases_conf):
                            l_3 = l_3 + 1
                            coarse_lines_trapped.append(line)
                            break


    with open(filename) as file_again:
        for num, line in enumerate(file_again, 1):
            for each in fine_lines_trapped:
                if each in line:
                    fine_index_trapped.append(num)
            for each in coarse_lines_trapped:
                if each in line:
                    coarse_index_trapped.append(num)
    fine_and_coarse = [fine_index_trapped, coarse_index_trapped]
    total = lb_1 + lb_2 + lb_3 + lbj_1 + lbj_2 + lbj_3 + b_1 + bj_1 + l_1 + l_2 + l_3 + len(coarse_index_trapped)
    print('Fine = ', len(fine_index_trapped))
    print('Coarse = ', len(coarse_index_trapped))
    print("lb_1 = %d" % lb_1)
    print("lb_2 = %d" % lb_2)
    print("lb_3 = %d" % lb_3)
    print("lbj_1 = %d" % lbj_1)
    print("lbj_2 = %d" % lbj_2)
    print("lbj_3 = %d" % lbj_3)
    print("b_1 = %d" % b_1)
    print("bj_1 = %d" % bj_1)
    print("l_1 = %d" % l_1)
    print("l_2 = %d" % l_2)
    print("l_3 = %d" % l_3)
    print("total = %d" % total)
    # print("total = %d" % (len(fine_index_trapped) + len(coarse_index_trapped)))
    # return lb_1, lb_2, lb_3, lbj_1, lbj_2, lbj_3, b_1, bj_1, l_1, l_2, l_3, (len(fine_index_trapped) + len(coarse_index_trapped))
    return lb_1, lb_2, lb_3, lbj_1, lbj_2, lbj_3, b_1, bj_1, l_1, l_2, l_3, total


def yolo_classify_one_by_one(userId, sectionId):
    image_List = []

    user_dir = test_data_dir + '/u-' + userId + '/s-' + sectionId
    test_list_Path  = user_dir + '/test'
    result_image_path = user_dir + result_dir
     
    with open((test_list_Path + '.list'), 'r') as fobj:
        for line in fobj:
            image_List.append([i for i in line.strip("\n").split(":")])
            image_List.sort(key=lambda x: x[0])
        for images in image_List:
            commands = [config.get('testing_command', 'command_classify'), ' ', images[0]]
            os.system(' '.join(commands))
            predicted_image = Image.open("predictions.jpg")
            output = result_image_path + '/predicted_image_%s' % os.path.basename(os.path.normpath(images[0]))
            predicted_image.save(output)


def yolo_classify_trap_one_by_one(userId, sectionId):
    image_List = []
    user_dir = test_data_dir + '/u-' + userId + '/s-' + sectionId
    result_image_path = user_dir + result_dir
    with open((trap_list_path + '.list'), 'r') as fobj:
        for line in fobj:
            image_List.append([i for i in line.strip("\n").split(":")])
            image_List.sort(key=lambda x: x[0])
        for images in image_List:
            commands = [config.get('testing_command', 'command_classify'), ' ', images[0]]
            os.system(' '.join(commands))
            predicted_image = Image.open("predictions.jpg")
            output = result_image_path + '/predicted_image_%s' % os.path.basename(os.path.normpath(images[0]))
            predicted_image.save(output)


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
                fine_count = fine_count + 1
    with open(filename) as file_again:
        for num, line in enumerate(file_again, 1):
            for each in fine_lines_trapped:
                if each in line:
                    fine_index_trapped.append(num)
            for each in coarse_lines_trapped:
                if each in line:
                    coarse_index_trapped.append(num)

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
        display_results.make_files_list(report_count, fine_count, chunks)
        display_results.merge_pdf(report_count)

        report_count = report_count + 1

    display_results.final_report_pdf()
    os.system('rm ' + augmented_path + '/*.pdf')


def yolo_classify_each_and_generate_report(userId, sectionId):
    from collections import defaultdict

    user_dir = test_data_dir + '/u-' + userId + '/s-' + sectionId
    filename = user_dir + '/result.list'
    image_file = user_dir + '/test.list'
    tracked_images_path = user_dir + tracked_image_dir
    augmented_path = user_dir + augmented_dir

    lines = []
    fine_lines_trapped = []
    coarse_lines_trapped = []
    fine_index_trapped = []
    coarse_index_trapped = []
    with open(filename, 'r') as file:
        for line in file:
            lines.append(line)
        chunks = [lines[x:x + 7] for x in range(0, len(lines), 7)]
        for chunk in chunks:
            fine_cases_in_7 = []
            all_coarse_in_7 = []
            for line in chunk:
                words = line.split()
                if words[-2] in ['3lb', '2lb', '1lb', '1b', '1lbj']:
                    fine_cases_in_7.append(words[-2])
                else:
                    all_coarse_in_7.append(line)
            #print(fine_cases_in_7)

            if len(all_coarse_in_7) == 7:
                coarse_lines_trapped.append(all_coarse_in_7[0])
                continue
            else:
                d = defaultdict(int)
                for i in fine_cases_in_7:
                    d[i] += 1
                result = max(d.items(), key=lambda x: x[1])

            frequent_fine_cases_conf = []
            conf = 0
            for line in chunk:
                words = line.split()
                if words[-2] == result[0]:
                    if words[-2] == '3lb':
                        conf = (int(words[1]) + int(words[2]) + int(words[3]) + int(words[4])) / 4
                    if words[-2] == '2lb':
                        conf = (int(words[1]) + int(words[2]) + int(words[3])) / 3
                    if words[-2] == '1lb':
                        conf = (int(words[1]) + int(words[2])) / 2
                    if words[-2] == '1lbj':
                        conf = (int(words[1]) + int(words[2])) / 2
                    if words[-2] == '1b':
                        conf = int(words[1])
                    frequent_fine_cases_conf.append(conf)
                # if conf > greatest:
                #     greatest = conf

            for line in chunk:
                words = line.split()
                if words[-2] == result[0]:
                    if words[-2] == '3lb':
                        confd = (int(words[1]) + int(words[2]) + int(words[3]) + int(words[4])) / 4
                        if confd == max(frequent_fine_cases_conf):
                            fine_lines_trapped.append(line)
                            break
                    if words[-2] == '2lb':
                        confd = (int(words[1]) + int(words[2]) + int(words[3])) / 3
                        if confd == max(frequent_fine_cases_conf):
                            fine_lines_trapped.append(line)
                            break
                    if words[-2] == '1lb':
                        confd = (int(words[1]) + int(words[2])) / 2
                        if confd == max(frequent_fine_cases_conf):
                            fine_lines_trapped.append(line)
                            break
                    if words[-2] == '1lbj':
                        confd = (int(words[1]) + int(words[2])) / 2
                        if confd == max(frequent_fine_cases_conf):
                            fine_lines_trapped.append(line)
                            break
                    if words[-2] == '1b':
                        confd = int(words[1])
                        if confd == max(frequent_fine_cases_conf):
                            fine_lines_trapped.append(line)
                            break
            #print(max(frequent_fine_cases_conf))
            #print(frequent_fine_cases_conf)
            #print(fine_lines_trapped)
            #print(coarse_lines_trapped)

    with open(filename) as file_again:
        for num, line in enumerate(file_again, 1):
            for each in fine_lines_trapped:
                if each in line:
                    fine_index_trapped.append(num)
            for each in coarse_lines_trapped:
                if each in line:
                    coarse_index_trapped.append(num)
    fine_and_coarse = [fine_index_trapped, coarse_index_trapped]
    print(fine_and_coarse)
    print('Fine = ', len(fine_index_trapped))
    print('Coarse = ', len(coarse_index_trapped))

    report_count = 1
    for each in fine_and_coarse:
        if each:
            for i, line in enumerate(open(image_file), 1):
                if i in each:
                    line = line.strip('\n')
                    #print(line)
                    shutil.move(line, tracked_images_path)
            create_trapped_list(userId, sectionId)
            yolo_classify_trap_one_by_one(userId, sectionId)
            display_results.merge_test_and_result(userId, sectionId)
            display_results.make_files_list(report_count, len(fine_index_trapped), len(coarse_index_trapped), userId, sectionId)
            display_results.merge_pdf(report_count, userId, sectionId)

            report_count = report_count + 1
        else:
            continue

    display_results.final_report_pdf(userId, sectionId)
    #shutil.rmtree(test_data_dir + '/u-' + userId + '/s-' + sectionId + '/')

    return len(fine_index_trapped), len(coarse_index_trapped)



def yolo_classify_each_and_generate_report_as_per_best_among_7_rotation_by_priotising_leaf_def(userId, sectionId):
    from collections import defaultdict
    priority_list = ['3lbj', '3lb', '3l', '2lbj', '2lb', '2l', '1lbj', '1lb', '1l', '1bj', '1b']
    user_dir = test_data_dir + '/u-' + userId + '/s-' + sectionId
    filename = user_dir + '/result.list'
    image_file = user_dir + '/test.list'
    tracked_images_path = user_dir + tracked_image_dir
    augmented_path = user_dir + augmented_dir

    lines = []
    fine_lines_trapped = []
    coarse_lines_trapped = []
    fine_index_trapped = []
    coarse_index_trapped = []
    lb_1 = lb_2 = lb_3 = lbj_1 = lbj_2 = lbj_3 = b_1 = bj_1 = l_1 = l_2 = l_3 = 0
    with open(filename, 'r') as file:
        for line in file:
            lines.append(line)
        chunks = [lines[x:x + 7] for x in range(0, len(lines), 7)]
        for chunk in chunks:
            fine_cases_in_7 = []
            all_coarse_in_7 = []
            for line in chunk:
                words = line.split()
                if words[-2] in priority_list:
                    fine_cases_in_7.append(words[-2])
                else:
                    all_coarse_in_7.append(line)
            if len(all_coarse_in_7) == 7:
                coarse_lines_trapped.append(all_coarse_in_7[0])
                continue
            else:
                if fine_cases_in_7:
                    for i in range(len(priority_list)):
                        if (priority_list[i] or priority_list[i + 1] or priority_list[i + 2]) in fine_cases_in_7:
                            result = priority_list[i]
                            break
                        else:
                            continue
            frequent_fine_cases_conf = []
            conf = 0
            for line in chunk:
                words = line.split()
                if words[-2] == result:
                    if (words[-2] == '3lb') or (words[-2] == '3lbj'):
                        conf = (int(words[1]) + int(words[2]) + int(words[3]) + int(words[4])) / 4
                    if (words[-2] == '2lb') or (words[-2] == '2lbj') or (words[-2] == '3l'):
                        conf = (int(words[1]) + int(words[2]) + int(words[3])) / 3
                    if (words[-2] == '1lb') or (words[-2] == '1lbj' or (words[-2] == '2l')):
                        conf = (int(words[1]) + int(words[2])) / 2
                    if (words[-2] == '1b') or (words[-2] == '1bj') or (words[-2] == '1l'):
                        conf = int(words[1])
                    frequent_fine_cases_conf.append(conf)
            for line in chunk:
                words = line.split()
                if words[-2] == result:
                    if words[-2] == '3lb':
                        confd = (int(words[1]) + int(words[2]) + int(words[3]) + int(words[4])) / 4
                        if confd == max(frequent_fine_cases_conf):
                            lb_3 = lb_3 + 1
                            fine_lines_trapped.append(line)
                            break
                    if words[-2] == '3lbj':
                        confd = (int(words[1]) + int(words[2]) + int(words[3]) + int(words[4])) / 4
                        if confd == max(frequent_fine_cases_conf):
                            lbj_3 = lbj_3 + 1
                            coarse_lines_trapped.append(line)
                            break
                    if words[-2] == '2lb':
                        confd = (int(words[1]) + int(words[2]) + int(words[3])) / 3
                        if confd == max(frequent_fine_cases_conf):
                            lb_2 = lb_2 + 1
                            fine_lines_trapped.append(line)
                            break
                    if words[-2] == '2lbj':
                        confd = (int(words[1]) + int(words[2]) + int(words[3])) / 3
                        if confd == max(frequent_fine_cases_conf):
                            lbj_2 = lbj_2 + 1
                            coarse_lines_trapped.append(line)
                            break
                    if words[-2] == '1lb':
                        confd = (int(words[1]) + int(words[2])) / 2
                        if confd == max(frequent_fine_cases_conf):
                            lb_1 = lb_1 + 1
                            fine_lines_trapped.append(line)
                            break
                    if words[-2] == '1lbj':
                        confd = (int(words[1]) + int(words[2])) / 2
                        if confd == max(frequent_fine_cases_conf):
                            fine_lines_trapped.append(line)
                            lbj_1 = lbj_1 + 1
                            break
                    if words[-2] == '1b':
                        confd = int(words[1])
                        if confd == max(frequent_fine_cases_conf):
                            b_1 = b_1 + 1
                            fine_lines_trapped.append(line)
                            break
                    if words[-2] == '1bj':
                        confd = int(words[1])
                        if confd == max(frequent_fine_cases_conf):
                            bj_1 = bj_1 + 1
                            fine_lines_trapped.append(line)
                            break
                    if words[-2] == '1l':
                        confd = int(words[1])
                        if confd == max(frequent_fine_cases_conf):
                            l_1 = l_1 + 1
                            coarse_lines_trapped.append(line)
                            break
                    if words[-2] == '2l':
                        confd = (int(words[1]) + int(words[2])) / 2
                        if confd == max(frequent_fine_cases_conf):
                            l_2 = l_2 + 1
                            coarse_lines_trapped.append(line)
                            break
                    if words[-2] == '3l':
                        confd = (int(words[1]) + int(words[2]) + int(words[3])) / 3
                        if confd == max(frequent_fine_cases_conf):
                            l_3 = l_3 + 1
                            coarse_lines_trapped.append(line)
                            break

    with open(filename) as file_again:
        for num, line in enumerate(file_again, 1):
            for each in fine_lines_trapped:
                if each in line:
                    fine_index_trapped.append(num)
            for each in coarse_lines_trapped:
                if each in line:
                    coarse_index_trapped.append(num)
    fine_and_coarse = [fine_index_trapped, coarse_index_trapped]
    print(fine_and_coarse)
    print('Fine = ', len(fine_index_trapped))
    print('Coarse = ', len(coarse_index_trapped))
    print("lb_1 = %d" % lb_1)
    print("lb_2 = %d" % lb_2)
    print("lb_3 = %d" % lb_3)
    print("lbj_1 = %d" % lbj_1)
    print("lbj_2 = %d" % lbj_2)
    print("lbj_3 = %d" % lbj_3)
    print("b_1 = %d" % b_1)
    print("bj_1 = %d" % bj_1)
    print("l_1 = %d" % l_1)
    print("l_2 = %d" % l_2)
    print("l_3 = %d" % l_3)
    print("total = %d" % (len(fine_index_trapped) + len(coarse_index_trapped)))

    report_count = 1
    for each in fine_and_coarse:
        if each:
            for i, line in enumerate(open(image_file), 1):
                if i in each:
                    line = line.strip('\n')
                    shutil.move(line, tracked_images_path)
            create_trapped_list(userId, sectionId)
            yolo_classify_trap_one_by_one(userId, sectionId)
            display_results.merge_test_and_result(userId, sectionId)
            display_results.make_files_list(report_count, len(fine_index_trapped), len(coarse_index_trapped), userId, sectionId)
            display_results.merge_pdf(report_count, userId, sectionId)

            report_count = report_count + 1
        else:
            continue

    display_results.final_report_pdf(userId, sectionId)
    #shutil.rmtree(test_data_dir + '/u-' + userId + '/s-' + sectionId + '/')

    return len(fine_index_trapped), len(coarse_index_trapped)

