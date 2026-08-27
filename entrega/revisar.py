#!/usr/bin/env python3
"""Revisa que las 10 páginas existan, estén completas y no se hayan mezclado."""
import csv
import html
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
filas = list(csv.DictReader((BASE / "entrega" / "negocios-10.csv").open(encoding="utf-8")))
problemas = []

for fila in filas:
    p = BASE / ("para-%s" % fila["slug"].strip()) / "index.html"
    if not p.exists():
        problemas.append("FALTA la página de %s" % fila["nombre"])
        continue
    t = p.read_text(encoding="utf-8")

    mio = html.escape(fila["nombre"])

    if "{{" in t:
        problemas.append("%s: quedaron huecos sin llenar" % fila["nombre"])
    if mio not in t:
        problemas.append("%s: no aparece su propio nombre" % fila["nombre"])
    if re.sub(r"\D", "", fila["telefono"]) not in re.sub(r"\D", "", t):
        problemas.append("%s: no aparece su teléfono" % fila["nombre"])
    if "noindex" not in t:
        problemas.append("%s: le falta la línea de noindex" % fila["nombre"])
    if "muestra de cortesía" not in t.lower():
        problemas.append("%s: le falta la banda de cortesía" % fila["nombre"])

    for otra in filas:
        if otra["slug"] == fila["slug"]:
            continue
        if html.escape(otra["nombre"]) in t:
            problemas.append("%s trae el nombre de %s" % (fila["nombre"], otra["nombre"]))

carpetas = len(list(BASE.glob("para-*/index.html")))
print("Negocios en la lista: %d" % len(filas))
print("Páginas en el disco:  %d" % carpetas)
print("")
if problemas:
    print("PROBLEMAS (%d):" % len(problemas))
    for x in problemas:
        print("  · %s" % x)
else:
    print("Las %d páginas están completas, con sus datos y sin mezclas." % carpetas)
