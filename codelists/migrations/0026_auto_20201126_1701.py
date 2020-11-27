# Generated by Django 3.1.3 on 2020-11-26 17:01

# This migration fixes the CodelistVersions created from DraftCodelists in migration
# 0023.  That migration did not create SearchResult objects, because on line 32
#
#   search_codes = draft_search.results.values_list("code", flat=True)
#
#  should have been
#
#   search_codes = draft_search.results.values_list("code__code", flat=True)
#
# That is, the original query returned the database IDs of the Codes in the builder
# app, and not the code attributes of those Codes.

from django.db import migrations


def move_drafts_properly(apps, schema_editor):
    Codelist = apps.get_model("codelists", "Codelist")
    SearchResult = apps.get_model("codelists", "SearchResult")
    DraftCodelist = apps.get_model("builder", "DraftCodelist")

    for draft in DraftCodelist.objects.all():
        # Find the new Codelist corresponding to the old DraftCodelist
        codelist = Codelist.objects.get(slug=draft.slug, user=draft.owner)

        # Find the version that was created by the original migration (any later
        # versions will have the correct SearchResults, because the searches are
        # recreated in codlists.actions.export_to_builder)
        version = codelist.versions.order_by("id").first()

        for draft_search in draft.searches.all():
            # Find the new Search corresponding to the original
            search = version.searches.get(slug=draft_search.slug)

            # Find the codes that matched the original
            search_codes = draft_search.results.values_list("code__code", flat=True)

            # Find the IDs of the new CodeObjs with these codes
            code_obj_ids = version.code_objs.filter(code__in=search_codes).values_list(
                "id", flat=True
            )

            # Create the new SearchResults
            SearchResult.objects.bulk_create(
                SearchResult(search=search, code_obj_id=id) for id in code_obj_ids
            )


class Migration(migrations.Migration):

    dependencies = [
        ("codelists", "0025_auto_20201123_1708"),
    ]

    operations = [migrations.RunPython(move_drafts_properly)]