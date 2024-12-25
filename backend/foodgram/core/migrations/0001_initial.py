# Generated by Django 3.2.16 on 2024-12-24 07:28

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
            name='ConfirmationCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('confirmation_code', models.CharField(blank=True, max_length=6, null=True, verbose_name='код доступа')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='confirmation_code', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Код подтверждения',
                'verbose_name_plural': 'Коды подтверждения',
            },
        ),
    ]
