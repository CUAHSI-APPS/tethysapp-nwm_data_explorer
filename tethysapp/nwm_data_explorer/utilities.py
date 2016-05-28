from django.http import FileResponse

import os
import requests
from requests.auth import HTTPBasicAuth
from pwd import getpwuid
from inspect import getfile, currentframe
from json import loads

import zipfile
import random
import datetime

temp_dir = '/tmp/nwm_data'


def data_query(query_type, selection_path, filters_list):
    response = None
    contents = []
    contains_folder = False

    resource = 'collection' if '?folder' in selection_path else 'dataObject'
    selection_path = format_selection_path(selection_path)

    if query_type == 'filesystem':
        if os.path.exists(selection_path):
            if os.path.isdir(selection_path):
                files_list = get_files_list(selection_path, filters_list)
                for f in files_list:
                    f_type = 'folder' if os.path.isdir(f) else 'file'
                    f_name = os.path.basename(f)

                    if not contains_folder and f_type == 'folder':
                        contains_folder = True

                    select_option = '<option data-filename="%s" class="%s" data-path="%s">%s</option>' % \
                                    (f_name, f_type, f + '?' + f_type, f_name)
                    contents.append(select_option)

            else:
                query_data = get_file_metadata(selection_path)
                return query_data

    else:
        headers = {'Accept': 'application/json'}
        auth = HTTPBasicAuth('nwm-reader', 'nwmreader')
        url = 'http://nwm.renci.org:1247/irods-rest/rest/' + resource + selection_path + '?listing=true'
        print url

        try:
            r = requests.get(url, headers=headers, auth=auth)
            response = r.json()
            entries_object = response['children']

            if not entries_object:
                raise

            entry_count = 1 if type(entries_object) == dict else len(entries_object)

            for i in range(0, entry_count):
                object_type = entries_object['objectType'] if type(entry_count) == dict \
                    else entries_object[i]['objectType']
                if object_type == 'COLLECTION':
                    data_type = 'folder'
                    folder_path = entries_object['pathOrName'] if type(entry_count) == dict \
                        else entries_object[i]['pathOrName']
                    last_dash_index = folder_path.rfind('/')
                    folder_name = folder_path[last_dash_index + 1:]
                    select_option = '<option value="%s" data-path="%s">%s</option>' % \
                                    (folder_name, folder_path + "?" + data_type, folder_name)
                    contents.append(select_option)
                else:
                    data_type = 'file'
                    file_name = entries_object['pathOrName'] if type(entry_count) == dict \
                        else entries_object[i]['pathOrName']
                    file_path = (entries_object['parentPath'] + '/' + file_name) if type(entry_count) == dict \
                        else (entries_object[i]['parentPath'] + '/' + file_name)
                    select_option = '<option value="%s" data-path="%s">%s</option>' % \
                                    (file_name, file_path + "?" + data_type, file_name)
                    contents.append(select_option)

        except Exception as e:
            print "An error ocurred"
            print str(e)
            if resource == "collection":
                contents = '<select title="This folder is empty" class="files"><option></option></select>'
                query_data = {
                    'contents': contents
                }
                return query_data
            else:
                query_data = response if response else "An error occured"
                # if response:
                #     query_data = build_table_from_json(response)
                # else:
                #     query_data = "An error occured"
                return query_data

    if contents:
        contents.insert(0, '<select title="Select a file/folder" class="contents"><option></option>')
    else:
        contents.append('<select title="Select a file/folder" class="contents"><option></option>')
    contents.append('</select>')
    contents = ''.join(contents)

    query_data = {
        'contents': contents,
        'contains_folder': contains_folder
    }

    return query_data


def get_files_list(selection_path, filters_list=None):
    files_list = []
    raw_files_list = os.listdir(selection_path)
    raw_files_list.sort()
    for f in raw_files_list:
        full_path = os.path.join(selection_path, f)
        filter_out = False
        if filters_list is not None or (filters_list and len(filters_list) > 0):
            if not os.path.isdir(os.path.join(selection_path, f)):
                for filter_val in filters_list:
                    if filter_val != '':
                        if str(filter_val) not in str(f):
                            filter_out = True
                            break
        if not filter_out:
            files_list.append(full_path)

    return files_list


def get_file_metadata(selection_path):
    file_stats = os.stat(selection_path)
    file_name = os.path.basename(selection_path)
    return {
        'dataName': file_name,
        'dataSize': file_stats.st_size,
        'dataOwnerName': getpwuid(file_stats.st_uid).pw_name,
        'accessedAt': file_stats.st_atime * 1000,
        'updatedAt': file_stats.st_mtime * 1000
    }


def get_temp_folder_path():
    this_file_path = getfile(currentframe())
    this_filename = os.path.basename(this_file_path)
    return this_file_path.replace(this_filename, 'public/temp_files')


def build_table_from_json(json_obj):
    html = '<table><tr><th>'
    if type(json_obj) != object:
        json_obj = loads(json_obj)
    for key in json_obj:
        print key

    return html


def format_selection_path(selection_path):
    object_type_index = selection_path.rfind('?')
    if object_type_index == -1:
        return selection_path
    else:
        return selection_path[0:object_type_index]


def zip_files(directory, files):
    global temp_dir
    temp_file = 'zip' + str(random.randint(0, 100000))

    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    while os.path.exists(os.path.join(temp_dir, temp_file)):
        temp_file = 'zip' + str(random.randint(0, 100000))

    zip_path = os.path.join(temp_dir, temp_file)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, False) as zip_object:
            for each_file in files:
                zip_object.write(os.path.join(directory, each_file), each_file)
            zip_object.close()

    return zip_path


def get_file_response_object(file_path, content_type):
    response = FileResponse(open(file_path, 'rb'), content_type=content_type)
    if content_type is None:
        response['Content-Disposition'] = 'attachment; filename="' + os.path.basename(file_path)
    else:
        response['Content-Disposition'] = 'attachment; filename="' + 'nwm_data.zip"'
    response['Content-Length'] = os.path.getsize(file_path)

    return response


def validate_data(config, date_string, root_path, time=None, data_type=None):
    is_valid = True
    message = 'Data is valid.'
    configs = ['short_range', 'medium_range', 'long_range']
    data_types = ['channel', 'land', 'reservoir', 'terrain']

    while True:
        if config is None:
            is_valid = False
            message = 'The "config" parameter must be included in the request'
            break
        if date_string is None:
            is_valid = False
            message = 'The "config" parameter must be included in the request'
            break
        if config not in configs:
            is_valid = False
            message = 'Invalid config. ' \
                      'Choose one of the following: short_range, medium_range, long_range'
            break

        try:
            datetime.datetime.strptime(date_string, '%Y-%m-%d')
        except ValueError:
            is_valid = False
            message = 'Incorrect date format. Should be YYYY-MM-DD'
            break

        if time:
            try:
                int(time)
            except ValueError:
                is_valid = False
                message = 'Incorrect time format. Should be hh. ' \
                          'For example, "00" for 12:00AM, "01" for 1:00AM, up to "23" for 11:00PM'
                break
        if data_type:
            if data_type not in data_types:
                is_valid = False
                message = 'Invalid data_type. ' \
                          'Choose one of the following: channel, land, reservoir, or terrain'
                break
        if not os.path.exists(os.path.join(root_path, config, ''.join(date_string.split('-')))):
            is_valid = False
            message = 'There is no data stored for the startDate specified.'
            break
        break

    return is_valid, message
