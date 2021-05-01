from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render


def login_required_handler(my_function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return my_function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('index'))

    return wrap


def misc_error_handler(my_function):
    def wrap(request, *args, **kwargs):
        try:
            return my_function(request, *args, **kwargs)
        except Exception as e:
            print(str(e))
            return render(request, "network/error.html", {
                'message': 'An unexpected error has occured.'
            })
    return wrap


def request_not_put_handler(my_function):
    def wrap(request, *args, **kwargs):
        if request.method == 'PUT':
            return my_function(request, *args, **kwargs)
        else:
            return render(request, "network/error.html", {
                'message': 'This is an invalid request. The request should be PUT.'
            })
    return wrap
