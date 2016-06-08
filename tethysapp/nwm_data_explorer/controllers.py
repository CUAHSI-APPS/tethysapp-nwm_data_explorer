from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required()
def home(request):
    """
    Controller for the app info page.
    """

    context = {}

    return render(request, 'nwm_data_explorer/home.html', context)


@login_required()
def data_explorer(request):
    """
    Controller for the app home page.
    """

    hours_init = {}
    vals_init = range(0, 24)

    for val in vals_init:
        if val < 10:
            hours_init[val] = 't0' + str(val) + 'z'
        else:
            hours_init[val] = 't' + str(val) + 'z'

    context = {
        'hours_init': hours_init
    }

    return render(request, 'nwm_data_explorer/data_explorer.html', context)


@login_required()
def api(request):
    """
    Controller for the app info page.
    """
    host = 'https://%s' % request.get_host()

    context = {
        'host': host
    }

    return render(request, 'nwm_data_explorer/api.html', context)
