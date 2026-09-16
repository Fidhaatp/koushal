# Add Duration, Session, ModeOfStudy models and FK fields on BoardRegistration
# Data migration: populate new FKs from old char/int columns before altering

import django.db.models.deletion
from django.db import migrations, models, connection


def create_models_and_populate_fks(apps, schema_editor):
    """Create Session/Duration/ModeOfStudy, add new columns, populate from old data, drop old columns."""
    # 1. Create the new tables (already done by CreateModel operations before this)
    # 2. Add new columns (done by RunSQL before this)
    # 3. Populate: read old values and set new FK ids
    Course = apps.get_model('boardreg', 'Course')
    Session = apps.get_model('boardreg', 'Session')
    ModeOfStudy = apps.get_model('boardreg', 'ModeOfStudy')
    Duration = apps.get_model('boardreg', 'Duration')

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, course_id, session, mode_of_study, duration FROM boardreg_boardregistration"
        )
        rows = cursor.fetchall()

    for row_id, course_id, session_val, mode_val, duration_val in rows:
        if not course_id:
            continue
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            continue

        # Get or create Session (old value e.g. 'regular')
        session_name = (session_val or 'Regular').strip() or 'Regular'
        session_obj, _ = Session.objects.get_or_create(course=course, name=session_name)

        # Get or create ModeOfStudy (old value e.g. 'regular', 'fulltime')
        mode_name = (mode_val or 'Regular').strip() or 'Regular'
        mode_obj, _ = ModeOfStudy.objects.get_or_create(course=course, name=mode_name)

        # Get or create Duration (old value was integer years e.g. 3)
        if duration_val is not None:
            duration_name = f"{duration_val} Years"
        else:
            duration_name = "N/A"
        duration_obj, _ = Duration.objects.get_or_create(course=course, name=duration_name)

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE boardreg_boardregistration SET session_id = %s, mode_of_study_id = %s, duration_id = %s WHERE id = %s",
                [session_obj.id, mode_obj.id, duration_obj.id, row_id],
            )


def add_fk_columns(apps, schema_editor):
    """Add nullable FK columns so we can populate them before dropping old columns."""
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE boardreg_boardregistration ADD COLUMN session_id INTEGER NULL")
        cursor.execute("ALTER TABLE boardreg_boardregistration ADD COLUMN mode_of_study_id INTEGER NULL")
        cursor.execute("ALTER TABLE boardreg_boardregistration ADD COLUMN duration_id INTEGER NULL")


def drop_old_columns(apps, schema_editor):
    """Drop old session, mode_of_study, duration columns (SQLite 3.35+)."""
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE boardreg_boardregistration DROP COLUMN session")
        cursor.execute("ALTER TABLE boardreg_boardregistration DROP COLUMN mode_of_study")
        cursor.execute("ALTER TABLE boardreg_boardregistration DROP COLUMN duration")


def reverse_drop_old_columns(apps, schema_editor):
    """Re-add old columns for reverse migration (optional)."""
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE boardreg_boardregistration ADD COLUMN session VARCHAR(20) NULL")
        cursor.execute("ALTER TABLE boardreg_boardregistration ADD COLUMN mode_of_study VARCHAR(20) NULL")
        cursor.execute("ALTER TABLE boardreg_boardregistration ADD COLUMN duration INTEGER NULL")


def reverse_add_fk_columns(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE boardreg_boardregistration DROP COLUMN session_id")
        cursor.execute("ALTER TABLE boardreg_boardregistration DROP COLUMN mode_of_study_id")
        cursor.execute("ALTER TABLE boardreg_boardregistration DROP COLUMN duration_id")


class Migration(migrations.Migration):

    dependencies = [
        ('boardreg', '0010_remove_coursetype_application_fee_course_application_fee'),
    ]

    operations = [
        # 1. Create new models
        migrations.CreateModel(
            name='Duration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Duration Name')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_durations', to='boardreg.course')),
            ],
            options={
                'verbose_name': 'Duration',
                'verbose_name_plural': 'Durations',
                'unique_together': {('name', 'course')},
            },
        ),
        migrations.CreateModel(
            name='ModeOfStudy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Mode of Study Name')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_modes', to='boardreg.course')),
            ],
            options={
                'verbose_name': 'Mode of Study',
                'verbose_name_plural': 'Modes of Study',
                'unique_together': {('name', 'course')},
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Session Name')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_sessions', to='boardreg.course')),
            ],
            options={
                'verbose_name': 'Session',
                'verbose_name_plural': 'Sessions',
                'unique_together': {('name', 'course')},
            },
        ),
        # 2. Add new FK columns (nullable)
        migrations.RunPython(add_fk_columns, reverse_add_fk_columns),
        # 3. Populate new columns from old session, mode_of_study, duration
        migrations.RunPython(create_models_and_populate_fks, migrations.RunPython.noop),
        # 4. Drop old columns
        migrations.RunPython(drop_old_columns, reverse_drop_old_columns),
        # 5. Update Django state: replace old fields with FK fields
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(model_name='boardregistration', name='session'),
                migrations.RemoveField(model_name='boardregistration', name='mode_of_study'),
                migrations.RemoveField(model_name='boardregistration', name='duration'),
                migrations.AddField(
                    model_name='boardregistration',
                    name='session',
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='boardreg.session'),
                ),
                migrations.AddField(
                    model_name='boardregistration',
                    name='mode_of_study',
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='boardreg.modeofstudy'),
                ),
                migrations.AddField(
                    model_name='boardregistration',
                    name='duration',
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='boardreg.duration', verbose_name='Duration'),
                ),
            ],
            database_operations=[],
        ),
    ]
