

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('cazare', '0003_camera_tip_baie_profil_detalii_admin_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profil',
            name='status_cazare',
            field=models.CharField(choices=[('in_asteptare', 'În așteptare'), ('cazat', 'Cazat'), ('decazat', 'Decazat')], default='in_asteptare', max_length=20, verbose_name='Status Cazare'),
        ),
    ]
