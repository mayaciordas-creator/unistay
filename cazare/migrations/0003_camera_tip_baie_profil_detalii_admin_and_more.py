

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('cazare', '0002_camera_gen_camera_plata_plata_recurenta_profil_gen'),
    ]

    operations = [
        migrations.AddField(
            model_name='camera',
            name='tip_baie',
            field=models.CharField(choices=[('camera', 'În cameră'), ('palier', 'Pe palier')], default='camera', max_length=10, verbose_name='Tip baie'),
        ),
        migrations.AddField(
            model_name='profil',
            name='detalii_admin',
            field=models.CharField(blank=True, max_length=300, verbose_name='Cămin administrat / Universitate (doar pentru Admin)'),
        ),
        migrations.AddField(
            model_name='rezervare',
            name='document_atasat',
            field=models.FileField(blank=True, null=True, upload_to='documente_rezervari/', verbose_name='Document atașat'),
        ),
        migrations.AlterField(
            model_name='rezervare',
            name='status',
            field=models.CharField(choices=[('pending', 'În așteptare'), ('confirmed', 'Confirmată'), ('checked_in', 'Check-in realizat'), ('cancelled', 'Anulată'), ('rejected', 'Respinsă')], default='pending', max_length=15, verbose_name='Status'),
        ),
    ]
