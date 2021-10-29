import os
import ntpath

def get_files_by_file_size(dirname, reverse=True):
    filepaths = []
    file_names = []
    for basename in os.listdir(dirname):
        filename = os.path.join(dirname, basename)
        if os.path.isfile(filename):
            filepaths.append(filename)

    for i in range(len(filepaths)):
        filepaths[i] = (filepaths[i], os.path.getsize(filepaths[i]))
    filepaths.sort(key=lambda filename: filename[1], reverse=reverse)\

    for i in range(len(filepaths)):
        filepaths[i] = filepaths[i][0]
        file_names.append(ntpath.basename(filepaths[i]))

    return file_names


def compress():
    no_of_files = len([name for name in os.listdir(path_to_watch) \
                        if os.path.isfile(os.path.join(path_to_watch, name))])
    if no_of_files > 0:
        # Get list of all the files
        list_of_files = get_files_by_file_size(path_to_watch)
        if 'result.avi' in list_of_files:
                list_of_files.remove('result.avi')
                no_of_files = no_of_files -1
        if 'ignore_me' in list_of_files:
                list_of_files.remove('ignore_me')
                no_of_files = no_of_files -1
        print("\n\n")
        print(list_of_files)
        print("\n\n")
        while no_of_files > 0:
            actual_name = os.path.splitext(list_of_files[no_of_files - 1])[0] + ".mp4"
            input_file = os.path.join(path_to_watch, list_of_files[no_of_files - 1])
            output_file = os.path.join(UPLOAD_DIR, "result.mp4")
            cmd = "ffmpeg -i " + input_file + " -vcodec libx265 -crf 22 " + output_file
            print("\n\n")
            print(cmd)
            print("\n\n")
            os.system(cmd)
            os.rename(output_file, os.path.join(UPLOAD_DIR,actual_name))
            os.remove(input_file)
            no_of_files -= 1

        # Current done, now clearing the variables to avoid abnormal behaviour 
        if no_of_files == 0:
            file_prog_map = {}
try:
    
    # Main method to call
    ROOT_DIR = os.path.join(os.environ['HOME'], "Documents","tragnext","flc_utils","trainVideo")
    path_to_watch = os.path.join(ROOT_DIR, "testing")

    print('\n\nvideo compression started ....\n\n')
    UPLOAD_DIR= os.path.join(ROOT_DIR, "upload_s3")
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    before = dict ([(f, None) for f in os.listdir (path_to_watch)])
    while 1:
            after = dict ([(f, None) for f in os.listdir (path_to_watch)])
            added = [f for f in after if not f in before]
            if added or len(path_to_watch):
                    compress()
            else:
                 before = after
except Exception as e:   
    print(e)