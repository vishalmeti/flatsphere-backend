# Generated by Django 5.1.6 on 2025-03-01 10:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='userworkspace',
            name='role',
            field=models.CharField(choices=[('resident', 'Resident'), ('admin', 'Admin')], max_length=20),
        ),
        migrations.CreateModel(
            name='UserApartment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_primary_resident', models.BooleanField(default=True)),
                ('lease_start_date', models.DateField(blank=True, null=True)),
                ('lease_end_date', models.DateField(blank=True, null=True)),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='apartment_users', to='workspaces.apartmentunit')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_apartments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'UserApartmentUnit',
                'unique_together': {('user', 'unit')},
            },
        ),
    ]
