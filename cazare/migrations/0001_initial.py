

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Camera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numar', models.CharField(max_length=10, verbose_name='Numărul camerei')),
                ('etaj', models.IntegerField(default=0, verbose_name='Etajul')),
                ('numar_locuri', models.IntegerField(default=2, verbose_name='Număr total de locuri')),
                ('locuri_disponibile', models.IntegerField(default=2, verbose_name='Locuri disponibile')),
                ('pret_lunar', models.DecimalField(decimal_places=2, default=300.0, max_digits=8, verbose_name='Preț lunar (RON)')),
                ('descriere', models.TextField(blank=True, verbose_name='Descriere')),
            ],
            options={
                'verbose_name': 'Cameră',
                'verbose_name_plural': 'Camere',
                'ordering': ['cladire', 'etaj', 'numar'],
            },
        ),
        migrations.CreateModel(
            name='Cladire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nume', models.CharField(max_length=100, verbose_name='Numele clădirii')),
                ('adresa', models.CharField(blank=True, max_length=300, verbose_name='Adresa')),
                ('numar_etaje', models.IntegerField(default=1, verbose_name='Număr de etaje')),
            ],
            options={
                'verbose_name': 'Clădire',
                'verbose_name_plural': 'Clădiri',
                'ordering': ['nume'],
            },
        ),
        migrations.CreateModel(
            name='Rezervare',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_start', models.DateField(verbose_name='Data de început')),
                ('data_sfarsit', models.DateField(verbose_name='Data de sfârșit')),
                ('status', models.CharField(choices=[('pending', 'În așteptare'), ('confirmed', 'Confirmată'), ('checked_in', 'Check-in realizat'), ('cancelled', 'Anulată')], default='pending', max_length=15, verbose_name='Status')),
                ('cod_unic', models.CharField(max_length=50, unique=True, verbose_name='Cod unic')),
                ('qr_code', models.ImageField(blank=True, null=True, upload_to='qr_codes/', verbose_name='Cod QR')),
                ('data_creare', models.DateTimeField(auto_now_add=True, verbose_name='Data creării')),
                ('camera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rezervari', to='cazare.camera', verbose_name='Camera')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rezervari', to=settings.AUTH_USER_MODEL, verbose_name='Student')),
            ],
            options={
                'verbose_name': 'Rezervare',
                'verbose_name_plural': 'Rezervări',
                'ordering': ['-data_creare'],
            },
        ),
        migrations.CreateModel(
            name='Profil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rol', models.CharField(choices=[('student', 'Student'), ('admin', 'Administrator')], default='student', max_length=10, verbose_name='Rol')),
                ('telefon', models.CharField(blank=True, max_length=15, verbose_name='Număr de telefon')),
                ('facultate', models.CharField(blank=True, max_length=200, verbose_name='Facultatea')),
                ('an_studiu', models.IntegerField(blank=True, null=True, verbose_name='Anul de studiu')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profil', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profil',
                'verbose_name_plural': 'Profile',
            },
        ),
        migrations.CreateModel(
            name='Plata',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('suma', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Suma (RON)')),
                ('stripe_payment_id', models.CharField(blank=True, max_length=200, verbose_name='ID plată Stripe')),
                ('status', models.CharField(choices=[('pending', 'În așteptare'), ('completed', 'Finalizată'), ('failed', 'Eșuată')], default='pending', max_length=10, verbose_name='Status plată')),
                ('data_plata', models.DateTimeField(auto_now_add=True, verbose_name='Data plății')),
                ('rezervare', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='plata', to='cazare.rezervare', verbose_name='Rezervare')),
            ],
            options={
                'verbose_name': 'Plată',
                'verbose_name_plural': 'Plăți',
                'ordering': ['-data_plata'],
            },
        ),
        migrations.AddField(
            model_name='camera',
            name='cladire',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='camere', to='cazare.cladire', verbose_name='Clădirea'),
        ),
        migrations.AlterUniqueTogether(
            name='camera',
            unique_together={('numar', 'cladire')},
        ),
    ]
