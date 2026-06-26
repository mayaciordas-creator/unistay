

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('cazare', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='camera',
            name='gen_camera',
            field=models.CharField(choices=[('M', 'Masculin'), ('F', 'Feminin'), ('mixt', 'Mixt')], default='mixt', max_length=4, verbose_name='Gen cameră'),
        ),
        migrations.AddField(
            model_name='plata',
            name='plata_recurenta',
            field=models.BooleanField(default=False, verbose_name='Plată recurentă'),
        ),
        migrations.AddField(
            model_name='profil',
            name='gen',
            field=models.CharField(choices=[('M', 'Masculin'), ('F', 'Feminin')], default='M', max_length=1, verbose_name='Gen'),
        ),
    ]
