from django.db import migrations, models

from contribution.models import Premium

from core.datetimes.ad_datetime import datetime


class Migration(migrations.Migration):
    dependencies = [
        ('contribution', '0006_add_source_field_to_contribution'),
    ]

    # For MSSQL These changes were added through raw sql, to keep consistency with existing databases it couldn't be
    # changed in postgres sql script.
    operations = []
    try:
        Premium.objects.all().aggregate(sum=models.Count('created_date'))
    except:
        operations.append(
            migrations.AddField(
                model_name='premium',
                name='created_date',
                field=models.DateField(db_column="CreatedDate", default=datetime.now),
            )
        )
