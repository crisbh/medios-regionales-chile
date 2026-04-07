#!/usr/bin/env python3
"""Generate medios_chile.opml from medios_final.csv.

Usage:
    python generate_opml.py
"""

import csv
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone

CSV_FILE = "medios_final.csv"
OPML_FILE = "medios_chile.opml"


def build_opml(rows):
    by_region = defaultdict(list)
    for row in rows:
        by_region[row["region"]].append(row)

    opml = ET.Element("opml", version="2.0")

    head = ET.SubElement(opml, "head")
    ET.SubElement(head, "title").text = "Medios Regionales Chile"
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    ET.SubElement(head, "dateCreated").text = now

    body = ET.SubElement(opml, "body")

    for region in sorted(by_region):
        region_el = ET.SubElement(body, "outline", text=region, title=region)
        for medio in sorted(by_region[region], key=lambda m: m["nombre"]):
            url = medio["url"].rstrip("/")
            ET.SubElement(
                region_el,
                "outline",
                text=medio["nombre"],
                title=medio["nombre"],
                type="rss",
                xmlUrl=f"{url}/feed",
                htmlUrl=url,
            )

    return opml


def indent(elem, level=0):
    """Add pretty-print indentation in place."""
    pad = "\n" + "  " * level
    if len(elem):
        elem.text = pad + "  "
        elem.tail = pad
        for child in elem:
            indent(child, level + 1)
        child.tail = pad
    else:
        elem.tail = pad
    if level == 0:
        elem.tail = "\n"


def main():
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    opml = build_opml(rows)
    indent(opml)

    tree = ET.ElementTree(opml)
    ET.indent(tree, space="  ")  # Python 3.9+

    with open(OPML_FILE, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" ?>\n')
        tree.write(f, encoding="unicode", xml_declaration=False)
        f.write("\n")

    total = sum(1 for r in rows)
    regions = len({r["region"] for r in rows})
    print(f"Generado {OPML_FILE} — {total} medios en {regions} regiones.")


if __name__ == "__main__":
    main()
