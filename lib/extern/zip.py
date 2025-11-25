# import python modules
import zipfile
import sys
import os
import datetime

# create zip function
def ezip(files_to_zip, dirs_to_zip, output_zip_file):
    # open zip file
    zip_file = zipfile.ZipFile(output_zip_file, 'w', zipfile.ZIP_DEFLATED)
    # add files to zip file
    for file_to_zip in files_to_zip:
        # get path of file to zip
        relative_path = os.path.relpath(file_to_zip, os.path.dirname(output_zip_file))
        # add file to zip file
        zip_file.write(file_to_zip, relative_path)

    # add dirs to zip file
    for dir_to_zip in dirs_to_zip:
        for root, _, files in os.walk(dir_to_zip):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, os.path.dirname(output_zip_file))
                zip_file.write(file_path, relative_path)

    # close zip file
    zip_file.close()

# create function
def unzip(file, dir = '.'):
    # open zip file
    zip_file = zipfile.ZipFile(file, 'r')
    # create dir if it not exist
    if not os.path.exists(dir):
        os.mkdir(dir)
    # unzip all files/directory's
    list_info = zip_file.infolist()
    for info in list_info:
        path = zip_file.extract(info.filename, dir)
        date = datetime.datetime(*info.date_time)
        time = date.timestamp()
        os.utime(path, (time, time))
    # close zip file
    zip_file.close()
   
