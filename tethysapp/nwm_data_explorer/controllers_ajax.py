from django.http import JsonResponse

import os
from shutil import rmtree
from utilities import data_query, get_temp_folder_path


def get_folder_contents(request):
    print "GETTING FOLDER CONTENTS"
    if request.method == 'GET':
        selection_path = request.GET['selection_path']
        query_type = request.GET['query_type']
        query_data = data_query(query_type, selection_path, request.get_host())

        if query_data == 'An error occured':
            return JsonResponse({
                'error': "An error occured while retrieving the data."
            })
        else:
            return JsonResponse({
                'success': "Response successfully returned!",
                'query_data': query_data
            })


def delete_temp_files(request):
    if request.method == 'GET' and request.is_ajax():
        temp_folder_path = get_temp_folder_path()
        if os.path.exists(temp_folder_path):
            rmtree(temp_folder_path)

        return JsonResponse({
            'success': 'Temp folder successfully deleted.'
        })
