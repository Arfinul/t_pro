import sys, datetime, time
import os
import threading
from os import listdir
from os.path import isfile, join
import ntpath
import math
from hurry.filesize import size
from sh import git
import boto3
from boto3.s3.transfer import TransferConfig


# AWS related global variables
s3_client = boto3.client('s3', aws_access_key_id='AKIAZ47ERKTBHM6BHB5R', aws_secret_access_key='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')

# S3 bucket name. Can be changed
S3_BUCKET = 'tragnext-vid-dev'

# Setting directory paths
SCAN_VID_DIR = os.path.join(os.environ['HOME'], "Documents","tragnext","flc_utils","trainVideo","testing")
# Maximum size of the directory which can be configured.
MAX_SIZE = 5

# Dict of file and their upload progress
file_prog_map = {}

# Progress percentage in CLI
class ProgressPercentage(object):
        def __init__(self, filename):
            self._local_file_name = filename
            self._filename = os.path.join(SCAN_VID_DIR, filename)
            self._size = float(os.path.getsize(self._filename))
            self._seen_so_far = 0
            self._lock = threading.Lock()

        def __call__(self, bytes_amount):
            # To simplify we'll assume this is hooked up
            # to a single filename.
            with self._lock:
                self._seen_so_far += bytes_amount
                percentage = (self._seen_so_far / self._size) * 100
                sys.stdout.write(
                    "\r%s  %s / %s  (%.2f%%)" % (
                        self._filename, self._seen_so_far, self._size,
                        percentage))
                if percentage == 100:
                    file_prog_map[self._local_file_name] = percentage
                sys.stdout.flush()

# Method to get the directory size recursively
def get_size(start_path = SCAN_VID_DIR):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

def get_files_by_file_size(dirname, reverse=True):
    """ Return list of file paths in directory sorted by file size """

    # Get list of files
    filepaths = []
    file_names = []
    for basename in os.listdir(dirname):
        filename = os.path.join(dirname, basename)
        if os.path.isfile(filename):
            filepaths.append(filename)

    # Re-populate list with filename, size tuples
    for i in range(len(filepaths)):
        filepaths[i] = (filepaths[i], os.path.getsize(filepaths[i]))

    # Sort list by file size
    # If reverse=True sort from largest to smallest
    # If reverse=False sort from smallest to largest
    filepaths.sort(key=lambda filename: filename[1], reverse=reverse)

    # Re-populate list with just filenames
    for i in range(len(filepaths)):
    	# print(filepaths[i][0])
        filepaths[i] = filepaths[i][0]
        file_names.append(ntpath.basename(filepaths[i]))

    return file_names

def track_uploading(file_name_, file_size_, time_):
    f = open('s3_upload_info.csv','a')
    client_ = "Arfin_Agnext"
    dt_ = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    f.write(f"{client_},{dt_},{file_name_},{file_size_},{time_}\n")
    f.close()

# File operation to delete or list or whatever
def fileOps():
    no_of_files = 0
    
    # Check for 1. SIZE of Directory. 2. Minimum two videos
    if (get_size()/(1024*1024)) > MAX_SIZE:
        # Call the upload function
        # to start uploading to s3
        no_of_files = len([name for name in os.listdir(SCAN_VID_DIR) \
                        if os.path.isfile(os.path.join(SCAN_VID_DIR, name))])
        if no_of_files > 0:
            # Get list of all the files
            # list_of_files = os.listdir(SCAN_VID_DIR)
            list_of_files = get_files_by_file_size(SCAN_VID_DIR)
            while no_of_files > 0:
                start = time.time()
                file_size_ = os.path.getsize(os.path.join(SCAN_VID_DIR,list_of_files[no_of_files - 1]))/(1024*1024)
                uploadVidsToS3(list_of_files[no_of_files - 1])
                end = time.time()
                track_uploading(list_of_files[no_of_files - 1],round(file_size_,2),round(end-start,2))
                os.remove(os.path.join(SCAN_VID_DIR, list_of_files[no_of_files - 1]))
                no_of_files -= 1
            
            # Current done, now clearing the variables to avoid abnormal behaviour 
            if no_of_files == 0:
                file_prog_map = {}
    else:
        # else go on with polling
        print("Directory size within safe range: Wait continues...")
        print("Current Size: " + str(get_size()/(1024*1024)))

# Method to upload video files to S3 in multipart fashion
def uploadVidsToS3(file_to_upload):

    # Setting up transfer config for s3 upload. Can be configured
    config = TransferConfig(
                    multipart_threshold=1024*25, 
                    max_concurrency=10,
                    multipart_chunksize=1024*25, 
                    use_threads=True)
    
    # Setting the file name and the key name inside the s3 bucket
    file = os.path.join(SCAN_VID_DIR, file_to_upload)
    key = file_to_upload

    # Actual uploading part. The files are serially uploaded.
    # 
    # To make it more effiecient, depending upon the internet speed
    #   we can paralellize or serialize the upload for multiple files

    s3_client.upload_file(
            file, 
            S3_BUCKET, 'Arfin_Agnext/{}'.format(key),
            ExtraArgs={'ContentType': 'video/mp4'},
            Config = config,
            Callback = ProgressPercentage(file_to_upload)
            )

# Main method to call
SCAN_VID_DIR = os.path.join(os.environ['HOME'], "Documents","tragnext","flc_utils","trainVideo","testing")

path_to_watch = SCAN_VID_DIR
print('S3 upload started ....')
before = dict ([(f, None) for f in os.listdir (path_to_watch)])
while 1:
        after = dict ([(f, None) for f in os.listdir (path_to_watch)])
        added = [f for f in after if not f in before]
        if added:
                fileOps()
        else:
             before = after
