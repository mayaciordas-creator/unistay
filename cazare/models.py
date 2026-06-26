import uuid
from django.db import models
from django.contrib.auth.models import User

class Profil(models.Model):
    """
    Profilul utilizatorului - extinde modelul User din Django.
    Fiecare utilizator are un profil cu rol (admin sau student)
    și informații academice.
    """

    ROL_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Administrator'),
    ]

    GEN_CHOICES = [
        ('B', 'Băieți'),
        ('F', 'Fete'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profil'
    )
    rol = models.CharField(
        max_length=10,
        choices=ROL_CHOICES,
        default='student',
        verbose_name='Rol'
    )
    telefon = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='Număr de telefon'
    )
    facultate = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Facultatea'
    )
    an_studiu = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Anul de studiu'
    )
    gen = models.CharField(
        max_length=1,
        choices=GEN_CHOICES,
        default='B',
        verbose_name='Gen'
    )
    detalii_admin = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Cămin administrat / Universitate (doar pentru Admin)'
    )

    STATUS_CAZARE_CHOICES = [
        ('in_asteptare', 'În așteptare'),
        ('cazat', 'Cazat'),
        ('decazat', 'Decazat'),
    ]
    status_cazare = models.CharField(
        max_length=20,
        choices=STATUS_CAZARE_CHOICES,
        default='in_asteptare',
        verbose_name='Status Cazare'
    )

    class Meta:
        verbose_name = 'Profil'
        verbose_name_plural = 'Profile'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.rol})"

    @property
    def este_admin(self):
        """Verifică dacă utilizatorul este administrator."""
        return self.rol == 'admin'

    @property
    def este_student(self):
        """Verifică dacă utilizatorul este student."""
        return self.rol == 'student'

class Cladire(models.Model):
    """
    Modelul pentru o clădire de cămin.
    O clădire conține mai multe camere.
    """
    nume = models.CharField(
        max_length=100,
        verbose_name='Numele clădirii'
    )
    adresa = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Adresa'
    )
    numar_etaje = models.IntegerField(
        default=1,
        verbose_name='Număr de etaje'
    )

    class Meta:
        verbose_name = 'Clădire'
        verbose_name_plural = 'Clădiri'
        ordering = ['nume']

    def __str__(self):
        return self.nume

class Camera(models.Model):
    """
    Modelul pentru o cameră din cămin.
    Fiecare cameră aparține unei clădiri și are un număr limitat de locuri.
    """
    numar = models.CharField(
        max_length=10,
        verbose_name='Numărul camerei'
    )
    cladire = models.ForeignKey(
        Cladire,
        on_delete=models.CASCADE,
        related_name='camere',
        verbose_name='Clădirea',
        null=True,
        blank=True
    )
    etaj = models.IntegerField(
        default=0,
        verbose_name='Etajul'
    )
    numar_locuri = models.IntegerField(
        default=2,
        verbose_name='Număr total de locuri'
    )
    locuri_disponibile = models.IntegerField(
        default=2,
        verbose_name='Locuri disponibile'
    )
    pret_lunar = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=300.00,
        verbose_name='Preț lunar (RON)'
    )
    descriere = models.TextField(
        blank=True,
        verbose_name='Descriere'
    )

    GEN_CAMERA_CHOICES = [
        ('B', 'Băieți'),
        ('F', 'Fete'),
    ]
    gen_camera = models.CharField(
        max_length=4,
        choices=GEN_CAMERA_CHOICES,
        default='B',
        verbose_name='Gen cameră'
    )

    TIP_BAIE_CHOICES = [
        ('camera', 'În cameră'),
        ('palier', 'Pe palier'),
    ]
    tip_baie = models.CharField(
        max_length=10,
        choices=TIP_BAIE_CHOICES,
        default='camera',
        verbose_name='Tip baie'
    )

    class Meta:
        verbose_name = 'Cameră'
        verbose_name_plural = 'Camere'
        ordering = ['cladire', 'etaj', 'numar']
        unique_together = ['numar', 'cladire']

    def __str__(self):
        cladire_text = f" - {self.cladire.nume}" if self.cladire else ""
        return f"Camera {self.numar}{cladire_text} (Etaj {self.etaj})"

    @property
    def este_disponibila(self):
        """Verifică dacă camera mai are locuri disponibile."""
        return self.locuri_disponibile > 0

class Rezervare(models.Model):
    """
    Modelul pentru o rezervare.
    Leagă un student de o cameră, cu statusul rezervării
    și codul QR generat.
    """

    STATUS_CHOICES = [
        ('pending', 'În așteptare'),
        ('confirmed', 'Confirmată'),
        ('checked_in', 'Check-in realizat'),
        ('cancelled', 'Anulată'),
        ('rejected', 'Respinsă'),
    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rezervari',
        verbose_name='Student'
    )
    camera = models.ForeignKey(
        Camera,
        on_delete=models.CASCADE,
        related_name='rezervari',
        verbose_name='Camera'
    )
    data_start = models.DateField(verbose_name='Data de început')
    data_sfarsit = models.DateField(verbose_name='Data de sfârșit')
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    cod_unic = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Cod unic'
    )
    qr_code = models.ImageField(
        upload_to='qr_codes/',
        blank=True,
        null=True,
        verbose_name='Cod QR'
    )
    document_atasat = models.FileField(
        upload_to='documente_rezervari/',
        blank=True,
        null=True,
        verbose_name='Document atașat'
    )
    data_creare = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data creării'
    )

    class Meta:
        verbose_name = 'Rezervare'
        verbose_name_plural = 'Rezervări'
        ordering = ['-data_creare']

    def __str__(self):
        return f"Rezervare #{self.cod_unic[:8]} - {self.student.get_full_name() or self.student.username}"

    def save(self, *args, **kwargs):
        """
        Suprascrie metoda save() pentru a genera automat
        un cod unic dacă nu există deja.
        """
        if not self.cod_unic:
            self.cod_unic = uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)

class Plata(models.Model):
    """
    Modelul pentru o plată asociată unei rezervări.
    Fiecare rezervare poate avea o singură plată.
    """

    STATUS_CHOICES = [
        ('pending', 'În așteptare'),
        ('completed', 'Finalizată'),
        ('failed', 'Eșuată'),
    ]

    rezervare = models.OneToOneField(
        Rezervare,
        on_delete=models.CASCADE,
        related_name='plata',
        verbose_name='Rezervare'
    )
    suma = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Suma (RON)'
    )
    stripe_payment_id = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='ID plată Stripe'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status plată'
    )
    data_plata = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data plății'
    )
    plata_recurenta = models.BooleanField(
        default=False,
        verbose_name='Plată recurentă'
    )

    class Meta:
        verbose_name = 'Plată'
        verbose_name_plural = 'Plăți'
        ordering = ['-data_plata']

    def __str__(self):
        return f"Plată {self.suma} RON - {self.get_status_display()}"
