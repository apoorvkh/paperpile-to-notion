import os
import csv

import bibtexparser
from bibtexparser.bparser import BibTexParser

import utils.bibtex_parsing as bibtex_parsing
import utils.notion as notion


NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_IDENTIFIER = os.environ["DATABASE_IDENTIFIER"]

## User customizations

BIB_PATH = "../references.bib"
CFG_PATH = "../data_config.csv"

TITLE_KEY = "Title"
PRIMARY_KEY = "Reference ID"

## Main

if __name__ == "__main__":
    print(f"Loading config from {CFG_PATH} ...")

    with open(CFG_PATH, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        data_config = list(reader)

    print(f"Parsing {BIB_PATH} ...")

    bib_database = bibtexparser.load(
        open(BIB_PATH, "r"),
        parser=BibTexParser(
            customization=bibtex_parsing.parser_customizations,
            ignore_nonstandard_types=False,
        ),
    )

    bib_entries = [
        {c["notion_property"]: b.get(c["bibtex_field"], "") for c in data_config}
        for b in bib_database.entries
    ]

    print("Querying Notion DB ...")

    notion_headers = notion.get_headers(NOTION_TOKEN)
    notion_pages = notion.query_db(db_id=DATABASE_IDENTIFIER, headers=notion_headers)

    notion_page_ids = [page["id"] for page in notion_pages]

    notion_entries = [
        {
            c["notion_property"]: notion.get_property(
                page, c["notion_property"], c["property_type"]
            )
            for c in data_config
        }
        for page in notion_pages
    ]

    notion_entries_by_pkey = {e[PRIMARY_KEY]: e for e in notion_entries}
    notion_page_ids_by_pkey = {
        e[PRIMARY_KEY]: pid for e, pid in zip(notion_entries, notion_page_ids)
    }

    print("Updating pages ...")

    # Insert or update missing pages

    for bib_e in bib_entries:
        p_key = bib_e[PRIMARY_KEY]

        if p_key not in notion_entries_by_pkey:
            notion_page_id = None
        elif bib_e != notion_entries_by_pkey[p_key]:
            notion_page_id = notion_page_ids_by_pkey[p_key]
        else:
            continue

        print("Updating" if notion_page_id else "Adding", end="")
        print(f' page for paper "{bib_e[TITLE_KEY]}"')

        properties = {
            c["notion_property"]: notion.property_to_value(
                property_type=c["property_type"], content=bib_e[c["notion_property"]]
            )
            for c in data_config
        }

        response_ok, response_text = notion.update_page(
            db_id=DATABASE_IDENTIFIER,
            properties=properties,
            update_page_id=notion_page_id,
            headers=notion_headers,
        )

        if response_ok is False:
            print(response_text)

    print("Removing outdated pages ...")

    # Flag duplicates?

    print("Updating Google Drive PDF links ...")

    # Use https://github.com/iterative/PyDrive2

    print("Completed.")
