import os
import requests
import bibtexparser

BIB_PATH = "references.bib"
NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_IDENTIFIER = os.environ["DATABASE_IDENTIFIER"]

headers = {
    "Accept": "application/json",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {NOTION_TOKEN}",
}

property_types = {
    "Title": "title",
    "Authors": "rich_text",
    "Year": "number",
    "Reference ID": "rich_text",
    "Link": "url",
}

def parse_bib_entry(entry):
    title = clean_str(entry.get("title", ""))
    authors = clean_str(entry.get("author", ""))
    year = entry.get("year", "")
    link = entry.get("url", "")
    ref_id = entry.get("ID")

    return {
        "Title": title,
        "Authors": authors,
        "Year": year,
        "Reference ID": ref_id,
        "Link": link,
    }


def get_property_value(property_type, content):
    if property_type == "title":
        return {
            "title": [
                {
                    "text": {
                        "content": content,
                    }
                }
            ]
        }
    elif property_type == "rich_text":
        return [
            {
                "type": "text",
                "text": {
                    "content": content,
                },
            }
        ]
    # number, url, etc.
    return {property_type: content}

def build_properties(entry_properties):
    return {
        name: get_property_value(property_types[name], content)
        for name, content in entry_properties.items()
    }


def notion_add_entry(entry_properties):
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {
            "database_id": DATABASE_IDENTIFIER,
        },
        "properties": build_properties(entry_properties),
    }
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)

def notion_update_entry(page_id, entry_properties):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {
        "parent": {
            "database_id": DATABASE_IDENTIFIER,
        },
        "properties": build_properties(entry_properties),
    }
    response = requests.patch(url, json=payload, headers=headers)

def notion_query_db():
    url = f"https://api.notion.com/v1/databases/{DATABASE_IDENTIFIER}/query"

    cursor = None
    payload = {"page_size": 100}

    pages = []

    while True:
        if cursor is not None:
            payload["start_cursor"] = cursor
        response = requests.post(url, json=payload, headers=headers).json()

        for page in response["results"]:
            pages.append(page)

        if response["has_more"] is False:
            break
        cursor = response["next_cursor"]

    return pages


def clean_str(string):
    string = string.strip()
    string = string.replace("\n", " ")
    string = string.replace(r"\"a", "ä")
    string = string.replace(r"\"e", "ë")
    string = string.replace(r"\"i", "ï")
    string = string.replace(r"\"o", "ö")
    string = string.replace(r"\"u", "ü")
    string = string.replace(r"\'a", "á")
    string = string.replace(r"\'e", "é")
    string = string.replace(r"\'i", "í")
    string = string.replace(r"\'o", "ó")
    string = string.replace(r"\'u", "ú")
    string = string.replace(r"\^a", "â")
    string = string.replace(r"\^e", "ê")
    string = string.replace(r"\^i", "î")
    string = string.replace(r"\^o", "ô")
    string = string.replace(r"\^u", "û")
    string = string.replace(r"\`a", "à")
    string = string.replace(r"\`e", "è")
    string = string.replace(r"\`i", "ì")
    string = string.replace(r"\`o", "ò")
    string = string.replace(r"\`u", "ù")
    string = " ".join([w.title() if w.islower() else w for w in string.split()])
    string = string.replace("{", "")
    string = string.replace("}", "")
    return string


def main():
    # instantiate the parser
    parser = bibtexparser.bparser.BibTexParser()
    parser.ignore_nonstandard_types = True
    parser.homogenize_fields = False
    parser.interpolate_strings = False
    # parser.customization = bibtexparser.customization.convert_to_unicode

    with open(BIB_PATH) as bib_file:
        bibliography = bibtexparser.load(bib_file, parser=parser)

    existing_pages = notion_query_db()
    existing_pages_by_title = [
        p['properties']['Title']['title'][0]['text']['content']
        for p in existing_pages
    ]

    for bib_entry in reversed(bibliography.entries):
        entry = parse_bib_entry(bib_entry)
        if entry['Title'] not in existing_pages_by_title:
            print(f"Adding {entry['Title']}")
            notion_add_entry(build_properties(entry))
        # if ref_id not in archive_ids:  # new page
        #     notion_add_entry(entry)
        # elif entry not in archive:  # update existing page
        #     page_id = notion_fetch_page(ref_id)
        #     if page_id != -1:
        #         notion_update_page(entry)

if __name__ == "__main__":
    main()
