#!/usr/bin/env python3
"""Dibuja las 46 escenas del video como SVG en 02_Imagenes/svg/.

Después se pasan a PNG con:  node herramientas/svg_a_png.js <carpeta_video>
"""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve()
sys.path.insert(0, str(AQUI.parents[5] / "herramientas"))
from dibujo import *  # noqa: E402,F403

E = {}


def escena(n, titulo):
    def deco(f):
        E[n] = lambda: lienzo(titulo, f())
        return f
    return deco


def crono(x, y, r=60):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="white" stroke="{NAVY}" stroke-width="6"/>'
            + curva(f"M{x} {y}V{y - r * .6}M{x} {y}l{r * .4:.0f} {r * .25:.0f}", NAVY, 6))


def chispa(x, y, r=46):
    import math
    p = " ".join(f"{x + (r if i % 2 == 0 else r * .45) * math.cos(i * math.pi / 6):.0f},"
                 f"{y + (r if i % 2 == 0 else r * .45) * math.sin(i * math.pi / 6):.0f}" for i in range(12))
    return f'<polygon points="{p}" fill="{TEAL}"/>'


def cruz(x, y, r=40):
    return curva(f"M{x - r} {y - r}L{x + r} {y + r}M{x + r} {y - r}L{x - r} {y + r}", ROJO, 14)


# ---------------------------------------------------------------- 1-2 gancho
@escena(1, "Una señal eléctrica recorre tus nervios")
def _():
    return (neurona(330, 540, 1200, 1.2) + pulso(1000, 540, 170, 60)
            + "".join(curva(f"M{800 - i * 70} {500 + i * 0}h-40", TEAL, 8) for i in range(3))
            + flecha(1120, 540, 1300, 540, TEAL, 10)
            + texto(1000, 420, "más de 100 m/s", 64, TEAL, peso=800))


@escena(2, "El potencial de acción")
def _():
    g = Grafico(430, 250, 1060, 560)
    return (f'<rect x="300" y="200" width="1320" height="700" rx="28" fill="white" stroke="{NAVY}" stroke-width="8"/>'
            + g.traza(color=TEAL, ancho=12))


# ---------------------------------------------------------------- 3-10 reposo
@escena(3, "La membrana: una doble capa de lípidos")
def _():
    return (membrana() + lados() + flecha(960, 330, 960, 480, NAVY, 6)
            + texto(960, 305, "Bicapa lipídica", 44, NAVY, peso=700))


@escena(4, "Sodio afuera, potasio adentro")
def _():
    prot = [(430, MY + 210), (1010, MY + 240), (1560, MY + 200)]
    return (membrana() + lados() + nube("Na", 16, AFUERA, 4, evitar=[(700, MY - 150, 80), (1300, MY - 250, 80)])
            + ion(700, MY - 150, "K") + ion(1300, MY - 250, "K")
            + "".join(proteina(x, y) for x, y in prot)
            + nube("K", 14, ADENTRO, 5, evitar=[(x, y, 95) for x, y in prot] + [(760, MY + 150, 80)]) + ion(760, MY + 150, "Na"))


@escena(5, "La bomba de sodio y potasio gasta ATP")
def _():
    return (membrana(huecos=[(960, 100)]) + lados() + bomba(960)
            + nube("Na", 9, AFUERA, 7, evitar=[(960, MY - 200, 200)])
            + nube("K", 8, (120, MY + 110, 1800, MY + 300), 8, evitar=[(960, MY + 200, 330)]))


@escena(6, "Saca 3 sodios y mete 2 potasios")
def _():
    s = membrana(huecos=[(960, 100)]) + lados() + bomba(960, atp=False)
    for i, x in enumerate((640, 720, 800)):
        s += ion(x, MY - 250 + i * 12, "Na")
    s += curva(f"M900 {MY - 60}C860 {MY - 180} 860 {MY - 220} 850 {MY - 235}", TEAL, 10, True)
    for x in (1120, 1200):
        s += ion(x, MY + 240, "K")
    s += curva(f"M1100 {MY + 215}C1060 {MY + 200} 1040 {MY + 150} 1025 {MY + 80}", NAVY, 10, True)
    return s + texto(720, MY - 320, "3 Na⁺ salen", 48, TEAL, peso=800) + texto(1180, MY + 340, "2 K⁺ entran", 48, NAVY, peso=800)


@escena(7, "Canales de fuga: el potasio se escapa")
def _():
    return (membrana(huecos=[(960, 62)]) + lados() + canal_fuga(960)
            + nube("K", 11, ADENTRO, 9, evitar=[(960, MY + 200, 150)]) + ion(960, MY + 170, "K") + ion(960, MY - 190, "K")
            + ion(1050, MY - 260, "K") + flecha(960, MY + 120, 960, MY - 130, NAVY, 10)
            + nube("Na", 8, AFUERA, 10, evitar=[(990, MY - 220, 190)])
            + texto(1320, MY - 330, "Canal de fuga de K⁺", 40, NAVY, peso=700))


@escena(8, "El interior queda negativo")
def _():
    s = membrana() + lados()
    for x in range(200, 1800, 120):
        s += texto(x, MY - 110, "+", 70, TEAL, peso=800) + texto(x, MY + 150, "−", 70, NAVY, peso=800)
    return s + texto(960, MY - 250, "Exterior positivo", 46, TEAL, peso=700) + texto(960, MY + 290, "Interior negativo", 46, NAVY, peso=700)


@escena(9, "Potencial de membrana en reposo")
def _():
    return (axon(200, 1300, 700, 150)
            + f'<rect x="1150" y="230" width="520" height="290" rx="26" fill="white" stroke="{NAVY}" stroke-width="8"/>'
            + f'<rect x="1190" y="270" width="440" height="150" rx="14" fill="{TEAL_CLARO}"/>'
            + texto(1410, 375, "−70 mV", 92, NAVY, peso=800)
            + curva("M1280 520V610C1280 680 900 600 800 690", NAVY, 6) + f'<circle cx="800" cy="694" r="12" fill="{NAVY}"/>'
            + curva("M1540 520V560C1540 600 1000 480 700 560", TEAL, 6) + f'<circle cx="700" cy="562" r="12" fill="{TEAL}"/>'
            + texto(520, 590, "afuera", 34, TEAL, peso=700) + texto(520, 712, "adentro", 34, NAVY, peso=700))


@escena(10, "Una batería cargada, lista para usarse")
def _():
    b = (f'<rect x="1150" y="400" width="520" height="260" rx="30" fill="white" stroke="{NAVY}" stroke-width="10"/>'
         f'<rect x="1670" y="480" width="40" height="100" rx="10" fill="{NAVY}"/>'
         + "".join(f'<rect x="{1185 + i * 118}" y="435" width="98" height="190" rx="14" fill="{TEAL}"/>' for i in range(4)))
    return neurona(360, 530, 520, 1.1) + b + texto(960, 540, "=", 110, NAVY, peso=800)


# ---------------------------------------------------------------- 11-21 despolarización
@escena(11, "Canales activados por voltaje")
def _():
    return (membrana(huecos=[(640, 66), (1280, 66)]) + lados()
            + canal(640, "Na", "cerrada", "abierta", rotulo="Canal de Na⁺")
            + canal(1280, "K", "cerrada", rotulo="Canal de K⁺"))


@escena(12, "El canal de sodio tiene dos compuertas")
def _():
    return (membrana(huecos=[(820, 66)]) + lados() + canal(820, "Na", "cerrada", "abierta")
            + flecha(1180, MY - 190, 880, MY - 76, TEAL, 6) + texto(1200, MY - 200, "Compuerta de activación", 42, TEAL, "start", 700)
            + texto(1200, MY - 150, "(cerrada en reposo)", 32, "#7A869A", "start")
            + flecha(1180, MY + 230, 965, MY + 150, TEAL, 6) + texto(1200, MY + 240, "Compuerta de inactivación", 42, TEAL, "start", 700)
            + texto(1200, MY + 290, "(abierta en reposo)", 32, "#7A869A", "start"))


@escena(13, "En reposo, el sodio no puede entrar")
def _():
    return (membrana(huecos=[(960, 66)]) + lados() + canal(960, "Na", "cerrada", "abierta")
            + nube("Na", 15, AFUERA, 13, evitar=[(960, MY - 200, 120)]) + ion(930, MY - 150, "Na") + ion(995, MY - 165, "Na")
            + cruz(960, MY - 62, 30))


@escena(14, "Llega un estímulo: la membrana se despolariza")
def _():
    g = Grafico()
    return (g.ejes(umbral=False) + g.traza(SUB, 0, 1.7, TEAL, 11)
            + flecha(g.px(1.0), g.py(-92), g.px(1.0), g.py(-76), NAVY, 9) + texto(g.px(1.0), g.py(-92) + 50, "estímulo", 36, NAVY, peso=700)
            + texto(g.px(3.2), g.py(-50), "menos negativa", 44, TEAL, peso=700))


@escena(15, "Estímulo débil: no alcanza el umbral")
def _():
    g = Grafico()
    return (g.ejes() + g.traza(SUB, color=NAVY, ancho=10)
            + texto(g.px(3.6), g.py(-30), "Vuelve al reposo", 48, NAVY, peso=700))


@escena(16, "Si llega al umbral, ya no hay vuelta atrás")
def _():
    g = Grafico()
    return (g.ejes() + g.traza(PA, 0, 1.5, NAVY, 10) + chispa(g.px(1.5), g.py(-56), 56)
            + texto(g.px(2.9), g.py(-30), "≈ −55 mV", 60, TEAL, peso=800))


@escena(17, "Se abren los canales de sodio")
def _():
    return (membrana(huecos=[(960, 66)]) + lados() + canal(960, "Na", "abierta", "abierta")
            + nube("Na", 12, AFUERA, 17, evitar=[(960, MY - 200, 130)])
            + ion(960, MY - 185, "Na") + ion(960, MY + 20, "Na") + ion(930, MY + 190, "Na") + ion(1030, MY + 270, "Na")
            + flecha(880, MY - 160, 880, MY + 190, TEAL, 12)
            + texto(1330, MY + 220, "El Na⁺ entra de golpe", 46, TEAL, peso=800))


@escena(18, "Más despolarización abre más canales")
def _():
    s = membrana(huecos=[(480, 66), (960, 66), (1440, 66)]) + lados()
    for x, a in ((480, "abierta"), (960, "abierta"), (1440, "media")):
        s += canal(x, "Na", a, "abierta") + ion(x, MY - 170, "Na") + ion(x - 10, MY + 190, "Na") + flecha(x - 90, MY - 150, x - 90, MY + 170, TEAL, 10)
    return s + flecha(600, MY - 250, 820, MY - 250, NAVY, 7) + flecha(1080, MY - 250, 1300, MY - 250, NAVY, 7)


@escena(19, "Retroalimentación positiva")
def _():
    cajas = [(960, 300, "Entra Na⁺"), (1380, 700, "La membrana se despolariza"), (540, 700, "Se abren más canales de Na⁺")]
    s = ""
    for x, y, t in cajas:
        s += (f'<rect x="{x - 300}" y="{y - 60}" width="600" height="120" rx="60" fill="{TEAL_CLARO}" stroke="{TEAL}" stroke-width="6"/>'
              + texto(x, y + 14, t, 38, NAVY, peso=700))
    return (s + curva("M1240 345C1400 400 1440 520 1420 620", TEAL, 10, True)
            + curva("M1060 740H860", TEAL, 10, True) + curva("M500 620C480 500 540 400 680 340", TEAL, 10, True)
            + texto(960, 560, "+", 120, TEAL, peso=800))


@escena(20, "Fase de despolarización")
def _():
    g = Grafico()
    return (g.ejes() + g.traza() + g.traza(PA, 1.5, 2.05, TEAL, 16)
            + texto(g.px(1.25), g.py(0), "Entra Na⁺", 46, TEAL, "end", 800) + texto(g.px(3.6), g.py(20), "menos de 1 ms", 40, "#7A869A", peso=600))


@escena(21, "El pico: el interior queda positivo")
def _():
    g = Grafico()
    return (g.ejes() + g.traza() + g.traza(PA, 1.9, 2.25, TEAL, 16)
            + flecha(g.px(3.0), g.py(42), g.px(2.2), g.py(37), TEAL, 6)
            + texto(g.px(3.05), g.py(38), "Overshoot (sobreexcitación)", 44, TEAL, "start", 800))


# ---------------------------------------------------------------- 22-30 repolarización
@escena(22, "El mismo voltaje inactiva el canal de sodio")
def _():
    return (membrana(huecos=[(820, 66)]) + lados() + canal(820, "Na", "abierta", "cerrada")
            + ion(820, MY - 180, "Na") + flecha(1180, MY + 200, 860, MY + 90, TEAL, 6)
            + texto(1200, MY + 215, "Compuerta de inactivación", 42, TEAL, "start", 700)
            + texto(1200, MY + 265, "tapa el poro", 36, "#7A869A", "start"))


@escena(23, "Los tres estados del canal de sodio")
def _():
    s = membrana(huecos=[(420, 66), (960, 66), (1500, 66)])
    s += canal(420, "Na", "cerrada", "abierta", rotulo="Reposo")
    s += canal(960, "Na", "abierta", "abierta", rotulo="Activado") + ion(960, MY - 10, "Na") + flecha(880, MY - 150, 880, MY + 130, TEAL, 9)
    s += canal(1500, "Na", "abierta", "cerrada", rotulo="Inactivado") + cruz(1500, MY - 150, 30)
    return s + flecha(560, MY - 250, 820, MY - 250, NAVY, 7) + flecha(1100, MY - 250, 1360, MY - 250, NAVY, 7)


@escena(24, "Se abren los canales de potasio, más lentos")
def _():
    return (membrana(huecos=[(820, 66)]) + lados() + canal(820, "K", "media")
            + nube("K", 9, ADENTRO, 24, evitar=[(820, MY + 190, 130)]) + crono(1300, MY - 220, 70)
            + texto(1400, MY - 205, "se abren con retraso", 40, NAVY, "start", 700))


@escena(25, "El potasio sale de la célula")
def _():
    return (membrana(huecos=[(960, 66)]) + lados() + canal(960, "K", "abierta")
            + nube("K", 9, ADENTRO, 25, evitar=[(960, MY + 190, 150)])
            + ion(960, MY + 170, "K") + ion(960, MY, "K") + ion(940, MY - 200, "K") + ion(1040, MY - 270, "K")
            + flecha(1050, MY + 180, 1050, MY - 160, NAVY, 12)
            + texto(1380, MY - 230, "Salen cargas positivas", 44, NAVY, peso=800))


@escena(26, "Fase de repolarización")
def _():
    g = Grafico()
    return (g.ejes() + g.traza() + g.traza(PA, 2.05, 2.95, TEAL, 16)
            + texto(g.px(3.0), g.py(-10), "Sale K⁺", 46, TEAL, "start", 800))


@escena(27, "Más negativa que en reposo")
def _():
    g = Grafico()
    return (g.ejes() + g.traza() + g.traza(PA, 2.95, 4.3, TEAL, 16)
            + f'<line x1="{g.x}" y1="{g.py(-70)}" x2="{g.x + g.w}" y2="{g.py(-70)}" stroke="{NAVY}" stroke-width="3" stroke-dasharray="6 10"/>'
            + texto(g.px(4.3), g.py(-20), "Los canales de K⁺", 42, TEAL, peso=700) + texto(g.px(4.3), g.py(-32), "tardan en cerrarse", 42, TEAL, peso=700))


@escena(28, "Hiperpolarización posterior y vuelta al reposo")
def _():
    g = Grafico()
    return (g.ejes() + g.traza() + g.traza(PA, 3.3, 6, TEAL, 16)
            + texto(g.px(4.6), g.py(-20), "Pospotencial", 46, TEAL, peso=800)
            + flecha(g.px(4.5), g.py(-28), g.px(3.6), g.py(-76), TEAL, 6))


@escena(29, "Se mueven muy pocos iones")
def _():
    return (membrana(huecos=[(960, 66)]) + lados() + canal(960, "Na", "abierta", "abierta")
            + nube("Na", 22, AFUERA, 29, evitar=[(960, MY - 200, 110)]) + nube("K", 22, ADENTRO, 30, evitar=[(960, MY + 200, 110)])
            + ion(960, MY - 10, "Na"))


@escena(30, "La bomba mantiene los gradientes")
def _():
    g = Grafico(1150, 230, 560, 230)
    return (membrana(huecos=[(600, 100)], y=MY + 190) + bomba(600, MY + 190)
            + f'<rect x="1090" y="190" width="680" height="320" rx="24" fill="white" stroke="{GRIS}" stroke-width="6"/>'
            + g.traza(color=TEAL, ancho=8)
            + texto(1430, 570, "El potencial de acción", 38, NAVY, peso=700) + texto(1430, 618, "no depende de la bomba", 38, NAVY, peso=700)
            + texto(600, MY - 40, "Trabaja a largo plazo", 40, TEAL, peso=700))


# ---------------------------------------------------------------- 31-35 refractarios, todo o nada
@escena(31, "Período refractario absoluto")
def _():
    g = Grafico()
    return (g.banda(1.5, 2.95) + g.ejes() + g.traza()
            + texto(g.px(2.22), g.y + 50, "ABSOLUTO", 34, NAVY, peso=800)
            + texto(g.px(4.5), g.py(10), "Ningún estímulo", 46, NAVY, peso=700) + texto(g.px(4.5), g.py(-4), "dispara otro potencial", 46, NAVY, peso=700))


@escena(32, "Período refractario relativo")
def _():
    g = Grafico()
    return (g.banda(1.5, 2.95) + g.banda(2.95, 5.0, NAVY, .13) + g.ejes() + g.traza()
            + texto(g.px(2.22), g.y + 50, "ABSOLUTO", 34, NAVY, peso=800) + texto(g.px(3.97), g.y + 50, "RELATIVO", 34, NAVY, peso=800)
            + flecha(g.px(3.9), g.py(-95), g.px(3.9), g.py(-86), TEAL, 10) + texto(g.px(3.97), g.py(-20), "hace falta un", 38, TEAL, peso=700) + texto(g.px(3.97), g.py(-31), "estímulo mayor", 38, TEAL, peso=700))


@escena(33, "Avanza en un solo sentido")
def _():
    return (axon() + f'<rect x="560" y="505" width="330" height="70" rx="30" fill="{NAVY}" opacity=".18"/>' + pulso(980)
            + flecha(820, 380, 1500, 380, TEAL, 14) + cruz(520, 380, 34) + flecha(760, 380, 600, 380, "#1B2A49", 8)
            + texto(725, 660, "zona refractaria", 36, NAVY, peso=700))


@escena(34, "La ley del todo o nada")
def _():
    a, b = Grafico(190, 290, 660, 520), Grafico(1070, 290, 660, 520)
    return (a.ejes(chico=True) + a.traza(SUB) + b.ejes(chico=True) + b.traza(color=TEAL, ancho=11)
            + texto(520, 250, "NADA", 64, NAVY, peso=800) + texto(1400, 250, "TODO", 64, TEAL, peso=800))


@escena(35, "La intensidad cambia la frecuencia")
def _():
    def tren(y, xs, color):
        d = f"M260 {y}" + "".join(f"H{x - 14}L{x} {y - 190}L{x + 14} {y}" for x in xs) + "H1700"
        return curva(d, color, 8)
    return (tren(480, range(420, 1700, 400), NAVY) + tren(820, range(360, 1700, 130), TEAL)
            + texto(260, 240, "Estímulo débil", 44, NAVY, "start", 700) + texto(260, 590, "Estímulo fuerte", 44, TEAL, "start", 700)
            + texto(1700, 895, "misma altura, más potenciales por segundo", 34, "#7A869A", "end", 600))


# ---------------------------------------------------------------- 36-40 propagación
@escena(36, "Corrientes locales llevan al umbral a la zona vecina")
def _():
    s = axon(alto=150) + pulso(800, 540, 280, 150)
    for x in range(700, 920, 70):
        s += texto(x, 556, "+", 54, "white", peso=800)
    for x in range(1040, 1700, 110):
        s += texto(x, 556, "−", 54, NAVY, peso=800)
    s += curva("M900 500C980 440 1060 440 1120 500", TEAL, 9, True) + curva("M900 580C980 640 1060 640 1120 580", TEAL, 9, True)
    return s + flecha(1000, 330, 1500, 330, TEAL, 12) + texto(800, 720, "zona activa", 36, TEAL, peso=700) + texto(1280, 720, "zona vecina en reposo", 36, NAVY, peso=700)


@escena(37, "Como fichas de dominó")
def _():
    s = axon(140, 1780, 800, 60)
    for i, a in enumerate((78, 66, 50, 30, 12, 0, 0, 0, 0)):
        x = 330 + i * 150
        s += (f'<rect x="{x}" y="470" width="44" height="290" rx="10" fill="{TEAL if a else "white"}" '
              f'stroke="{NAVY}" stroke-width="6" transform="rotate({a} {x + 44} 760)"/>')
    return s + flecha(500, 330, 1400, 330, TEAL, 12)


@escena(38, "Sin mielina: conducción continua y lenta")
def _():
    caracol = (f'<path d="M1180 420c-50 0-150 0-190-20 30-50 110-50 150-40" fill="{GRIS}" stroke="{NAVY}" stroke-width="6"/>'
               f'<circle cx="1230" cy="360" r="84" fill="white" stroke="{NAVY}" stroke-width="7"/>'
               + curva("M1230 360m-10 0a10 10 0 1 0 22 4a30 30 0 1 0 -52 -8a52 52 0 1 0 86 16", NAVY, 6)
               + curva("M1010 392l-30 -60M1030 386l-12 -62", NAVY, 6))
    return (axon(alto=44, y=640) + pulso(560, 640, 130, 44) + flecha(660, 640, 780, 640, TEAL, 8)
            + caracol + texto(700, 400, "≈ 0,25 m/s", 80, TEAL, peso=800))


@escena(39, "Mielina y nódulos de Ranvier")
def _():
    m, nodos = mielina()
    s = axon(alto=56) + m
    for x in nodos:
        s += f'<rect x="{x - 20}" y="505" width="40" height="70" fill="{TEAL}" opacity=".85"/>'
    return (s + flecha(nodos[1], 770, nodos[1], 600, TEAL, 6) + texto(nodos[1], 825, "Nódulo de Ranvier", 44, TEAL, peso=800)
            + flecha(1250, 330, 1250, 455, NAVY, 6) + texto(1250, 300, "Vaina de mielina (aislante)", 44, NAVY, peso=700))


@escena(40, "Conducción saltatoria")
def _():
    m, nodos = mielina()
    s = axon(alto=56) + m
    for x in nodos:
        s += f'<rect x="{x - 20}" y="505" width="40" height="70" fill="{TEAL}" opacity=".85"/>'
    for a, b in zip(nodos, nodos[1:]):
        s += curva(f"M{a} 450C{a + 60} 300 {b - 60} 300 {b - 6} 440", TEAL, 10, True)
    return s + texto(960, 780, "hasta 100 m/s y con menos gasto de energía", 48, TEAL, peso=800)


# ---------------------------------------------------------------- 41-43 clínica
@escena(41, "Anestésicos locales: bloquean el canal de sodio")
def _():
    jer = (f'<g transform="rotate(35 1380 330)"><rect x="1230" y="290" width="300" height="80" rx="10" fill="white" stroke="{NAVY}" stroke-width="7"/>'
           f'<rect x="1250" y="306" width="170" height="48" fill="{TEAL_CLARO}"/>'
           f'<rect x="1530" y="318" width="90" height="24" fill="{NAVY}"/><rect x="1610" y="290" width="16" height="80" rx="6" fill="{NAVY}"/>'
           f'<line x1="1230" y1="330" x2="1110" y2="330" stroke="{NAVY}" stroke-width="6"/></g>')
    return (membrana(huecos=[(700, 66)]) + lados() + canal(700, "Na", "abierta", "abierta")
            + f'<circle cx="700" cy="{MY}" r="24" fill="{ROJO}"/>' + nube("Na", 7, (150, MY - 290, 1000, MY - 120), 41, evitar=[(700, MY - 200, 120)])
            + cruz(700, MY - 160, 30) + jer + texto(1000, MY + 230, "Lidocaína", 46, ROJO, "start", 800)
            + flecha(980, MY + 200, 735, MY + 22, ROJO, 6))


@escena(42, "Sin potencial de acción, el dolor no llega")
def _():
    cerebro = (f'<ellipse cx="1560" cy="520" rx="170" ry="130" fill="{GRIS}" stroke="{NAVY}" stroke-width="7"/>'
               + curva("M1440 500c40-50 90 10 120-30s80 0 110-20M1450 570c50-30 80 20 120-10s70 10 100-10", NAVY, 5)
               + texto(1560, 720, "Sistema nervioso central", 38, NAVY, peso=700))
    return (chispa(300, 520, 70) + texto(300, 680, "Dolor", 44, TEAL, peso=800)
            + curva("M390 520H880", TEAL, 14) + curva("M980 520H1380", GRIS, 14, punteada=True)
            + f'<rect x="900" y="420" width="60" height="200" rx="14" fill="{ROJO}"/>' + texto(930, 690, "bloqueo", 38, ROJO, peso=800)
            + cerebro)


@escena(43, "Enfermedades desmielinizantes")
def _():
    m, nodos = mielina(danada=(2, 3))
    return (axon(alto=56) + m + pulso(360, 540, 110, 50) + flecha(440, 420, 780, 420, TEAL, 10)
            + curva("M860 420H1250", TEAL, 8, True, True) + cruz(1380, 420, 30)
            + texto(1130, 760, "La conducción se enlentece o se bloquea", 46, NAVY, peso=700))


# ---------------------------------------------------------------- 44-46 cierre
def numero(x, y, n):
    return f'<circle cx="{x}" cy="{y}" r="58" fill="{TEAL}"/>' + texto(x, y + 24, n, 70, "white", peso=800)


@escena(44, "Resumen: el reposo es negativo")
def _():
    return (membrana(huecos=[(700, 62), (1250, 100)]) + canal_fuga(700) + bomba(1250, atp=False)
            + ion(700, MY + 180, "K") + ion(700, MY - 190, "K") + flecha(790, MY + 150, 790, MY - 150, NAVY, 10)
            + numero(200, 250, "1") + texto(290, 270, "Fuga de K⁺ + bomba = −70 mV", 52, NAVY, "start", 800))


@escena(45, "Resumen: entra sodio, sale potasio")
def _():
    g = Grafico(330, 240, 1100, 620)
    return (g.ejes() + g.traza() + g.traza(PA, 1.5, 2.05, TEAL, 16)
            + numero(g.px(0.85), g.py(-5), "2") + texto(g.px(0.85), g.py(-28), "Entra Na⁺", 42, TEAL, peso=800)
            + numero(g.px(3.4), g.py(-5), "3") + texto(g.px(3.4), g.py(-28), "Sale K⁺", 42, NAVY, peso=800))


@escena(46, "Próximo video: la sinapsis")
def _():
    return (neurona(300, 540, 560, 1.0) + neurona(1250, 540, 420, 1.0)
            + f'<circle cx="1010" cy="540" r="95" fill="none" stroke="{TEAL}" stroke-width="10" stroke-dasharray="18 14"/>'
            + texto(960, 860, "Contenido educativo. No reemplaza la consulta médica.", 36, "#7A869A", peso=600))


if __name__ == "__main__":
    destino = AQUI.parents[1] / "02_Imagenes" / "svg"
    destino.mkdir(parents=True, exist_ok=True)
    for n in sorted(E):
        (destino / f"escena_{n:03d}.svg").write_text(E[n](), encoding="utf-8")
    print(f"{len(E)} escenas dibujadas en {destino}")
