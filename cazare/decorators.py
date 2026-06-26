"""
Decoratori personalizați pentru controlul accesului pe bază de rol.

Acești decoratori se aplică pe funcțiile view pentru a restricționa
accesul doar la utilizatorii cu rolul potrivit (admin sau student).
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    """
    Decorator care permite accesul doar administratorilor.
    Dacă utilizatorul nu este admin, este redirecționat la pagina principală.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            messages.warning(request, 'Trebuie să fii autentificat.')
            return redirect('login')

        if hasattr(request.user, 'profil') and request.user.profil.este_admin:
            return view_func(request, *args, **kwargs)

        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        messages.error(request, 'Nu ai permisiunea de a accesa această pagină.')
        return redirect('home')

    return wrapper

def student_required(view_func):
    """
    Decorator care permite accesul doar studenților.
    Dacă utilizatorul nu este student, este redirecționat la pagina principală.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            messages.warning(request, 'Trebuie să fii autentificat.')
            return redirect('login')

        if hasattr(request.user, 'profil') and request.user.profil.este_student:
            return view_func(request, *args, **kwargs)

        messages.error(request, 'Această pagină este doar pentru studenți.')
        return redirect('home')

    return wrapper
