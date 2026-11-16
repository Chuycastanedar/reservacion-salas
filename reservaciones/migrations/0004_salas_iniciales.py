from django.db import migrations

SALAS = [
    ('Sala A', 'Biblioteca, planta baja', 4, True),
    ('Sala B', 'Biblioteca, planta baja', 8, True),
    ('Sala C', 'Biblioteca, planta alta', 12, True),
    ('Sala de mantenimiento', 'Biblioteca, planta alta', 6, False),
]


def cargar_salas(apps, schema_editor):
    Sala = apps.get_model('reservaciones', 'Sala')
    for nombre, ubicacion, capacidad, activa in SALAS:
        Sala.objects.get_or_create(
            nombre=nombre,
            defaults={
                'ubicacion': ubicacion,
                'capacidad': capacidad,
                'activa': activa,
            },
        )


def borrar_salas(apps, schema_editor):
    Sala = apps.get_model('reservaciones', 'Sala')
    nombres = [nombre for nombre, *_ in SALAS]
    Sala.objects.filter(nombre__in=nombres).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('reservaciones', '0003_alter_reservacion_estado'),
    ]

    operations = [
        migrations.RunPython(cargar_salas, borrar_salas),
    ]
