# Guía completa — de cero a canal publicado

Empezá por acá. Está pensada para seguirla sin ayuda, en orden.

## Qué hay ya hecho

| | NeoMed Fisiología | Cuerpo Curioso |
|---|---|---|
| Ficha y reglas del canal | `canales/medico/canal.md` | `canales/popular/canal.md` |
| Kit para crear el canal (textos listos) | `canales/medico/kit_canal.md` | `canales/popular/kit_canal.md` |
| Perfil, banner y marca de agua | `canales/medico/marca/` | `canales/popular/marca/` |
| Videos guionados (guion, escenas, prompts, reels) | 01 Potencial de acción · 02 Sinapsis · 03 Contracción muscular · 04 Placa neuromuscular · 05 Ciclo cardíaco · 06 Potencial cardíaco · 07 Gasto cardíaco · 08 Presión arterial | 01 No dormir · 02 Sueño después de comer · 03 Estrés · 04 Memoria y estudio · 05 24 horas sin comer · 06 Café · 07 Enamorarse · 08 Dolor de cabeza |
| Plan de temas siguientes | 12 videos | 10 videos |
| Prompt para guionar más videos con cualquier IA | `plantillas/prompt_listo_neomed.md` | `plantillas/prompt_listo_cuerpo_curioso.md` |

Qué equipo y qué suscripciones hacen falta (y cuáles no): [`EQUIPAMIENTO.md`](EQUIPAMIENTO.md).

Lo que falta en todos los videos: **revisar el guion, generar las imágenes, grabar la voz y montar.**

---

## Etapa 1 — Crear los canales (una sola vez, ~40 minutos)

1. Entrar a youtube.com con tu cuenta de Google → foto de perfil → **Crear un canal**.
   Para el segundo canal: Configuración → **Agregar o administrar tus canales** → Crear canal
   (queda como "cuenta de marca", se administra con el mismo usuario).
2. En cada canal, abrir **YouTube Studio → Personalización**:
   - *Perfil:* nombre, identificador (@) y descripción → copiarlos de `kit_canal.md`.
   - *Imagen:* subir `marca/perfil.png`, `marca/banner.png` y `marca/marca_de_agua.png`.
3. **Configuración → Canal:** país Argentina, palabras clave del kit, "no es contenido para niños".
4. **Configuración → Valores predeterminados de carga:** pegar la "descripción fija" del kit,
   categoría Educación, idioma español.
5. **Verificar el canal con tu teléfono** (Configuración → Canal → Elegibilidad para funciones):
   habilita miniaturas personalizadas y videos de más de 15 minutos.
6. Crear las listas de reproducción del kit (vacías).
7. Opcional: abrir Instagram y TikTok con el mismo nombre e imagen de perfil para reservar el
   usuario y publicar ahí los mismos reels.

## Etapa 2 — Producir un video (repetir por cada video)

Cada video vive en `canales/<canal>/videos/NN_<titulo>/`.

1. **Revisar el guion.** Abrir `01_Guion/guion.md`, completar la lista de verificación con el
   libro o la fuente a la vista y corregir las frases en `01_Guion/escenas.csv` (columna
   `narracion`). Si cambiás texto, volver a correr el comando `prompts` (ver etapa 3) o editar
   también `04_Voz/texto_para_voz.txt`.
2. **Generar las imágenes.** En Google Flow (labs.google/flow): proyecto nuevo, modo imagen,
   formato 16:9. Abrir `01_Guion/prompts_para_flow.txt`, pegar el texto de cada escena (sin la
   línea `[escena_NNN]`) y descargar el resultado como `escena_001.png`, `escena_002.png`…
   en `02_Imagenes/`. Con las primeras 2-3 que te gusten, usarlas como imagen de referencia
   para que el resto mantenga el estilo. En el canal médico, revisar que cada esquema sea
   correcto.
3. **Animar (opcional).** Las escenas marcadas `(ANIMAR)`: imagen → video en Flow, guardar en
   `03_Animaciones/` con el mismo nombre (`escena_007.mp4`).
4. **Grabar la voz.** Leer `04_Voz/texto_para_voz.txt` de corrido, a ritmo parejo, sin agregar
   ni saltear frases. Guardar como `04_Voz/narracion.mp3` (o `.m4a`, `.wav`).
5. **Música (opcional).** Un tema de la Biblioteca de audio de YouTube Studio (gratis y sin
   reclamos) como `05_Musica/musica.mp3`. Queda de fondo, a volumen bajo.
6. **Miniatura.** 1280×720, con la idea que figura en `guion.md`. Se puede hacer en Canva con
   una de las imágenes del video y 2-4 palabras grandes.

## Etapa 3 — Montar

Elegí una de las tres opciones.

**A. En GitHub, sin instalar nada.** Requiere que esta carpeta esté en la rama principal del
repositorio. Subir las imágenes y la voz a las carpetas del video (botón *Add file → Upload
files*), luego pestaña **Actions → Montar video → Run workflow**, pegar la carpeta del video
(ej. `canales/medico/videos/01_Potencial_de_accion_paso_a_paso`) y ejecutar. A los pocos
minutos, descargar `video-montado` desde el resumen de la ejecución: trae el video largo, los
reels y los subtítulos.

**B. En tu computadora.** Instalar Python (python.org) y ffmpeg (en Windows:
`winget install Gyan.FFmpeg`). Descargar el repositorio (Code → Download ZIP), abrir una
terminal dentro de `estudio-videos` y correr:

```
python herramientas/estudio.py prompts canales/medico/videos/01_Potencial_de_accion_paso_a_paso
python herramientas/estudio.py montar  canales/medico/videos/01_Potencial_de_accion_paso_a_paso
python herramientas/estudio.py reels   canales/medico/videos/01_Potencial_de_accion_paso_a_paso
```

El resultado queda en `06_Final/`. Para un video nuevo:
`python herramientas/estudio.py nuevo medico "Título del video"`.

**C. A mano en CapCut** (si no querés usar el montador). Importar las imágenes en orden y la
voz; dar a cada imagen la duración de su frase; exportar en 1080p. Para los reels: proyecto
9:16, pegar el tramo de escenas que indica `01_Guion/reels.csv`.

Sincronía: el montador reparte la duración de la voz entre las escenas en proporción. Si alguna
imagen entra antes o después de su frase, ajustar el número de la columna `duracion` de esa
escena en `escenas.csv` (más grande = dura más) y volver a montar.

## Etapa 4 — Publicar

1. YouTube Studio → **Crear → Subir video** → `06_Final/video_largo.mp4`.
2. Título, descripción y etiquetas: sección "Publicación" de `guion.md`. Debajo queda la
   descripción fija del canal.
3. Subir la miniatura y agregar el video a su lista de reproducción.
4. Subtítulos: subir `06_Final/subtitulos.srt` (español).
5. Marcar **contenido alterado o sintético: Sí** si usaste imágenes o voz de IA.
6. Programar día y hora según el calendario del kit.
7. Publicar el comentario fijado del kit.
8. Reels: subir cada archivo de `06_Final/reels/` como Short (duran menos de 3 minutos y son
   verticales, YouTube los detecta solo). En la descripción, mencionar el video largo.
   Los mismos archivos sirven para Instagram Reels y TikTok.

## Etapa 5 — Guionar los videos siguientes

Abrir `plantillas/prompt_listo_<canal>.md`, copiar el bloque, escribir el tema (el próximo de
la tabla de `canal.md`) y enviarlo a cualquier asistente de IA. Guardar las respuestas como
`01_Guion/escenas.csv` y `01_Guion/reels.csv` del video nuevo (creado con el comando `nuevo`
o copiando una carpeta de video existente) y seguir desde la etapa 2.

## Monetización: qué esperar

- **Requisitos actuales del Programa de Socios de YouTube** (confirmar en la página oficial):
  1.000 suscriptores y 4.000 horas de reproducción en 12 meses, o 10 millones de vistas de
  Shorts en 90 días. Con 500 suscriptores se habilitan funciones de apoyo de fans.
- **Cambio anunciado:** desde el 1 de febrero de 2027 se duplican las horas y las vistas de
  Shorts exigidas a los canales nuevos. Conviene publicar con constancia desde ya.
- **Contenido con IA:** YouTube no monetiza contenido repetitivo o producido en masa sin aporte
  propio. Lo que protege a estos canales es tu revisión médica, la voz propia y el guion
  original; por eso no conviene publicar los borradores sin revisar.
- El video que originó este proyecto prometía monetizar en 8 semanas; es publicidad de un
  curso. Un plazo realista para un canal nuevo es de varios meses de publicación semanal.

## Lista de control por video

- [ ] Guion revisado y lista de verificación completa
- [ ] Imágenes generadas, numeradas y revisadas
- [ ] Voz grabada como `narracion.mp3`
- [ ] Video y reels montados y vistos de principio a fin
- [ ] Miniatura
- [ ] Título, descripción, etiquetas, lista de reproducción, subtítulos
- [ ] Marcado como contenido sintético si corresponde
- [ ] Programado · comentario fijado · reels subidos
