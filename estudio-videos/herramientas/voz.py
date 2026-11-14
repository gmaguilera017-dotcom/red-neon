#!/usr/bin/env python3
"""Genera la voz escena por escena con Piper y ajusta las duraciones del CSV.

Uso: python3 herramientas/voz.py <carpeta_video> <modelo.onnx> [pausa_segundos]
Requiere: pip install piper-tts  (y el modelo de voz .onnx con su .onnx.json)
Escribe 04_Voz/narracion.mp3 y pone en escenas.csv la duración real de cada frase.
"""
import csv
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

video, modelo = Path(sys.argv[1]), sys.argv[2]
pausa = float(sys.argv[3]) if len(sys.argv) > 3 else 0.45
archivo = video / "01_Guion" / "escenas.csv"
with archivo.open(encoding="utf-8-sig", newline="") as f:
    filas = list(csv.DictReader(f))

with tempfile.TemporaryDirectory() as tmp:
    lista = []
    for fila in filas:
        crudo, final = f"{tmp}/c{fila['n']}.wav", f"{tmp}/e{fila['n']}.wav"
        subprocess.run([sys.executable, "-m", "piper", "-m", modelo, "-f", crudo],
                       input=fila["narracion"], text=True, check=True, capture_output=True)
        # recorta silencios de los extremos y agrega una pausa fija al final
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", crudo, "-af",
                        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                        f"apad=pad_dur={pausa}", "-ar", "44100", "-ac", "1", final], check=True)
        with wave.open(final) as w:
            fila["duracion"] = f"{w.getnframes() / w.getframerate():.2f}"
        lista.append(f"file '{final}'")
        print(f"\r  escena {fila['n']}/{len(filas)}", end="", flush=True)
    Path(f"{tmp}/l.txt").write_text("\n".join(lista))
    salida = video / "04_Voz" / "narracion.mp3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/l.txt",
                    "-af", "loudnorm=I=-16:TP=-1.5", "-ar", "44100", "-b:a", "160k", str(salida)], check=True)

with archivo.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=filas[0].keys(), quoting=csv.QUOTE_MINIMAL)
    w.writeheader()
    w.writerows(filas)
total = sum(float(x["duracion"]) for x in filas)
print(f"\nListo: {salida} ({total / 60:.1f} min). Duraciones actualizadas en escenas.csv")
