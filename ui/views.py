from django.shortcuts import render
from core.models import Contestant, ContestantGroup, Event, Show
from state.models import ServerState
# from django.contrib.auth.decorators import login_required

# @login_required
def setup_dashboard(request):
    # Only returns the HTML shell. The JS inside will fetch the actual data.
    return render(request, 'ui/setup.html')

# @login_required
def score_keeper(request):
    server_state = ServerState.get_state()
    event = server_state.current_event
    all_contestants = None
    context = {}
    active_event = server_state.current_event
    if event.group_size == 1 :
        all_contestants = active_event.registered_contestants.all().order_by('show_number')
        context = {
            'contestants': all_contestants
        }
    else:
        groups = ContestantGroup.objects.filter(events=active_event)
        context = {
            'contestants': groups,
            'is_group':  (event.group_size > 1)
        }


    return render(request, 'ui/score_keeper_all.html', context)

def score_display(request):
    # Might not need login if you want this to be a public screen
    return render(request, 'ui/display.html')
