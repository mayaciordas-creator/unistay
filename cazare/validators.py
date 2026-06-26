import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class SpecialCharacterValidator:
    """
    Validare personalizată: parola trebuie să conțină cel puțin
    un caracter special din lista de caractere definite.
    """
    def validate(self, password, user=None):
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("Parola trebuie să conțină cel puțin un caracter special (ex: !@#$%^&*)."),
                code='password_no_special_character',
            )

    def get_help_text(self):
        return _("Parola ta trebuie să conțină cel puțin un caracter special.")

class UppercaseValidator:
    """
    Parola trebuie să conțină cel puțin o literă mare.
    """
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Parola trebuie să conțină cel puțin o literă majusculă (A-Z)."),
                code='password_no_uppercase',
            )

    def get_help_text(self):
        return _("Parola trebuie să conțină cel puțin o majusculă.")

class NumberValidator:
    """
    Parola trebuie să conțină cel puțin o cifră.
    """
    def validate(self, password, user=None):
        if not re.search(r'\d', password):
            raise ValidationError(
                _("Parola trebuie să conțină cel puțin o cifră (0-9)."),
                code='password_no_number',
            )

    def get_help_text(self):
        return _("Parola trebuie să conțină cel puțin o cifră.")
