from django.http import JsonResponse
from django.shortcuts import redirect

from utilities import get_file_list, get_file_metadata, make_file_public, get_server_origin


def api_get_file_list(request):
    json_data = {}
    if request.method == 'GET':
        json_data = get_file_list('/projects/water/nwm/nwm_sample')
    else:
        json_data['status_code'] = 405
        json_data['reason_phrase'] = 'Request must be of type "GET"'

    return JsonResponse(json_data, safe=False)


def api_get_file(request):
    json_data = {}

    if request.method == 'GET':
        if request.GET.get('filename'):
            file_path = '/projects/water/nwm/nwm_sample/' + request.GET['filename']
            url = make_file_public(file_path, get_server_origin(request))
            return redirect(url)
        else:
            json_data['status_code'] = 400
            json_data['reason_phrase'] = 'The \'filename\' parameter must be included in the request'
    else:
        json_data['status_code'] = 405
        json_data['reason_phrase'] = 'Request must be of type "GET"'

    return JsonResponse(json_data)


def api_get_file_metadata(request):
    json_data = {}

    if request.method == 'GET':
        if request.GET.get('filename'):
            json_data = get_file_metadata('/projects/water/nwm/nwm_sample/' + request.GET['filename'])
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
