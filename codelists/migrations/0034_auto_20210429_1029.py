# Generated by Django 3.1.8 on 2021-04-29 10:29

from django.db import migrations


def create_handles(apps, schema_editor):
    Codelist = apps.get_model("codelists", "Codelist")

    for cl in Codelist.objects.all():
        cl.handles.create(
            name=cl.name,
            slug=cl.slug,
            organisation=cl.organisation,
            user=cl.user,
            is_current=True,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("codelists", "0033_auto_20210429_1029"),
    ]

    operations = [migrations.RunPython(create_handles)]