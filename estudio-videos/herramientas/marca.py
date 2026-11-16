#!/usr/bin/env python3
"""Genera la imagen de marca de los dos canales (perfil, banner y marca de agua) en SVG.
Pasar a PNG con: node herramientas/marca_a_png.js"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
F = 'font-family="Inter, DejaVu Sans, sans-serif"'
NAVY, TEAL, NAR, NEGRO = "#1B2A49", "#00A8A8", "#FF6B00", "#111111"


def svg(w, h, cuerpo):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" {F}>{cuerpo}</svg>'


def espiga(x, y, w, h, color, ancho):
    """Curva del potencial de acción dentro de la caja x,y,w,h."""
    p = [(0, .72), (.28, .72), (.36, .62), (.46, .05), (.60, .86), (.78, .72), (1, .72)]
    d = f"M{x + p[0][0] * w:.0f} {y + p[0][1] * h:.0f}"
    for (x0, y0), (x1, y1) in zip(p, p[1:]):
        xm = (x0 + x1) / 2
        d += f" C{x + xm * w:.0f} {y + y0 * h:.0f} {x + xm * w:.0f} {y + y1 * h:.0f} {x + x1 * w:.0f} {y + y1 * h:.0f}"
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{ancho}" stroke-linecap="round" stroke-linejoin="round"/>'


def neomed():
    d = RAIZ / "canales/medico/marca"
    perfil = (f'<rect width="800" height="800" fill="{NAVY}"/>' + espiga(130, 170, 540, 330, TEAL, 30)
              + f'<text x="400" y="640" font-size="120" font-weight="800" fill="white" text-anchor="middle">Neo<tspan fill="{TEAL}">Med</tspan></text>')
    (d / "perfil.svg").write_text(svg(800, 800, perfil))
    # Zona segura del banner de YouTube: 1546x423 centrada en 2560x1440
    banner = (f'<rect width="2560" height="1440" fill="{NAVY}"/>' + espiga(-100, 250, 2760, 900, "#24365C", 60)
              + espiga(530, 590, 230, 190, TEAL, 18)
              + f'<text x="800" y="735" font-size="118" font-weight="800" fill="white">Neo<tspan fill="{TEAL}">Med</tspan> <tspan font-weight="500">Fisiología</tspan></text>'
              + f'<text x="804" y="815" font-size="50" font-weight="500" fill="#C9D2E3">Fisiología humana, paso a paso.</text>')
    (d / "banner.svg").write_text(svg(2560, 1440, banner))
    agua = f'<rect width="150" height="150" rx="24" fill="{NAVY}"/>' + espiga(18, 30, 114, 90, TEAL, 9)
    (d / "marca_de_agua.svg").write_text(svg(150, 150, agua))


def curioso():
    d = RAIZ / "canales/popular/marca"
    signo = lambda x, y, t, c: f'<text x="{x}" y="{y}" font-size="{t}" font-weight="900" fill="{c}" text-anchor="middle">?</text>'
    perfil = (f'<rect width="800" height="800" fill="{NAR}"/><circle cx="400" cy="400" r="270" fill="white"/>'
              f'<circle cx="400" cy="400" r="270" fill="none" stroke="{NEGRO}" stroke-width="26"/>' + signo(400, 545, 420, NEGRO))
    (d / "perfil.svg").write_text(svg(800, 800, perfil))
    banner = (f'<rect width="2560" height="1440" fill="white"/><rect y="0" width="2560" height="1440" fill="{NAR}" opacity=".08"/>'
              f'<circle cx="630" cy="720" r="105" fill="{NAR}"/><circle cx="630" cy="720" r="105" fill="none" stroke="{NEGRO}" stroke-width="12"/>'
              + signo(630, 778, 165, "white")
              + f'<text x="780" y="745" font-size="128" font-weight="900" fill="{NEGRO}">Cuerpo <tspan fill="{NAR}">Curioso</tspan></text>'
              + f'<text x="784" y="822" font-size="48" font-weight="500" fill="#444">Cada semana, una curiosidad de tu cuerpo.</text>')
    (d / "banner.svg").write_text(svg(2560, 1440, banner))
    agua = (f'<circle cx="75" cy="75" r="70" fill="{NAR}"/>' + signo(75, 112, 105, "white"))
    (d / "marca_de_agua.svg").write_text(svg(150, 150, agua))


neomed()
curioso()
print("Marca generada en canales/*/marca/")
