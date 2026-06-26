"""
Tag-uri personalizate pentru template-uri Django.

Aceste tag-uri pot fi folosite în template-uri pentru a adăuga
funcționalități suplimentare (ex: verificarea rolului utilizatorului).
"""

from django import template

register = template.Library()

@register.filter
def este_admin(user):
    """
    Filtru care verifică dacă un utilizator este administrator.
    Utilizare în template: {% if user|este_admin %}...{% endif %}
    """
    if hasattr(user, 'profil'):
        return user.profil.este_admin
    return user.is_superuser

@register.filter
def este_student(user):
    """
    Filtru care verifică dacă un utilizator este student.
    Utilizare în template: {% if user|este_student %}...{% endif %}
    """
    if hasattr(user, 'profil'):
        return user.profil.este_student
    return False
