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

    hours = {}
    vals = range(0, 24)

    for val in vals:
        if val < 10:
            hours[val] = 't0' + str(val) + 'z'
        else:
            hours[val] = 't' + str(val) + 'z'

    context = {
        'hours': hours
    }

    return render(request, 'nwm_data_explorer/data_explorer.html', context)


@login_required()
def api(request):
    """
    Controller for the app info page.
    """

    context = {}

    return render(request, 'nwm_data_explorer/api.html', context)
