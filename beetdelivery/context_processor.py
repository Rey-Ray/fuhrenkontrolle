import datetime

def current_time(request):
    now = datetime.datetime.now().time()
    return {'current_time': now}