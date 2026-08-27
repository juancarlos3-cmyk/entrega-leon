#!/usr/bin/env python3
"""Toma negocios-10.csv + plantilla.html y escribe una página por negocio.

Uso:
    python generar.py            -> arma las páginas reales en para-<slug>/
                                     (si el CSV trae más filas que el TOPE, para y avisa)
    python generar.py --prueba   -> modo de prueba: arma SOLO la primera fila en
                                     prueba-<slug>/, para revisar el diseño antes
                                     de generar (y publicar) las diez reales.
"""
import csv
import html
import re
import shutil
import sys
import urllib.parse
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent        # la carpeta del proyecto
CSV = BASE / "entrega" / "negocios-10.csv"
PLANTILLA = BASE / "entrega" / "plantilla.html"

AUTOR = "Juan Carlos"
AUTOR_CONTACTO = "WhatsApp 477 185 0807"
LADA_PAIS = "52"                                     # México

MENSAJE_AL_NEGOCIO = "Hola, vi su página y quiero información."

TOPE = 10   # no son diez cualquiera: si el CSV trae más, algo se coló sin querer


def solo_digitos(t: str) -> str:
    return re.sub(r"\D", "", t or "")


ICONO_WSP = ('<svg width="19" height="19" viewBox="0 0 24 24" fill="#1a1305">'
             '<path d="M12 2a10 10 0 0 0-8.6 15L2 22l5.2-1.4A10 10 0 1 0 12 2Z" opacity=".15"/>'
             '<path d="M17 14.2c-.3-.2-1.7-.9-2-1s-.5-.2-.7.2-.8 1-1 1.2-.4.2-.7 0a8 8 0 0 1-2.4-1.5 8.9 8.9 0 0 1-1.6-2c-.2-.3 0-.5.1-.6l.4-.5c.1-.2.2-.3.2-.5s0-.4-.1-.6L8.4 7c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3A3 3 0 0 0 5.5 9c0 1.3 1 2.6 1.1 2.8.1.2 2 3 4.8 4.3.7.3 1.2.5 1.6.6.7.2 1.3.2 1.8.1.5-.1 1.7-.7 1.9-1.4.2-.7.2-1.2.2-1.3-.1-.1-.3-.2-.6-.4Z"/>'
             '</svg>')
ICONO_TEL = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1a1305" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
             '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.3 1.8.6 2.7a2 2 0 0 1-.4 2.1L8 9.9a16 16 0 0 0 6 6l1.4-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.5 2.7.6a2 2 0 0 1 1.8 2Z"/>'
             '</svg>')


def boton(fila: dict) -> str:
    tel = solo_digitos(fila["telefono"])
    if fila["tipo_numero"].strip().lower() == "movil":
        texto = urllib.parse.quote(MENSAJE_AL_NEGOCIO)
        url = "https://wa.me/%s%s?text=%s" % (LADA_PAIS, tel, texto)
        return '<a class="boton" href="%s" target="_blank" rel="noopener">%s Escríbenos por WhatsApp</a>' % (url, ICONO_WSP)
    return '<a class="boton" href="tel:%s">%s Llámanos: %s</a>' % (tel, ICONO_TEL, html.escape(fila["telefono"]))


def armar_pagina(plantilla: str, fila: dict) -> str:
    mapa = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(
        "%s, %s, %s" % (fila["nombre"], fila["direccion"], fila["ciudad"]))

    pagina = plantilla
    reemplazos = {
        "{{NOMBRE}}": html.escape(fila["nombre"]),
        "{{GIRO}}": html.escape(fila["giro"]),
        "{{CIUDAD}}": html.escape(fila["ciudad"]),
        "{{DIRECCION}}": html.escape(fila["direccion"]),
        "{{TELEFONO}}": html.escape(fila["telefono"]),
        "{{TEL_LIMPIO}}": solo_digitos(fila["telefono"]),
        "{{SERVICIO1}}": html.escape(fila["servicio1"]),
        "{{SERVICIO2}}": html.escape(fila["servicio2"]),
        "{{SERVICIO3}}": html.escape(fila["servicio3"]),
        "{{MAPA}}": mapa,
        "{{BOTON}}": boton(fila),
        "{{AUTOR}}": html.escape(AUTOR),
        "{{AUTOR_CONTACTO}}": html.escape(AUTOR_CONTACTO),
    }
    for hueco, valor in reemplazos.items():
        pagina = pagina.replace(hueco, valor)
    return pagina


def main() -> None:
    prueba = "--prueba" in sys.argv

    plantilla = PLANTILLA.read_text(encoding="utf-8")
    filas = list(csv.DictReader(CSV.open(encoding="utf-8")))

    if prueba:
        if not filas:
            print("El CSV está vacío, no hay nada que probar.")
            return
        fila = filas[0]
        slug = fila["slug"].strip()
        carpeta = BASE / ("prueba-%s" % slug)
        carpeta.mkdir(parents=True, exist_ok=True)
        destino = carpeta / "index.html"
        destino.write_text(armar_pagina(plantilla, fila), encoding="utf-8")
        print("── MODO DE PRUEBA ──")
        print("Renglones en el CSV: %d" % len(filas))
        print("Página de prueba:    prueba-%s/index.html" % slug)
        print("\nÁbrela en http://localhost:8080/prueba-%s/ (con el servidor local prendido)" % slug)
        print("y revisa el diseño ANTES de correr 'python generar.py' (sin --prueba) para las diez.")
        print("Esta carpeta 'prueba-*' nunca se publica ni se cuenta como entrega.")
        return

    if len(filas) > TOPE:
        print("── TOPE ──")
        print("Renglones en el CSV: %d" % len(filas))
        print("Tope por corrida:    %d" % TOPE)
        print("\nSon más de %d. No escribí ninguna página." % TOPE)
        print("No son diez cualquiera: revisa el CSV, quita los que sobran, y vuelve a correr.")
        return

    escritas = []
    for fila in filas:
        slug = fila["slug"].strip()
        carpeta = BASE / ("para-%s" % slug)
        carpeta.mkdir(parents=True, exist_ok=True)
        destino = carpeta / "index.html"

        if destino.exists():
            shutil.copy(destino, destino.with_suffix(".html.respaldo"))

        destino.write_text(armar_pagina(plantilla, fila), encoding="utf-8")
        escritas.append(slug)

    print("Renglones en el CSV: %d" % len(filas))
    print("Páginas escritas:    %d" % len(escritas))
    for s in escritas:
        print("  · para-%s/index.html" % s)


if __name__ == "__main__":
    main()
