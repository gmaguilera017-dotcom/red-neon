"""Piezas de dibujo en SVG para esquemas de fisiología (estilo pizarra NeoMed).

Cada función devuelve un trozo de SVG. Lienzo fijo de 1920x1080.
"""
import math
import random

W, H = 1920, 1080
NAVY, TEAL = "#1B2A49", "#00A8A8"
GRIS, TEAL_CLARO, ROJO = "#E6EAF0", "#CDEFEF", "#D64545"
MY = 560  # altura del centro de la membrana


def lienzo(titulo, cuerpo):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"
 font-family="Inter, DejaVu Sans, sans-serif">
<defs>
{"".join(f'<marker id="f{n}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{c}"/></marker>' for n, c in (("n", NAVY), ("t", TEAL), ("r", ROJO)))}
</defs>
<rect width="{W}" height="{H}" fill="white"/>
<text x="100" y="118" font-size="56" font-weight="700" fill="{NAVY}">{titulo}</text>
<rect x="100" y="140" width="120" height="8" rx="4" fill="{TEAL}"/>
{cuerpo}
</svg>'''


def texto(x, y, t, tam=36, color=NAVY, ancla="middle", peso=500):
    return (f'<text x="{x}" y="{y}" font-size="{tam}" font-weight="{peso}" fill="{color}" '
            f'text-anchor="{ancla}">{t}</text>')


def flecha(x1, y1, x2, y2, color=NAVY, ancho=8, punteada=False):
    m = {NAVY: "n", TEAL: "t", ROJO: "r"}.get(color, "n")
    d = ' stroke-dasharray="14 12"' if punteada else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{ancho}" '
            f'stroke-linecap="round" marker-end="url(#f{m})"{d}/>')


def curva(d, color=NAVY, ancho=8, flecha_fin=False, punteada=False):
    m = {NAVY: "n", TEAL: "t", ROJO: "r"}.get(color, "n")
    fin = f' marker-end="url(#f{m})"' if flecha_fin else ""
    dash = ' stroke-dasharray="14 12"' if punteada else ""
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{ancho}" '
            f'stroke-linecap="round" stroke-linejoin="round"{fin}{dash}/>')


# ------------------------------------------------------------------ membrana
def membrana(x0=80, x1=1840, huecos=(), y=MY):
    """Bicapa lipídica. huecos = [(x_centro, semiancho)] donde van proteínas."""
    s = [f'<rect x="{x0}" y="{y - 50}" width="{x1 - x0}" height="100" fill="{GRIS}" opacity=".55"/>']
    x = x0 + 17
    while x < x1:
        if not any(abs(x - c) < a for c, a in huecos):
            for sg in (-1, 1):
                s.append(f'<line x1="{x}" y1="{y + sg * 38}" x2="{x}" y2="{y + sg * 6}" stroke="{NAVY}" stroke-width="3"/>')
                s.append(f'<circle cx="{x}" cy="{y + sg * 52}" r="14" fill="white" stroke="{NAVY}" stroke-width="4"/>')
        x += 34
    return "".join(s)


def lados(y=MY):
    return (texto(110, y - 330, "EXTERIOR", 30, "#7A869A", "start", 700)
            + texto(110, y + 350, "INTERIOR", 30, "#7A869A", "start", 700))


def ion(x, y, tipo="Na", r=26):
    if tipo == "Na":
        return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="white" stroke="{TEAL}" stroke-width="5"/>'
                f'<text x="{x}" y="{y + 8}" font-size="22" font-weight="700" fill="{TEAL}" text-anchor="middle">Na<tspan dy="-8" font-size="16">+</tspan></text>')
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{NAVY}"/>'
            f'<text x="{x}" y="{y + 8}" font-size="22" font-weight="700" fill="white" text-anchor="middle">K<tspan dy="-8" font-size="16">+</tspan></text>')


def proteina(x, y):
    return (f'<ellipse cx="{x}" cy="{y}" rx="52" ry="34" fill="{GRIS}" stroke="{NAVY}" stroke-width="4"/>'
            + texto(x, y + 14, "−", 44, NAVY, peso=700))


def nube(tipo, n, zona, semilla, evitar=(), extra=()):
    """n iones repartidos en zona=(x0,y0,x1,y1) sin encimarse. evitar=[(x,y,radio)]."""
    rnd, pts = random.Random(semilla), list(extra)
    out, intentos = [], 0
    while len(out) < n and intentos < 5000:
        intentos += 1
        x, y = rnd.uniform(zona[0], zona[2]), rnd.uniform(zona[1], zona[3])
        if all(math.hypot(x - a, y - b) > 62 for a, b in pts) and \
           all(math.hypot(x - a, y - b) > r for a, b, r in evitar):
            pts.append((x, y))
            out.append(ion(round(x), round(y), tipo))
    return "".join(out)


AFUERA = (120, MY - 290, 1800, MY - 110)
ADENTRO = (120, MY + 110, 1800, MY + 300)


def canal(x, tipo="Na", activacion="cerrada", inactivacion=None, y=MY, rotulo=None):
    """Canal activado por voltaje. activacion: cerrada/abierta/media.
    inactivacion (solo Na): None, 'abierta' o 'cerrada' (bola tapando el poro)."""
    col = TEAL if tipo == "Na" else NAVY
    rel = TEAL_CLARO if tipo == "Na" else "#C9D2E3"
    s = [f'<rect x="{x - 24}" y="{y - 80}" width="48" height="160" fill="white"/>']
    for dx in (-62, 24):
        s.append(f'<rect x="{x + dx}" y="{y - 92}" width="38" height="184" rx="17" fill="{rel}" stroke="{col}" stroke-width="5"/>')
    if activacion == "cerrada":
        s.append(f'<line x1="{x - 26}" y1="{y - 62}" x2="{x + 26}" y2="{y - 62}" stroke="{col}" stroke-width="12" stroke-linecap="round"/>')
    else:
        ang = -70 if activacion == "abierta" else -30
        ex = x - 24 + 50 * math.cos(math.radians(ang))
        ey = y - 62 + 50 * math.sin(math.radians(ang))
        s.append(f'<line x1="{x - 24}" y1="{y - 62}" x2="{ex:.0f}" y2="{ey:.0f}" stroke="{col}" stroke-width="12" stroke-linecap="round"/>')
    if inactivacion == "abierta":
        s.append(curva(f"M{x + 43} {y + 92} q20 40 50 46", col, 4))
        s.append(f'<circle cx="{x + 108}" cy="{y + 142}" r="19" fill="{col}"/>')
    elif inactivacion == "cerrada":
        s.append(curva(f"M{x + 43} {y + 92} q0 36 -30 8", col, 4))
        s.append(f'<circle cx="{x}" cy="{y + 78}" r="21" fill="{col}"/>')
    if rotulo:
        s.append(texto(x, y + 215, rotulo, 32, col, peso=700))
    return "".join(s)


def canal_fuga(x, y=MY):
    return (f'<rect x="{x - 24}" y="{y - 80}" width="48" height="160" fill="white"/>'
            + "".join(f'<rect x="{x + dx}" y="{y - 86}" width="34" height="172" rx="15" fill="#C9D2E3" stroke="{NAVY}" stroke-width="5"/>' for dx in (-56, 22)))


def bomba(x, y=MY, atp=True):
    s = (f'<ellipse cx="{x}" cy="{y}" rx="92" ry="118" fill="{TEAL_CLARO}" stroke="{TEAL}" stroke-width="6"/>'
         + texto(x, y - 8, "Bomba", 30, NAVY, peso=700) + texto(x, y + 30, "Na⁺/K⁺", 28, NAVY, peso=600))
    if atp:
        p = " ".join(f"{x + 170 + (58 if i % 2 == 0 else 34) * math.cos(i * math.pi / 8):.0f},"
                     f"{y + 190 + (58 if i % 2 == 0 else 34) * math.sin(i * math.pi / 8):.0f}" for i in range(16))
        s += (f'<polygon points="{p}" fill="#FFE9A8" stroke="{NAVY}" stroke-width="4"/>'
              + texto(x + 170, y + 201, "ATP", 28, NAVY, peso=800))
    return s


# ------------------------------------------------------------------ gráfico
PA = [(0, -70), (1.0, -70), (1.5, -56), (2.05, 35), (3.3, -82), (5.2, -70), (6, -70)]
SUB = [(0, -70), (1.0, -70), (1.7, -61), (2.7, -70), (6, -70)]


def _v(pts, t):
    for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            k = (1 - math.cos(math.pi * (t - t0) / (t1 - t0))) / 2
            return v0 + (v1 - v0) * k
    return pts[-1][1]


class Grafico:
    def __init__(self, x=330, y=220, w=1300, h=640, tmax=6.0):
        self.x, self.y, self.w, self.h, self.tmax = x, y, w, h, tmax

    def px(self, t):
        return self.x + self.w * t / self.tmax

    def py(self, v):
        return self.y + self.h * (50 - v) / 145

    def ejes(self, marcas=(35, 0, -55, -70), umbral=True, chico=False):
        tam = 24 if chico else 32
        s = [curva(f"M{self.x} {self.y - 10}V{self.y + self.h}H{self.x + self.w + 10}", NAVY, 5)]
        for v in marcas:
            y = self.py(v)
            s.append(f'<line x1="{self.x - 14}" y1="{y}" x2="{self.x}" y2="{y}" stroke="{NAVY}" stroke-width="5"/>')
            s.append(texto(self.x - 26, y + tam * .35, f"{'+' if v > 0 else ''}{v}".replace("-", "−"), tam, NAVY, "end", 600))
        if not chico:
            s.append(texto(self.x - 26, self.y - 30, "mV", 30, "#7A869A", "end", 700))
            s.append(texto(self.x + self.w, self.y + self.h + 50, "tiempo (ms)", 30, "#7A869A", "end", 700))
        if umbral:
            y = self.py(-55)
            s.append(f'<line x1="{self.x}" y1="{y}" x2="{self.x + self.w}" y2="{y}" stroke="#7A869A" stroke-width="4" stroke-dasharray="16 12"/>')
            if not chico:
                s.append(texto(self.x + self.w, y - 16, "umbral", 30, "#7A869A", "end", 700))
        return "".join(s)

    def traza(self, pts=PA, t0=0, t1=None, color=NAVY, ancho=9, dt=0):
        t1 = self.tmax if t1 is None else t1
        n = max(2, int((t1 - t0) * 60))
        d = "M" + " L".join(f"{self.px(t0 + (t1 - t0) * i / n + dt):.1f} {self.py(_v(pts, t0 + (t1 - t0) * i / n)):.1f}"
                            for i in range(n + 1))
        return curva(d, color, ancho)

    def banda(self, t0, t1, color=TEAL, op=.22):
        return (f'<rect x="{self.px(t0)}" y="{self.y}" width="{self.px(t1) - self.px(t0)}" height="{self.h}" '
                f'fill="{color}" opacity="{op}"/>')


# ------------------------------------------------------------------ neurona y axón
def neurona(x, y, largo=700, e=1.0, color=NAVY):
    s = []
    for a in (100, 140, 180, 220, 260):
        r = math.radians(a)
        x1, y1 = x + 62 * e * math.cos(r), y + 62 * e * math.sin(r)
        x2, y2 = x + 150 * e * math.cos(r), y + 150 * e * math.sin(r)
        s.append(curva(f"M{x1:.0f} {y1:.0f}L{x2:.0f} {y2:.0f}", color, 7))
        for da in (-28, 28):
            r2 = math.radians(a + da)
            s.append(curva(f"M{x2:.0f} {y2:.0f}l{50 * e * math.cos(r2):.0f} {50 * e * math.sin(r2):.0f}", color, 5))
    s.append(curva(f"M{x + 60 * e} {y}H{x + largo}", color, 12))
    for dy in (-46, 0, 46):
        s.append(curva(f"M{x + largo} {y}l60 {dy}", color, 6))
        s.append(f'<circle cx="{x + largo + 68}" cy="{y + dy}" r="11" fill="{color}"/>')
    s.append(f'<circle cx="{x}" cy="{y}" r="{66 * e}" fill="white" stroke="{color}" stroke-width="7"/>')
    s.append(f'<circle cx="{x}" cy="{y}" r="{22 * e}" fill="{GRIS}" stroke="{color}" stroke-width="4"/>')
    return "".join(s)


def axon(x0=140, x1=1780, y=540, alto=80):
    return (f'<rect x="{x0}" y="{y - alto / 2}" width="{x1 - x0}" height="{alto}" rx="{alto / 2}" '
            f'fill="#F3F6FA" stroke="{NAVY}" stroke-width="6"/>')


def pulso(x, y=540, ancho=150, alto=80):
    return (f'<rect x="{x - ancho / 2}" y="{y - alto / 2 + 5}" width="{ancho}" height="{alto - 10}" rx="34" '
            f'fill="{TEAL}" opacity=".85"/>')


def mielina(x0=220, x1=1700, y=540, n=5, hueco=44, danada=()):
    largo = (x1 - x0 - hueco * (n - 1)) / n
    s, nodos = [], []
    for i in range(n):
        x = x0 + i * (largo + hueco)
        if i in danada:
            for k in range(3):
                s.append(f'<rect x="{x + 20 + k * largo / 3}" y="{y - 58 + 14 * (k % 2)}" width="{largo / 5}" '
                         f'height="{116 - 28 * (k % 2)}" rx="20" fill="{GRIS}" stroke="{NAVY}" stroke-width="4" '
                         f'stroke-dasharray="10 10" opacity=".8"/>')
        else:
            s.append(f'<rect x="{x}" y="{y - 70}" width="{largo}" height="140" rx="56" fill="{GRIS}" '
                     f'stroke="{NAVY}" stroke-width="6"/>')
        if i < n - 1:
            nodos.append(x + largo + hueco / 2)
    return "".join(s), nodos
