# Move application_fee from CourseType to Course only

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boardreg', '0009_alter_boardregistration_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coursetype',
            name='application_fee',
        ),
        migrations.AddField(
            model_name='course',
            name='application_fee',
            field=models.DecimalField(blank=True, decimal_places=2, default=500.0, max_digits=10, null=True, verbose_name='Application Fee'),
        ),
    ]
