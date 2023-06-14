from functools import wraps
from django.shortcuts import redirect

def manager_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'manager'):
            # request.is_manager = True
            return view_func(request, *args, **kwargs)
        else:
            return redirect('login')
        
    return wrapper

def set_role(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'manager'):
            request.is_manager = True
            request.is_ratte = False
            return view_func(request, *args, **kwargs)
        elif hasattr(request.user, 'ratte'):
            request.is_ratte = True
            request.is_manager = False
            return view_func(request, *args, **kwargs)
        else:
            request.is_manager = False
            request.is_ratte = False
            return redirect('login')
        
    return wrapper
