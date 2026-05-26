from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="courselesson",
            name="video_url",
            field=models.URLField(blank=True, null=True),
        ),
    ]
