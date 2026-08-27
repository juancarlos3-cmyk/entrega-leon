#!/usr/bin/env python3
"""Abre las 10 ligas publicadas y cuenta cuántas responden de verdad."""
import csv
import sys
import urllib.request
from pathlib import Path

if len(sys.argv) < 2:
    print('Uso: python entrega/probar-ligas.py https://tu-proyecto.vercel.app')
    sys.exit(0)

base = sys.argv[1].rstrip("/")
BASE = Path(__file__).resolve().parent.parent
filas = list(csv.DictReader((BASE / "entrega" / "negocios-10.csv").open(encoding="utf-8")))

vivas, ligas = 0, []
for fila in filas:
    url = "%s/para-%s/" % (base, fila["slug"].strip())
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            codigo = r.status
    except Exception as e:
        codigo = getattr(e, "code", str(e))
    ok = (codigo == 200)
    vivas += ok
    ligas.append((fila["nombre"], url, codigo))
    print("%s  %s  ->  %s" % ("OK " if ok else "X  ", fila["nombre"], codigo))

print("")
print("Vivas: %d de %d" % (vivas, len(filas)))
if vivas < len(filas):
    print("401 = protección prendida en Vercel · 404 = todavía no publica o el slug no coincide")
