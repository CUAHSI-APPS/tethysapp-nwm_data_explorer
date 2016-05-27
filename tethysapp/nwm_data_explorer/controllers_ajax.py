from django.http import JsonResponse

import os
from shutil import rmtree
from utilities import data_query, get_temp_folder_path, format_selection_path, zip_files, temp_dir, \
    get_file_response_object


def get_folder_contents(request):
    if request.method == 'GET':
        selection_path = request.GET['selection_path']
        query_type = request.GET['query_type']
        filters_list = request.GET['filters_list'].split(',')

        query_data = data_query(query_type, selection_path, filters_list)

        if query_data == 'An error occured':
            return JsonResponse({
                'error': "An error occured while retrieving the data."
            })
        else:
            return JsonResponse({
                'success': "Response successfully returned!",
                'query_data': query_data
            })


def download_file(request):
    if request.method == 'GET':
        selection_path = request.GET['selection_path']
        selection_path = format_selection_path(selection_path)

        return get_file_response_object(selection_path, None)


def download_files(request):
    if request.method == 'GET':
        selection_dir = str(request.GET['selection_dir'])
        files = request.GET['files'].split(',')
        zip_path = zip_files(selection_dir, files)

        return get_file_response_object(zip_path, 'application/zip')


def delete_temp_files(request):
    if request.method == 'GET' and request.is_ajax():
        temp_folder_path = get_temp_folder_path()
        if os.path.exists(temp_folder_path):
            rmtree(temp_folder_path)
        if os.path.exists(temp_dir):
            rmtree(temp_dir)
        return JsonResponse({
            'success': 'Temp folder successfully deleted.'
        })
