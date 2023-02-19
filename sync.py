import os
import requests

import bibtexparser
from bibtexparser.bparser import BibTexParser

import utils.bibtex_parsing as bibtex_parsing
import utils.notion as notion


NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_IDENTIFIER = os.environ["DATABASE_IDENTIFIER"]

## User customizations

BIB_PATH = "references.bib"
PRIMARY_KEY = "Reference ID"

# Notion column names : Notion property types
notion_property_types = {
    # "Title": "title",
    "Authors": "rich_text",
    "Year": "rich_text",
    "Reference ID": "rich_text",
    "Link": "url",
}

# Notion column names : Bibtex property keys
notion_property_keys = {
    # "Title": "title",
    "Authors": "author",
    "Year": "year",
    "Reference ID": "ID",
    "Link": "url",
}

## Main

if __name__ == "__main__":

    # Parse Bibtex

    parser = BibTexParser(
        customization = bibtex_parsing.parser_customizations,
        ignore_nonstandard_types = False
    )

    with open(BIB_PATH) as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file, parser=parser)

    # Format: "content_dict"
    bib_entries = [
        bibtex_parsing.bibtex_to_content_dict(e, notion_property_keys)
        for e in bib_database.entries
    ]

    # Query Notion DB

    notion_headers = notion.get_headers(NOTION_TOKEN)

    notion_pages = notion.query_db(db_id=DATABASE_IDENTIFIER, headers=notion_headers)
    notion_page_ids = [page['id'] for page in notion_pages]
    notion_entries = [
        notion.page_to_entry(page, property_types=notion_property_types)
        for page in notion_pages
    ]

    notion_entries_by_pkey = { e[PRIMARY_KEY] : e for e in notion_entries }
    notion_page_ids_by_pkey = { e[PRIMARY_KEY] : page_id for e, page_id in zip(notion_entries, notion_page_ids)}

    # Insert or update missing pages

    for bib_e in bib_entries:
        p_key = bib_e[PRIMARY_KEY]

        if p_key not in notion_entries_by_pkey:
            notion_page_id = None
        elif bib_e != notion_entries_by_pkey[PRIMARY_KEY]:
            notion_page_id = notion_page_ids_by_pkey[PRIMARY_KEY]
        else:
            continue

        properties = notion.entry_to_properties(bib_e, notion_property_types)
        notion.update_page(db_id=DATABASE_IDENTIFIER, properties=properties, update_page_id=notion_page_id, headers=notion_headers)
