from django.http import JsonResponse

from utilities import get_files_list, get_file_metadata, get_file_response_object, validate_data

import os

root_path = '/projects/water/nwm/data'


def api_get_file_list(request):
    global root_path
    json_data = {}
    if request.method == 'GET':
        config = None
        date_string = None
        time = None
        data_type = None
        filters_list = []

        if request.GET.get('config'):
            config = request.GET['config']
        if request.GET.get('startDate'):
            date_string = request.GET['startDate']
        if request.GET.get('time'):
            time = request.GET['time']
        if request.GET.get('type'):
            data_type = request.GET['type']

        data_is_valid, message = validate_data(config, date_string, root_path, time, data_type)

        if not data_is_valid:
            json_data['status_code'] = 400
            json_data['reason_phrase'] = message
        else:
            date = ''.join(date_string.split('-'))

            if config == 'analysis_assim':
                filters_list.append(date)
                path = os.path.join(root_path, config)
            else:
                path = os.path.join(root_path, config, date)

            if time:
                filters_list.append('t' + time + 'z')

            if data_type:
                filters_list.append(data_type)

            files_list = get_files_list(path, filters_list=filters_list)

            if len(files_list) == 0:
                json_data['status_code'] = 200
                json_data['reason_phrase'] = 'No files matched your query.'
            else:
                json_data = files_list
    else:
        json_data['status_code'] = 405
        json_data['reason_phrase'] = 'Request must be of type "GET"'

    return JsonResponse(json_data, safe=False)


def api_get_file(request):
    global root_path
    json_data = {}

    if request.method == 'GET':
        if request.GET.get('filename'):
            file_path = os.path.join(root_path, request.GET['filename'])
            return get_file_response_object(file_path, None)
        else:
            json_data['status_code'] = 400
            json_data['reason_phrase'] = 'The \'filename\' parameter must be included in the request'
    else:
        json_data['status_code'] = 405
        json_data['reason_phrase'] = 'Request must be of type "GET"'

    return JsonResponse(json_data)


def api_get_file_metadata(request):
    global root_path
    json_data = {}

    if request.method == 'GET':
        if request.GET.get('filename'):
            json_data = get_file_metadata(os.path.join(root_path, request.GET['filename']))
        else:
            json_data['status_code'] = 400
            json_data['reason_phrase'] = 'The \'filename\' parameter must be included in the request'
    else:
        json_data['status_code'] = 405
        json_data['reason_phrase'] = 'Request must be of type "GET"'

    return JsonResponse(json_data, safe=False)


def api_get_forecast_list(request):
    if request.method == 'GET':
        # TODO: Create this function
        pass
