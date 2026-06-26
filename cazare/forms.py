"""
Formularele aplicației de cazare.

Formularele sunt clase Python care generează câmpuri HTML
și validează datele trimise de utilizator.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profil, Camera, Rezervare


class InregistrareForm(UserCreationForm):
    """
    Formular de înregistrare pentru utilizatori noi.
    Extinde formularul standard UserCreationForm cu câmpuri suplimentare.
    """

    # Câmpuri suplimentare pentru înregistrare
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'exemplu@email.com'
        })
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        label='Prenume',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prenumele tău'
        })
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        label='Nume',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Numele tău'
        })
    )
    telefon = forms.CharField(
        max_length=15,
        required=False,
        label='Telefon',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '07XX XXX XXX'
        })
    )
    facultate = forms.CharField(
        max_length=200,
        required=False,
        label='Facultatea',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Facultatea de Informatică'
        })
    )
    detalii_admin = forms.CharField(
        max_length=300,
        required=False,
        label='Cămin administrat / Universitate',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ex. Căminul 1 / Universitatea X'
        })
    )
    an_studiu = forms.IntegerField(
        required=False,
        label='Anul de studiu',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '1',
            'min': 1,
            'max': 6
        })
    )
    rol = forms.ChoiceField(
        choices=Profil.ROL_CHOICES,
        initial='student',
        label='Tip cont',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    gen = forms.ChoiceField(
        choices=Profil.GEN_CHOICES,
        initial='B',
        label='Gen',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email',
                  'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adaugă clasa Bootstrap la câmpurile standard
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Numele de utilizator'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Parola'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmă parola'
        })

    def save(self, commit=True):
        """
        Salvează utilizatorul. Profilul se creează separat prin save_profile().
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

    def save_profile(self, user):
        """
        Creează profilul asociat utilizatorului.
        Apelată separat după salvarea utilizatorului.
        """
        Profil.objects.create(
            user=user,
            rol=self.cleaned_data['rol'],
            telefon=self.cleaned_data.get('telefon', ''),
            facultate=self.cleaned_data.get('facultate', ''),
            an_studiu=self.cleaned_data.get('an_studiu'),
            gen=self.cleaned_data.get('gen', 'B'),
            detalii_admin=self.cleaned_data.get('detalii_admin', ''),
        )



class CameraForm(forms.ModelForm):
    """
    Formular pentru adăugarea/editarea unei camere.
    Folosit de admin pentru managementul camerelor.
    """

    class Meta:
        model = Camera
        fields = ['numar', 'cladire', 'etaj', 'numar_locuri',
                  'locuri_disponibile', 'pret_lunar', 'gen_camera', 'tip_baie', 'descriere']
        widgets = {
            'numar': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ex: 101'
            }),
            'cladire': forms.Select(attrs={
                'class': 'form-control'
            }),
            'etaj': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'numar_locuri': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'locuri_disponibile': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'pret_lunar': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'descriere': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descriere opțională a camerei...'
            }),
        }


class RezervareForm(forms.ModelForm):
    """
    Formular pentru crearea unei rezervări.
    Studentul alege data de început și sfârșit.
    """

    class Meta:
        model = Rezervare
        fields = ['data_start', 'data_sfarsit', 'document_atasat']
        widgets = {
            'data_start': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_sfarsit': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'document_atasat': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
        }
        labels = {
            'data_start': 'Data de început',
            'data_sfarsit': 'Data de sfârșit',
            'document_atasat': 'Document atașat (CI / Adeverință)'
        }

    def clean(self):
        """Validare suplimentară: data de sfârșit trebuie să fie după data de început."""
        cleaned_data = super().clean()
        data_start = cleaned_data.get('data_start')
        data_sfarsit = cleaned_data.get('data_sfarsit')

        if data_start and data_sfarsit:
            if data_sfarsit <= data_start:
                raise forms.ValidationError(
                    'Data de sfârșit trebuie să fie după data de început.'
                )
        return cleaned_data


class CheckinForm(forms.Form):
    """
    Formular pentru check-in digital.
    Studentul sau recepționerul introduce codul unic al rezervării.
    """
    cod_unic = forms.CharField(
        max_length=50,
        label='Cod unic rezervare',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Introdu codul unic (ex: A1B2C3D4E5F6)',
            'autofocus': True
        })
    )
