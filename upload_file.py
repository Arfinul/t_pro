import sys
import os
import threading
from os import listdir
from os.path import isfile, join

import math
from hurry.filesize import size

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
            list_of_files = os.listdir(SCAN_VID_DIR)
            while no_of_files > 0:
                uploadVidsToS3(list_of_files[no_of_files - 1])
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
    #
    # For now its serially
    s3_client.upload_file(
            file, 
            S3_BUCKET, 'Nagrijuli/{}'.format(key),
            ExtraArgs={'ContentType': 'video/mp4'},
            Config = config,
            Callback = ProgressPercentage(file_to_upload)
            )

# Main method to call
fileOps()



# import os, csv, dic
# csv_path = os.path.join(os.environ['HOME'], "Documents","tragnext", "s3_upload.csv")
# file_exists = os.path.isfile(filename)
# csv_path = os.path.isfile('result.csv')
# if not os.path.exists(csv_path):
#     with open (csv_path, 'a') as csvfile:
# 	    # headers = ['Client', 'Size', 'Time', 'S3_Bucket_Folder']
# 	    headers = ['TimeStamp', 'light', 'Proximity']
# 	    writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n',fieldnames=headers)

#     if not csv_path:
#         writer.writeheader()  # file doesn't exist yet, write a header

#     writer.writerow({'TimeStamp': dic['ts'], 'light': dic['light'], 'Proximity': dic['prox']})

