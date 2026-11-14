# Prompt maestro — de la idea a las escenas

Pegar en Claude junto con la ficha del canal (`canales/<canal>/canal.md`). Reemplazar lo que
está entre `<< >>`.

---

Sos el productor de mi canal. Abajo va la ficha del canal; respetala en todo.

**Tema del video:** << tema >>
**Canal o video de referencia (solo para estructura y ritmo, no copiar):** << link >>
**Duración objetivo:** << 8-10 >> minutos.
**Fuente del contenido (obligatoria en el canal médico):** << libro/capítulo/guía o texto pegado >>

Trabajá en este orden y esperá mi OK entre pasos:

1. **Análisis de la referencia** (máx. 10 líneas): gancho, estructura, ritmo de imágenes, tipo de
   título y miniatura, qué hace que retenga.
2. **3 opciones de título + idea de miniatura.**
3. **Guion** (`guion.md`): texto corrido para narrar, ~150 palabras por minuto, gancho en los
   primeros 15 s, cierre con llamado a la acción. En el canal médico: bibliografía al final y el
   aviso "Contenido educativo. No reemplaza la consulta médica."
4. **Escenas** (`escenas.csv`): partir el guion en escenas de la duración indicada en la ficha.
   Columnas exactas: `n,duracion,narracion,prompt,animar`
   - `narracion`: la frase exacta del guion que se oye en esa escena (en español).
   - `prompt`: EN INGLÉS, solo lo que se dibuja en esa escena (el bloque de estilo y el
     personaje se agregan solos desde `canal.json`). Sin texto dentro de la imagen.
   - `animar`: `si` en ~10 % de las escenas (las de más impacto), `no` en el resto.
5. **Reels** (`reels.csv`): 5-10 cortes de 30-50 s que funcionen solos.
   Columnas: `nombre,escena_desde,escena_hasta,titulo` (números de escena, no tiempos).
6. **Publicación:** descripción, capítulos con tiempos, 10 etiquetas.

Entregá los CSV en bloques de código para copiarlos tal cual.
