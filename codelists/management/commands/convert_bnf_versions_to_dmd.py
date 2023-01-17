import csv
from pathlib import Path

import structlog
from django.core.management import BaseCommand
from django.db.utils import IntegrityError

from ...actions import convert_bnf_codelist_version_to_dmd
from ...models import CodelistVersion, Handle

logger = structlog.get_logger()


class Command(BaseCommand):

    """
    Convert BNF codelist versions to new dm+d codelist.

    BNF codelists to convert are provided in a CSV file which includes a column headed "URL".

    Each BNF codelist version is converted to a dm+d codelist with the following attributes:
    - has the same owner (organisation or user) as the original
    - has -dmd appended to the codelist name and slug
    - includes a link to the original codelist version in the methodology
    - has the same description as the original
    - has the same references as the original
    - has "published" status
    - has codes generated by mappings.bnfdmd.mappers.bnf_to_dmd

    It generates a results CSV file with URLs of BNF versions with their newly created dm+d equivalents.
    """

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=Path)

    def handle(self, csv_file, **kwargs):
        with open(csv_file) as in_f:
            reader = csv.DictReader(in_f)
            bnf_versions = []
            not_found = []
            for i, row in enumerate(reader, start=1):
                row_data = {k.lower(): v for k, v in row.items()}
                assert "url" in row_data
                # ignore empty rows
                if not row_data["url"]:
                    continue
                # strip whitespace, strip trailing slash, split on slash
                hash_from_url = row_data["url"].strip().strip("/").rsplit("/", 1)[-1]
                try:
                    bnf_version = CodelistVersion.objects.get_by_hash(hash_from_url)
                except (CodelistVersion.DoesNotExist, ValueError):
                    # `get_by_hash()` can error if a CodelistVersion for the extracted
                    # hash can't be found, OR if the extracted hash is invalid (e.g. if
                    # the URL is for a codelist, not a version, the extracted "hash" will
                    # be a codelist slug, which raises a ValueError from get_by_hash)
                    not_found.append((i, row_data["url"]))
                else:
                    bnf_versions.append(bnf_version)

        converted_dmd_codelists = {}
        for version in bnf_versions:
            created = False
            try:
                dmd_codelist = convert_bnf_codelist_version_to_dmd(
                    version, published=True
                )
                created = True
            except IntegrityError as e:
                assert "UNIQUE constraint failed" in str(e)
                dmd_codelist = Handle.objects.get(
                    slug=f"{version.codelist.slug}-dmd"
                ).codelist
            converted_dmd_codelists[version.get_absolute_url()] = (
                dmd_codelist.get_absolute_url(),
                created,
            )

        outfile = csv_file.parent / f"{csv_file.stem}_converted.csv"
        with open(outfile, "w") as out_f:
            writer = csv.writer(out_f)
            writer.writerow(["BNF version", "dm+d codelist", "created", "comments"])
            for bnf_version, (dmd_version, created) in converted_dmd_codelists.items():
                writer.writerow(
                    [
                        bnf_version,
                        dmd_version,
                        created,
                        "already exists" if not created else "",
                    ]
                )
            for (row_num, not_found_version) in not_found:
                writer.writerow(
                    [
                        not_found_version,
                        "",
                        False,
                        f"BNF version not found (input file row {row_num})",
                    ]
                )

        self.stdout.write(f"Results exported to {outfile}")
