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
        filters_dict = {}

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
                filters_dict['dates'] = [date]
                path = os.path.join(root_path, config)
            else:
                path = os.path.join(root_path, config, date)

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
                                             'Make sure it exactly matches the string returned in the GetFileList list.'
        else:
            json_data['status_code'] = 400
            json_data['reason_phrase'] = 'The \"file\" parameter must be included in the request'
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
                json_data = get_file_metadata(os.path.join(root_path, request.GET['file']))
            else:
                json_data['status_code'] = 400
                json_data['reason_phrase'] = 'The file specified does not exist. ' \
                                             'Make sure it exactly matches the string returned in the GetFileList list.'
        else:
            json_data['status_code'] = 400
            json_data['reason_phrase'] = 'The \"file\" parameter must be included in the request'
    else:
        json_data['status_code'] = 405
        json_data['reason_phrase'] = 'Request must be of type "GET"'

    return JsonResponse(json_data, safe=False)


def api_get_forecast_list(request):
    if request.method == 'GET':
        # TODO: Create this function
        pass
