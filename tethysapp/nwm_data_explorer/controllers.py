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

    context = {}

    return render(request, 'nwm_data_explorer/data_explorer.html', context)


@login_required()
def api_info(request):
    """
    Controller for the app info page.
    """

    context = {}

    return render(request, 'nwm_data_explorer/api_info.html', context)
