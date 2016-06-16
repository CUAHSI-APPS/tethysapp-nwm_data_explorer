from django.http import JsonResponse

from utilities import get_files_list, get_file_metadata, get_file_response_object, validate_data, generate_filters_dict

import os

root_path = '/projects/water/nwm/data'


def api_get_file_list(request):
    global root_path
    json_data = {}
    if request.method == 'GET':
        config = None
        start_date_raw = None
        end_date_raw = None
        time = None
        geom = None
        member = None

        if request.GET.get('config'):
            config = request.GET['config']
        if request.GET.get('startDate'):
            start_date_raw = request.GET['startDate']
        if request.GET.get('endDate'):
            end_date_raw = request.GET['endDate']
        if request.GET.get('time'):
            time = request.GET['time']
        if request.GET.get('geom'):
            geom = request.GET['geom']
        if request.GET.get('member'):
            member = request.GET['member']

        data_is_valid, message = validate_data(config, start_date_raw, end_date_raw, root_path, time, geom, member)

        if not data_is_valid:
            json_data['status_code'] = 400
            json_data['reason_phrase'] = message
        else:
            path = os.path.join(root_path, config) if config == 'analysis_assim' \
                else os.path.join(root_path, config, ''.join(start_date_raw.split('-')))
            filters_dict = generate_filters_dict(config, start_date_raw, end_date_raw, time, geom, member)
            files_list = get_files_list(path, filters_dict=filters_dict)

            if len(files_list) == 0:
                json_data['status_code'] = 200
                json_data['reason_phrase'] = 'No files matched your query.'
            else:
                modified_files_list = []
                for f in files_list:
                    modified_files_list.append(f.split(root_path)[1][1:].replace('/', '-'))
                json_data = modified_files_list
    else:
        json_data['status_code'] = 405
        json_data['reason_phrase'] = 'Request must be of type "GET"'

    return JsonResponse(json_data, safe=False)


def api_get_file(request):
    global root_path
    json_data = {}

    if request.method == 'GET':
        if request.GET.get('file'):
            file_path = os.path.join(root_path, request.GET['file'].replace('-', '/'))
            if os.path.exists(file_path):
                return get_file_response_object(file_path, None)
            else:
                json_data['status_code'] = 400
                json_data['reason_phrase'] = 'The file specified does not exist. ' \
                                             'Make sure it exactly matches a string returned by the GetFileList method.'
        else:
            json_data['status_code'] = 400
            json_data['reason_phrase'] = 'The file parameter must be included in the request'
    else:
        json_data['status_code'] = 405
        json_data['reason_phrase'] = 'Request must be of type "GET"'

    return JsonResponse(json_data)


def api_get_file_metadata(request):
    global root_path
    json_data = {}

    if request.method == 'GET':
        if request.GET.get('file'):
            file_path = os.path.join(root_path, request.GET['file'].replace('-', '/'))
            if os.path.exists(file_path):
                json_data = get_file_metadata(file_path)
            else:
                json_data['status_code'] = 400
                json_data['reason_phrase'] = 'The file specified does not exist. ' \
                                             'Make sure it exactly matches a string returned by the GetFileList method.'
        else:
            json_data['status_code'] = 400
            json_data['reason_phrase'] = 'The file parameter must be included in the request'
    else:
        json_data['status_code'] = 405
        json_data['reason_phrase'] = 'Request must be of type "GET"'

    return JsonResponse(json_data, safe=False)
