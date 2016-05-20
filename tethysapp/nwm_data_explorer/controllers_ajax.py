from django.http import JsonResponse, FileResponse

import os
from shutil import rmtree
from utilities import data_query, get_temp_folder_path, get_server_origin, make_file_public, format_selection_path, zip_files, temp_dir


def get_folder_contents(request):
    print "GETTING FOLDER CONTENTS"
    if request.method == 'GET':
        selection_path = request.GET['selection_path']
        query_type = request.GET['query_type']
        filters_list = request.GET['filters_list'].split(',')
        if request.GET.get('show_georef'):
            show_georef = True if str(request.GET['show_georef']) == 'true' else False
        else:
            show_georef = None
        query_data = data_query(query_type, selection_path, filters_list, show_georef)

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
    if request.method == 'GET' and request.is_ajax():
        selection_path = request.GET['selection_path']
        selection_path = format_selection_path(selection_path)
        make_file_public(selection_path, get_server_origin(request))

        return JsonResponse({
            'success': 'File sucessfully made public.'
        })


def download_files(request):
    if request.method == 'GET':
        selection_dir = str(request.GET['selection_dir'])
        files = request.GET['files'].split(',')
        zip_path = zip_files(selection_dir, files)

        response = FileResponse(open(zip_path, 'rb'), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="' + 'nwm_data.zip"'
        response['Content-Length'] = os.path.getsize(zip_path)

        return response


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
