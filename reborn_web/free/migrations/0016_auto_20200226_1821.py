# Generated by Django 3.0.2 on 2020-02-26 09:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('free', '0015_auto_20200226_1814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='writer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='댓글작성자'),
        ),
    ]
