from django.shortcuts import render
# from django.contrib.auth.decorators import login_required

# @login_required
def setup_dashboard(request):
    # Only returns the HTML shell. The JS inside will fetch the actual data.
    return render(request, 'ui/setup.html')

# @login_required
def score_keeper(request):
    return render(request, 'ui/score_keeper.html')

def score_display(request):
    # Might not need login if you want this to be a public screen
    return render(request, 'ui/display.html')
