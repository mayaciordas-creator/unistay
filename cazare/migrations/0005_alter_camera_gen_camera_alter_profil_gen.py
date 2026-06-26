

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('cazare', '0004_profil_status_cazare'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camera',
            name='gen_camera',
            field=models.CharField(choices=[('B', 'Băieți'), ('F', 'Fete')], default='B', max_length=4, verbose_name='Gen cameră'),
        ),
        migrations.AlterField(
            model_name='profil',
            name='gen',
            field=models.CharField(choices=[('B', 'Băieți'), ('F', 'Fete')], default='B', max_length=1, verbose_name='Gen'),
        ),
    ]
