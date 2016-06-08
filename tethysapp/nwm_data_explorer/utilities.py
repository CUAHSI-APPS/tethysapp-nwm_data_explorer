from django.http import FileResponse

import os
import requests
from requests.auth import HTTPBasicAuth
from pwd import getpwuid
from inspect import getfile, currentframe
from json import loads

import zipfile
import random
from datetime import datetime, timedelta
from hurry.filesize import size

temp_dir = '/tmp/nwm_data'


def data_query(query_type, selection_path, filters_dict):
    response = None
    contents = []
    contains_folder = False

    resource = 'collection' if '?folder' in selection_path else 'dataObject'
    selection_path = format_selection_path(selection_path)

    if query_type == 'filesystem':
        if os.path.exists(selection_path):
            if os.path.isdir(selection_path):
                files_list = get_files_list(selection_path, filters_dict)
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


def get_files_list(selection_path, filters_dict=None):
    files_list = []
    raw_files_list = os.listdir(selection_path)
    raw_files_list.sort()
    for f in raw_files_list:
        full_path = os.path.join(selection_path, f)
        filter_out = False
        if filters_dict is not None or (filters_dict and len(filters_dict) > 0):
            if not os.path.isdir(os.path.join(selection_path, f)):
                for key in filters_dict:
                    if not filter_out:
                        apply_filters = True
                        if key == 'members' and 'long_range' not in selection_path:
                            apply_filters = False
                        if key == 'dates' and 'analysis_assim' not in selection_path:
                            apply_filters = False
                        if apply_filters:
                            for filter_val in filters_dict[key]:
                                if str(filter_val) in str(f):
                                    filter_out = False
                                    break
                                else:
                                    filter_out = True
        if not filter_out:
            files_list.append(full_path)

    return files_list


def get_file_metadata(selection_path):
    file_stats = os.stat(selection_path)
    file_name = os.path.basename(selection_path)
    return {
        'dataName': file_name,
        'dataSize': size(file_stats.st_size),
        'dataOwnerName': getpwuid(file_stats.st_uid).pw_name,
        'accessedAt': datetime.fromtimestamp(file_stats.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
        'updatedAt': datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
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


def validate_data(config, start_date_raw, end_date_raw, root_path, time=None, data_type=None, member=None):
    is_valid = False
    message = 'Data is valid.'
    valid_configs = ['short_range', 'medium_range', 'long_range', 'analysis_assim']
    valid_data_types = ['channel', 'land', 'reservoir', 'terrain']

    while True:
        if config is None:
            message = 'The \"config\" parameter must be included in the request'
            break
        if start_date_raw is None and config != 'analysis_assim':
            message = 'The \"startDate\" parameter must be included in the request, unless config=analysis_assim'
            break
        if start_date_raw is None and end_date_raw is not None:
            message = 'The endDate parameter was included without a startDate parameter.'
            break
        if config not in valid_configs:
            message = 'Invalid config. ' \
                      'Choose one of the following: short_range, medium_range, long_range, analysis_assim'
            break
        if config != 'analysis_assim' and end_date_raw is not None:
            message = 'The endDate parameter is only applicable if config=analysis_assim'
            break
        if config != 'long_range' and member is not None:
            message = 'The member parameter is only applicable if config=long_range'
        try:
            if start_date_raw is not None:
                datetime.strptime(start_date_raw, '%Y-%m-%d')
            if end_date_raw is not None:
                datetime.strptime(end_date_raw, '%Y-%m-%d')
        except ValueError:
            message = 'Incorrect date format. Should be YYYY-MM-DD'
            break

        if end_date_raw and datetime.strptime(end_date_raw, '%Y-%m-%d') < datetime.strptime(start_date_raw, '%Y-%m-%d'):
            message = 'Invalid dates. The endDate is chronologically sooner than the startDate'
            break

        if time:
            try:
                times = time.split(',')
                if len(times) == 1:
                    times = time[0].split('-')
                    if len(times) > 2:
                        raise ValueError
                for t in times:
                    int(t)
                if len(times) > 24:
                    raise ValueError
            except ValueError:
                message = 'Incorrect time format. Each individual time must be an integer from 0 to 23. ' \
                          'Time 0 corresponds to 12AM, and so forth up to time 23 for 11PM. ' \
                          'If multiple times are desired, either separate each time by a comma ' \
                          'or separate a range of times with a dash. For example, "time=1,3,5" or "time=0-10".'
                break
        if data_type:
            data_types = data_type.split(',')
            for d_type in data_types:
                if d_type not in valid_data_types:
                    message = 'Invalid data_type specified. ' \
                              'You may only choose from the following: channel, land, reservoir, or terrain. ' \
                              'If specifying more than one, separate each with a comma.'
                    break
        if config != 'analysis_assim' \
                and not os.path.exists(os.path.join(root_path, config, ''.join(start_date_raw.split('-')))):
            message = 'There is no data stored for the startDate specified.'
            break
        if member:
            try:
                members = member.split(',')
                for m in members:
                    int(m)
                if len(members) > 4:
                    raise ValueError
            except ValueError:
                message = 'Incorrect member format. Each individual member must be an integer from 1 to 4. If ' \
                          'multiple members are desired, separate each member by a comma. For example, "member=1,3".'

        is_valid = True
        break

    return is_valid, message


def generate_date_list(start_date_raw, end_date_raw):
    date_list = []
    start_date = datetime.strptime(start_date_raw, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date_raw, "%Y-%m-%d").date()
    while start_date <= end_date:
        date_list.append(start_date.strftime('%Y%m%d'))
        start_date = start_date + timedelta(days=1)

    return date_list


def generate_filters_dict(config, start_date_raw, end_date_raw, time, data_type, member):
    filters_dict = {}
    start_date_str = None

    if start_date_raw:
        start_date_str = ''.join(start_date_raw.split('-'))

    if config == 'analysis_assim':
        if start_date_raw and end_date_raw:
            date_list = generate_date_list(start_date_raw, end_date_raw)
            filters_dict['dates'] = date_list
        elif start_date_raw and not end_date_raw:
            filters_dict['dates'] = [start_date_str]

    if time:
        times = time.split(',')
        if len(times) == 1:
            times = times[0].split('-')
            if len(times) > 1:
                times = range(int(times[0]), int(times[1]) + 1)
        for t in times:
            t_mod = '0%s' % t if int(t) < 10 else t
            if 'hours' in filters_dict:
                filters_dict['hours'].append('t%sz' % t_mod)
            else:
                filters_dict['hours'] = ['t%sz' % t_mod]

    if data_type:
        data_types = data_type.split(',')
        for d_type in data_types:
            if 'types' in filters_dict:
                filters_dict['types'].append(d_type)
            else:
                filters_dict['types'] = [d_type]
    if member:
        members = member.split(',')
        for m in members:
            if 'members' in filters_dict:
                filters_dict['members'].append('_%s.f' % m)
            else:
                filters_dict['members'] = ['_%s.f' % m]

    return filters_dict
