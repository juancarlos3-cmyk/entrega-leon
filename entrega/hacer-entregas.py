#!/usr/bin/env python3
"""Arma entregas.md: liga de la página + cómo contactar a cada negocio."""
import csv
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SITIO = "https://entrega-leon.vercel.app"

filas = list(csv.DictReader((BASE / "entrega" / "negocios-10.csv").open(encoding="utf-8")))
lineas = ["# Mis 10 entregas", "",
          "| Negocio | Liga | Cómo le llego | Fecha | Qué contestó |",
          "|---|---|---|---|---|"]

for fila in filas:
    liga = "%s/para-%s/" % (SITIO, fila["slug"].strip())
    tel = re.sub(r"\D", "", fila["telefono"])
    if fila["tipo_numero"].strip().lower() == "movil":
        como = "WhatsApp %s" % fila["telefono"]
    else:
        como = "Llamar al %s (fijo, pedir el WhatsApp para mandar la liga)" % fila["telefono"]
    lineas.append("| %s | [abrir](%s) | %s |  |  |" % (fila["nombre"], liga, como))

(BASE / "entrega" / "entregas.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
print("entrega/entregas.md listo con %d negocios" % len(filas))
