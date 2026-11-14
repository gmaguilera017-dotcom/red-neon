# Estudio de montaje de videos

Dos canales, un mismo flujo: **popular** (`canales/popular`) y **médico educativo**
(`canales/medico`). Basado en el flujo del video analizado (ver al final).

## Flujo por video

| Paso | Qué se hace | Dónde | Resultado |
|---|---|---|---|
| 1 | Crear el proyecto | `estudio.py nuevo` | carpetas `00_…06_` |
| 2 | Guion + escenas + reels | Claude con `plantillas/prompt_maestro.md` + `canal.md` | `01_Guion/guion.md`, `escenas.csv`, `reels.csv` |
| 3 | Imágenes (una por escena) | Google Flow u otro generador, con `personaje_principal.jpg` de referencia | `02_Imagenes/escena_001.png`… |
| 4 | Animar ~10 % de las escenas (opcional) | mismo generador, imagen → video | `03_Animaciones/escena_012.mp4`… |
| 5 | Voz | grabación propia o TTS (ElevenLabs, etc.) leyendo `guion.md` | `04_Voz/narracion.mp3` |
| 6 | Música (opcional) | biblioteca libre de derechos | `05_Musica/musica.mp3` |
| 7 | Montaje del video largo | `estudio.py montar` | `06_Final/video_largo.mp4` + `subtitulos.srt` |
| 8 | Reels verticales | `estudio.py reels` | `06_Final/reels/*.mp4` |

## Comandos

Requiere Python 3 y ffmpeg. Desde la carpeta `estudio-videos/`:

```bash
python3 herramientas/estudio.py nuevo popular "9 hábitos que te cambian la vida"
python3 herramientas/estudio.py montar canales/popular/videos/01_9_habitos_que_te_cambian_la_vida --borrador
python3 herramientas/estudio.py montar canales/popular/videos/01_9_habitos_que_te_cambian_la_vida --subs
python3 herramientas/estudio.py reels  canales/popular/videos/01_9_habitos_que_te_cambian_la_vida
```

- `--borrador`: rápido y sin zoom, para revisar orden y ritmo.
- `--subs`: quema los subtítulos (si no, queda el `.srt` para subir a YouTube).
- Si existe `04_Voz/narracion.*`, las duraciones de las escenas se estiran en proporción para
  cubrir exactamente la voz. Sin voz, se usan las duraciones del CSV.
- Si falta una imagen, aparece un cartel gris "FALTA ESCENA N" y el montaje no se frena.
- Si hay un clip en `03_Animaciones` con el mismo nombre que la imagen, se usa el clip.
- Los nombres deben ser `escena_001`, `escena_002`… (tres dígitos, igual a la columna `n`).

## Ajustes por canal

`canales/<canal>/canal.json`: resolución, fps, segundos por escena, color de fondo, fuente y
volumen de música. `canales/<canal>/canal.md`: nicho, estilo, tono y reglas (completar los
**(definir)**).

## Qué mostraba el video de referencia

- Promesa: monetizar un canal en ~8 semanas apoyándose en IA (las cifras mostradas son del autor
  y promocionan su academia paga; tomarlas como publicidad, no como resultado esperable).
- Método: elegir un canal de referencia del nicho (el ejemplo: caricaturas simples, 38 videos) →
  darle el link a Claude para que lo analice y haga preguntas → Claude entrega guion de ~10 min,
  164 escenas de ~4 s con narración y prompt, y un personaje fijo guardado como referencia →
  imágenes generadas en Google Flow → animar algunas → cortar ~11 reels desde el video largo
  (imagen horizontal centrada sobre fondo blanco) → montaje final.
- Este estudio reproduce ese flujo y agrega lo que el video no muestra: el montaje automático
  y las reglas de calidad para contenido médico.
