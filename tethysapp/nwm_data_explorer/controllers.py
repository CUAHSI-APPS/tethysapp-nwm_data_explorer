from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tethys_sdk.gizmos import ToggleSwitch

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

    toggle_georef = ToggleSwitch(display_text='Georeferenced',
                                 name='toggle-georef',
                                 on_label='Show',
                                 off_label='Hide',
                                 on_style='success',
                                 off_style='danger',
                                 initial=True,
                                 size='small')

    toggle_nongeoref = ToggleSwitch(display_text='Non-georeferenced',
                                    name='toggle-nongeoref',
                                    on_label='Show',
                                    off_label='Hide',
                                    on_style='success',
                                    off_style='danger',
                                    initial=True,
                                    size='small')
    vals = range(0, 24)

    for val in vals:
        if val < 10:
            hours[val] = 't0' + str(val) + 'z'
        else:
            hours[val] = 't' + str(val) + 'z'

    context = {
        'hours': hours,
        'toggle_georef': toggle_georef,
        'toggle_nongeoref': toggle_nongeoref
    }

    return render(request, 'nwm_data_explorer/data_explorer.html', context)


@login_required()
def api(request):
    """
    Controller for the app info page.
    """

    context = {}

    return render(request, 'nwm_data_explorer/api.html', context)
