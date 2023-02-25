from bibtexparser.customization import convert_to_unicode, author, splitname


def rebuild_name(name):
    if name.endswith(", "):
        return name[: -len(", ")]
    name = splitname(name)
    name = name["first"] + name["last"] + name["von"] + name["jr"]
    name = " ".join(name)
    return name

def parser_customizations(record):
    record = convert_to_unicode(record)
    record = author(record)
    if "author" in record:
        author_list = [rebuild_name(name) for name in record["author"]]
        record["author"] = ", ".join(author_list)
    return record
