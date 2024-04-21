# Generated by Django 5.0.4 on 2024-04-19 23:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("medico", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DadosMedico",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("crm", models.CharField(max_length=255)),
                ("nome", models.CharField(max_length=255)),
                ("cep", models.CharField(max_length=255)),
                ("rua", models.CharField(max_length=255)),
                ("bairro", models.CharField(max_length=255)),
                ("numero", models.IntegerField()),
                ("rg", models.ImageField(upload_to="rgs")),
                ("cedula_identidade_medica", models.ImageField(upload_to="cim")),
                ("foto", models.ImageField(upload_to="fotos_perfil")),
                ("descricao", models.TextField()),
                ("valor_consulta", models.FloatField(default=100)),
                (
                    "especialidade",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="medico.especialidades",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
