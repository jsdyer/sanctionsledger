from html import escape
from urllib.parse import urlsplit


FIELDS = (("given_names", "Given names"), ("surname", "Surname"), ("entity_or_ship", "Entity or ship name"),
          ("listed_date", "Source listing date"), ("name", "Source-listed name"))
SOURCE = "https://www.international.gc.ca/world-monde/international_relations-relations_internationales/sanctions/consolidated-consolide.aspx?lang=eng"


def reference(row):
    return (f'{escape(row["regime"])} schedule {escape(str(row["schedule"]))}, '
            f'item {escape(str(row["item"]))}')


def sources(row):
    links = [f'<a href="{escape(SOURCE, quote=True)}">Open the consolidated list</a>']
    url = row.get("regulation_url", "")
    if urlsplit(url).scheme == "https" and urlsplit(url).hostname in {"laws.justice.gc.ca", "laws-lois.justice.gc.ca"}:
        links.append(f'<a href="{escape(url, quote=True)}">Read the linked regulation</a>')
    return " · ".join(links)


def example_card(current, history):
    before_date = next((h["captured_at"][:10] for h in reversed(history)
                        if h["captured_at"] < current["captured_at"]), None)
    after_date = current["captured_at"][:10]
    if before_date and not current.get("changes", {}).get("initial", True):
        for change in current["changes"].get("examples", []):
            if change["kind"] != "changed":
                continue
            old, new = change["before"], change["after"]
            if not all(old.get(k) and old[k] == new.get(k) for k in ("regime", "schedule", "item")):
                continue
            for key, label in FIELDS:
                if old.get(key) and new.get(key) and old[key] != new[key]:
                    return (f'<h2>{reference(new)}</h2><p>The “{label}” field in this list entry differed between '
                            f'the {before_date} and {after_date} captures.</p><details><summary>Compare the two captures</summary>'
                            f'<dl><dt>{before_date}</dt><dd>{escape(str(old[key]))}</dd>'
                            f'<dt>{after_date}</dt><dd>{escape(str(new[key]))}</dd></dl>'
                            f'<p>The dates refer to the saved copies of the list.</p>{sources(new)}</details>')
    row = next((r for r in current["records"] if all(r.get(k) for k in ("regime", "schedule", "item", "name", "listed_date"))), None)
    if not row:
        return '<p>Choose a saved capture to inspect its source entries.</p>'
    return (f'<h2>{reference(row)}</h2><p>The {after_date} capture gives a source listing date of '
            f'{escape(row["listed_date"])}.</p><details><summary>Inspect this source entry</summary>'
            f'<p>The source lists the name “{escape(row["name"])}”.</p>{sources(row)}</details>')
