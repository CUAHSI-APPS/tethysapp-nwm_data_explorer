from django.http import JsonResponse

from requests.auth import HTTPBasicAuth
import requests
import os
from pwd import getpwuid
from shutil import copyfile, rmtree
from inspect import getfile, currentframe


def get_folder_contents(request):
    print "GETTING FOLDER CONTENTS"
    if request.method == 'GET':
        selection_path = request.GET['selection_path']
        query_type = request.GET['query_type']
        query_data = data_query(query_type, selection_path)

        if query_data == 'An error occured':
            return JsonResponse({
                'error': "An error occured while retrieving the data."
            })
        else:
            return JsonResponse({
                'success': "Response successfully returned!",
                'query_data': query_data
            })


def data_query(query_type, selection_path):
    response = None
    folders = []
    files = []

    resource = 'collection' if '?COLLECTION' in selection_path else 'dataObject'
    object_type_index = selection_path.rfind('?')
    selection_path = selection_path[0:object_type_index]

    if query_type == 'filesystem':
        if os.path.exists(selection_path):
            if os.path.isdir(selection_path):
                contents = os.listdir(selection_path)
                contents.sort()
                for f in contents:
                    select_option = '<option value="%s" data-path="%s">%s</option>' % \
                                    (f, os.path.join(selection_path, f) + "?FILE", f)
                    files.append(select_option)
            else:
                file_stats = os.stat(selection_path)
                file_name = os.path.basename(selection_path)
                query_data = {
                    'dataName': file_name,
                    'dataSize': file_stats.st_size,
                    'dataOwnerName': getpwuid(file_stats.st_uid).pw_name,
                    'accessedAt': file_stats.st_atime * 1000,
                    'updatedAt': file_stats.st_mtime * 1000
                }
                temp_folder_path = getfile(currentframe()).replace('controllers_ajax.py', 'public/temp_files')
                if not os.path.exists(temp_folder_path):
                    os.mkdir(temp_folder_path)
                temp_file_path = os.path.join(temp_folder_path, file_name)
                if not os.path.exists(temp_file_path):
                    copyfile(selection_path, temp_file_path)
                return query_data

    else:
        headers = {'Accept': 'application/json'}
        auth = HTTPBasicAuth('shawncrawley', 'shawncrawley')
        url = 'http://nfie.hydroshare.org:8080/irods-rest/rest/' + resource + selection_path + '?listing=true'

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
                if object_type == "COLLECTION":
                    folder_path = entries_object['pathOrName'] if type(entry_count) == dict \
                        else entries_object[i]['pathOrName']
                    last_dash_index = folder_path.rfind('/')
                    folder_name = folder_path[last_dash_index + 1:]
                    select_option = '<option value="%s" data-path="%s">%s</option>' % \
                                    (folder_name, folder_path + "?" + object_type, folder_name)
                    folders.append(select_option)
                else:
                    file_name = entries_object['pathOrName'] if type(entry_count) == dict \
                        else entries_object[i]['pathOrName']
                    file_path = (entries_object['parentPath'] + '/' + file_name) if type(entry_count) == dict \
                        else (entries_object[i]['parentPath'] + '/' + file_name)
                    select_option = '<option value="%s" data-path="%s">%s</option>' % \
                                    (file_name, file_path + "?" + object_type, file_name)
                    files.append(select_option)

        except Exception as e:
            print "An error ocurred"
            print str(e)
            if resource == "collection":
                folders = ''
                files = '<select title="No files to display" class="files"><option></option></select>'
                query_data = {
                    'folders': folders,
                    'files': files
                }
                return query_data
            else:
                query_data = response if response else "An error occured"
                return query_data

    if folders:
        folders.insert(0, '<select title="Select a directory" class="folders"><option></option>')
        folders.append('</select>')
        folders = ''.join(folders)

    if files:
        files.insert(0, '<select title="Select a file" class="files"><option></option>')
        files.append('</select>')
        files = ''.join(files)

    query_data = {
        'folders': folders,
        'files': files
    }

    return query_data


def delete_temp_files(request):
    temp_folder_path = getfile(currentframe()).replace('controllers_ajax.py', 'public/temp_files')
    if os.path.exists(temp_folder_path):
        rmtree(temp_folder_path)

    return JsonResponse({
        'success': 'Temp folder successfully deleted.'
    })
