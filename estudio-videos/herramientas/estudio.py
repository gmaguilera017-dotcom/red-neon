#!/usr/bin/env python3
"""Estudio de montaje: crea proyectos de video, monta el video largo y corta reels.

Uso:
  python3 herramientas/estudio.py nuevo  <canal> "<titulo>"
  python3 herramientas/estudio.py montar <carpeta_video> [--subs] [--borrador]
  python3 herramientas/estudio.py reels  <carpeta_video>

Solo requiere Python 3 y ffmpeg instalados.
"""
import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")
VID_EXT = (".mp4", ".mov", ".webm")
AUD_EXT = (".mp3", ".wav", ".m4a", ".aac")


def ff(*args):
    cmd = ["ffmpeg", "-v", "error", "-y", *map(str, args)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"ffmpeg falló:\n{' '.join(cmd)}\n{r.stderr}")


def duracion(archivo):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(archivo)], capture_output=True, text=True)
    return float(r.stdout.strip())


def slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "_", t).strip("_")[:60]


def cargar_canal(carpeta_video):
    """El canal es la carpeta dos niveles arriba: canales/<canal>/videos/<video>."""
    cfg = carpeta_video.resolve().parent.parent / "canal.json"
    if not cfg.exists():
        sys.exit(f"No encuentro {cfg}")
    return json.loads(cfg.read_text(encoding="utf-8"))


def buscar(carpeta, base, extensiones):
    for ext in extensiones:
        p = carpeta / f"{base}{ext}"
        if p.exists():
            return p
    return None


def leer_escenas(carpeta_video, canal):
    archivo = carpeta_video / "01_Guion" / "escenas.csv"
    if not archivo.exists():
        sys.exit(f"Falta {archivo}")
    escenas = []
    with archivo.open(encoding="utf-8-sig", newline="") as f:
        for fila in csv.DictReader(f):
            if not (fila.get("n") or "").strip():
                continue
            escenas.append({
                "n": int(fila["n"]),
                "dur": float(fila.get("duracion") or canal["segundos_por_escena"]),
                "texto": (fila.get("narracion") or "").strip(),
            })
    if not escenas:
        sys.exit("escenas.csv está vacío")
    return escenas


# ---------------------------------------------------------------- nuevo
def cmd_nuevo(a):
    canal_dir = RAIZ / "canales" / a.canal
    if not (canal_dir / "canal.json").exists():
        disponibles = [p.parent.name for p in (RAIZ / "canales").glob("*/canal.json")]
        sys.exit(f"Canal '{a.canal}' no existe. Disponibles: {', '.join(disponibles)}")
    videos = canal_dir / "videos"
    videos.mkdir(exist_ok=True)
    numero = len([p for p in videos.iterdir() if p.is_dir()]) + 1
    destino = videos / f"{numero:02d}_{slug(a.titulo)}"
    for sub in ("00_Referencias", "01_Guion", "02_Imagenes", "03_Animaciones",
                "04_Voz", "05_Musica", "06_Final"):
        (destino / sub).mkdir(parents=True)
        (destino / sub / ".gitkeep").touch()
    shutil.copy(RAIZ / "plantillas" / "escenas.csv", destino / "01_Guion" / "escenas.csv")
    shutil.copy(RAIZ / "plantillas" / "reels.csv", destino / "01_Guion" / "reels.csv")
    (destino / "01_Guion" / "guion.md").write_text(f"# {a.titulo}\n\n", encoding="utf-8")
    print(f"Proyecto creado: {destino.relative_to(RAIZ)}")


# ---------------------------------------------------------------- montar
def segmento_imagen(img, salida, dur, i, W, H, fps, fondo, borrador):
    frames = max(1, round(dur * fps))
    if borrador:
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
              f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color={fondo},fps={fps}")
    else:
        # Zoom suave alternando acercar / alejar (efecto Ken Burns)
        z = ("min(1+0.0009*on,1.12)" if i % 2 == 0
             else "max(1.12-0.0009*on,1)")
        vf = (f"scale={W * 2}:{H * 2}:force_original_aspect_ratio=decrease,"
              f"pad={W * 2}:{H * 2}:(ow-iw)/2:(oh-ih)/2:color={fondo},"
              f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
              f":d={frames}:s={W}x{H}:fps={fps}")
    ff("-loop", "1", "-i", img, "-vf", vf, "-frames:v", frames,
       "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-an", salida)


def segmento_clip(clip, salida, dur, W, H, fps, fondo):
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color={fondo},fps={fps}")
    ff("-stream_loop", "-1", "-i", clip, "-t", f"{dur:.3f}", "-vf", vf,
       "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-an", salida)


def segmento_faltante(salida, dur, n, W, H, fps):
    vf = (f"drawtext=text='FALTA ESCENA {n:03d}':fontcolor=white:fontsize={H // 12}"
          f":x=(w-text_w)/2:y=(h-text_h)/2")
    ff("-f", "lavfi", "-i", f"color=c=0x333333:s={W}x{H}:r={fps}:d={dur:.3f}",
       "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", salida)


def t_srt(s):
    ms = round(s * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def cmd_montar(a):
    video = Path(a.carpeta)
    canal = cargar_canal(video)
    W, H, fps, fondo = canal["ancho"], canal["alto"], canal["fps"], canal["color_fondo"]
    escenas = leer_escenas(video, canal)

    voz = buscar(video / "04_Voz", "narracion", AUD_EXT)
    if voz:
        # La voz manda: se reparte su duración entre las escenas en proporción
        factor = duracion(voz) / sum(e["dur"] for e in escenas)
        for e in escenas:
            e["dur"] *= factor
        print(f"Voz encontrada ({duracion(voz):.1f}s): duraciones ajustadas x{factor:.2f}")
    else:
        print("Sin 04_Voz/narracion.*: se monta sin voz con las duraciones del CSV")

    tmp = video / "06_Final" / "_tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    faltan, lista = [], []
    for i, e in enumerate(escenas):
        base = f"escena_{e['n']:03d}"
        seg = tmp / f"{base}.mp4"
        clip = buscar(video / "03_Animaciones", base, VID_EXT)
        img = buscar(video / "02_Imagenes", base, IMG_EXT)
        if clip:
            segmento_clip(clip, seg, e["dur"], W, H, fps, fondo)
        elif img:
            segmento_imagen(img, seg, e["dur"], i, W, H, fps, fondo, a.borrador)
        else:
            faltan.append(e["n"])
            segmento_faltante(seg, e["dur"], e["n"], W, H, fps)
        lista.append(f"file '{seg.name}'")
        print(f"\r  escena {i + 1}/{len(escenas)}", end="", flush=True)
    print()
    (tmp / "lista.txt").write_text("\n".join(lista), encoding="utf-8")

    # Subtítulos .srt a partir de la narración de cada escena
    srt, t = [], 0.0
    for k, e in enumerate(escenas, 1):
        if e["texto"]:
            srt.append(f"{k}\n{t_srt(t)} --> {t_srt(t + e['dur'])}\n{e['texto']}\n")
        t += e["dur"]
    srt_path = video / "06_Final" / "subtitulos.srt"
    srt_path.write_text("\n".join(srt), encoding="utf-8")

    mudo = tmp / "mudo.mp4"
    ff("-f", "concat", "-safe", "0", "-i", tmp / "lista.txt", "-c", "copy", mudo)

    musica = buscar(video / "05_Musica", "musica", AUD_EXT)
    entradas, filtros, mapas = ["-i", mudo], [], ["-map", "0:v"]
    vf = None
    if a.subs and srt:
        ruta = str(srt_path.resolve()).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
        vf = (f"subtitles='{ruta}':force_style='FontName={canal['fuente']},"
              f"FontSize={canal['tamano_subtitulos']},Outline=2,MarginV=40'")
    if voz:
        entradas += ["-i", voz]
    if musica:
        entradas += ["-stream_loop", "-1", "-i", musica]
    if voz and musica:
        filtros = ["-filter_complex",
                   f"[2:a]volume={canal['volumen_musica']}[m];"
                   f"[1:a][m]amix=inputs=2:duration=first:normalize=0[a]"]
        mapas += ["-map", "[a]"]
    elif voz:
        mapas += ["-map", "1:a"]
    elif musica:
        filtros = ["-filter_complex", f"[1:a]volume={canal['volumen_musica']}[a]"]
        mapas += ["-map", "[a]"]
    salida = video / "06_Final" / "video_largo.mp4"
    codec_v = ["-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
               "-pix_fmt", "yuv420p"] if vf else ["-c:v", "copy"]
    ff(*entradas, *filtros, *mapas, *codec_v, "-c:a", "aac", "-b:a", "192k",
       "-shortest", "-movflags", "+faststart", salida)
    shutil.rmtree(tmp)
    print(f"Listo: {salida}  ({duracion(salida):.1f}s, {len(escenas)} escenas)")
    if faltan:
        print(f"ATENCIÓN: faltan {len(faltan)} imágenes (escenas {faltan[:15]}"
              f"{'...' if len(faltan) > 15 else ''}); se usó un cartel gris.")


# ---------------------------------------------------------------- reels
def a_segundos(t):
    partes = [float(p) for p in str(t).strip().split(":")]
    return sum(p * 60 ** i for i, p in enumerate(reversed(partes)))


def cmd_reels(a):
    video = Path(a.carpeta)
    canal = cargar_canal(video)
    origen = video / "06_Final" / "video_largo.mp4"
    if not origen.exists():
        sys.exit("Primero hay que montar el video largo (comando 'montar').")
    fondo, fuente_archivo = canal["color_fondo"], canal.get("fuente_archivo", "")
    destino = video / "06_Final" / "reels"
    destino.mkdir(exist_ok=True)
    total = duracion(origen)
    with (video / "01_Guion" / "reels.csv").open(encoding="utf-8-sig", newline="") as f:
        filas = [r for r in csv.DictReader(f) if (r.get("nombre") or "").strip()]
    for r in filas:
        ini, fin = a_segundos(r["desde"]), min(a_segundos(r["hasta"]), total)
        if fin <= ini:
            print(f"  {r['nombre']}: fuera del video, se omite")
            continue
        # Imagen horizontal centrada sobre fondo del canal, título arriba
        vf = f"scale=1080:-2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color={fondo}"
        titulo = (r.get("titulo") or "").strip()
        if titulo:
            txt = destino / "_titulo.txt"
            txt.write_text(titulo, encoding="utf-8")
            fuente = f":fontfile='{fuente_archivo}'" if fuente_archivo else ""
            vf += (f",drawtext=textfile='{txt}'{fuente}:fontsize=64"
                   f":fontcolor={canal['color_texto']}:x=(w-text_w)/2:y=330")
        salida = destino / f"{slug(r['nombre'])}.mp4"
        ff("-ss", f"{ini:.3f}", "-i", origen, "-t", f"{fin - ini:.3f}", "-vf", vf,
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-movflags", "+faststart", salida)
        print(f"  {salida.name}  ({fin - ini:.0f}s)")
    (destino / "_titulo.txt").unlink(missing_ok=True)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("nuevo", help="crea la carpeta de un video nuevo")
    n.add_argument("canal")
    n.add_argument("titulo")
    n.set_defaults(f=cmd_nuevo)
    m = sub.add_parser("montar", help="arma el video largo 16:9")
    m.add_argument("carpeta")
    m.add_argument("--subs", action="store_true", help="quema los subtítulos en el video")
    m.add_argument("--borrador", action="store_true", help="rápido, sin zoom")
    m.set_defaults(f=cmd_montar)
    r = sub.add_parser("reels", help="corta reels verticales 9:16 según reels.csv")
    r.add_argument("carpeta")
    r.set_defaults(f=cmd_reels)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
