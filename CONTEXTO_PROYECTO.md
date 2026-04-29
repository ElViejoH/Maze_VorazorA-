# Contexto del proyecto: Rutas en grilla

## Vision general

Este proyecto es una plataforma educativa e interactiva para visualizar algoritmos de busqueda de caminos sobre una grilla. Su objetivo es permitir que el usuario construya un escenario, ubique un punto de inicio A, un punto final B, agregue obstaculos y compare el comportamiento de dos algoritmos:

- Busqueda Voraz, tambien conocida como Greedy Best-First Search.
- A*, que combina el costo recorrido con una heuristica hacia el objetivo.

La aplicacion busca que la diferencia entre ambos algoritmos sea visible, medible y facil de entender. Por eso combina animacion paso a paso, estados visuales de celdas y metricas de resultado como cantidad de nodos visitados y pasos de la ruta final.

## Stack y versiones

El proyecto tiene dos superficies principales:

- Version web: construida con HTML, CSS moderno y JavaScript.
- Version desktop: construida con Python y Tkinter.

La version web vive en la raiz del proyecto:

- `index.html`: estructura de la interfaz.
- `styles.css`: sistema visual, layout, grilla y estados.
- `app.js`: estado de la aplicacion, edicion de grilla, algoritmos y animacion.

La version desktop vive en `desktop/`:

- `desktop/main.py`: interfaz Tkinter, controles, grilla y animacion.
- `desktop/pathfinding.py`: logica de busqueda reutilizable para la app desktop.
- `desktop/config.py`: constantes de grilla, etiquetas y colores.
- `desktop/README.md`: instrucciones de ejecucion y empaquetado.

Tambien existe una carpeta `dist/` con ejecutables generados y una carpeta `build/` con artefactos de PyInstaller.

## Modelo de grilla

La grilla usa una matriz de 17 filas por 25 columnas. Cada celda puede representar uno de varios estados:

- Celda vacia.
- Punto A, inicio de la busqueda.
- Punto B, destino.
- Obstaculo.
- Celda visitada durante la busqueda.
- Celda perteneciente a la ruta final.

En la version web, las celdas se generan como botones dentro de un contenedor CSS Grid. En la version desktop, se representan con widgets `tk.Label` organizados dentro de un frame con filas y columnas configuradas.

## Logica de algoritmos

Ambos algoritmos comparten la misma base:

- Se usa una lista abierta con nodos candidatos.
- Se usa un conjunto cerrado para evitar reprocesar celdas.
- Se almacena `cameFrom` para reconstruir la ruta final.
- La distancia heuristica es Manhattan: `abs(dx) + abs(dy)`.
- Los movimientos permitidos son ortogonales: arriba, abajo, izquierda y derecha.

La diferencia esta en la prioridad:

- Voraz: prioriza solo la heuristica `h`.
- A*: prioriza `g + h`, donde `g` es el costo recorrido y `h` es la heuristica.

Esto permite explicar visualmente que Voraz suele avanzar con mas decision hacia el objetivo, pero puede tomar decisiones menos optimas; A* explora con mas criterio de costo total y tiende a encontrar rutas optimas en este tipo de grilla no ponderada.

## Interaccion principal

El flujo de uso esta pensado asi:

1. Elegir algoritmo: Voraz o A*.
2. Seleccionar herramienta de edicion: Punto A, Punto B, Obstaculo o Borrar.
3. Editar la grilla con clic o arrastre.
4. Ejecutar la busqueda con "Buscar ruta".
5. Observar la animacion de visitados y ruta final.
6. Comparar metricas: visitados, pasos de ruta y algoritmo activo.

Cuando el usuario edita la grilla despues de una busqueda, el recorrido anterior se limpia para evitar lecturas ambiguas.

## Evolucion UX/UI

Durante el refinamiento se aplico una direccion visual tipo "Developer Tool", inspirada en productos como Vercel o Stripe: superficies limpias, jerarquia clara, componentes compactos y enfasis en datos.

### Jerarquia de acciones

Se separaron las acciones por importancia:

- "Buscar ruta" es la accion primaria, con color solido, mayor presencia y sombra.
- "Limpiar recorrido" y "Reiniciar todo" son acciones secundarias, con estilo outline o neutro.
- "Reiniciar todo" conserva un acento de peligro para indicar que puede borrar configuracion.

Esto reduce errores de clic y ayuda a que el usuario identifique rapidamente la accion principal.

### Estados activos

Las herramientas de edicion muestran un estado activo persistente. Esto es importante porque el usuario necesita saber que esta dibujando en la grilla: punto A, punto B, obstaculos o borrado.

En la version web, el estado activo usa fondo suave, borde y halo. En la version desktop, el control activo se representa mediante los radiobuttons de Tkinter.

### Estetica de la grilla

La grilla ocupa la mayor parte de la pantalla, por lo que su estetica define la experiencia. Se suavizaron las lineas internas para que funcionen como estructura de fondo y no compitan con la informacion importante.

En la version web:

- Las lineas se manejan con `gap: 1px` y un color gris muy suave.
- Las celdas interactivas tienen hover con iluminacion sutil.
- Obstaculos y puntos A/B tienen un pequeno `border-radius`.

Esto hace que los estados importantes, como ruta y obstaculos, destaquen mejor.

### Layout de dashboard

La interfaz se reorganizo como dashboard:

- Panel de control en una tarjeta diferenciada.
- Tablero principal en una superficie amplia.
- Separacion clara entre controles, resultados, leyenda y grilla.
- Padding aumentado en resultados y leyenda para mejorar lectura.

El objetivo fue pasar de una interfaz plana a una herramienta con superficies claras y una jerarquia mas profesional.

### Visualizacion comparativa de datos

La seccion de resultados se convirtio en una zona de metricas:

- "Visitados" y "Pasos de ruta" aparecen como tarjetas pequenas.
- El algoritmo activo aparece como chip.
- Voraz usa acento naranja.
- A* usa acento violeta.

El color sirve como codigo cognitivo: el usuario puede asociar rapidamente cada corrida con el algoritmo activo.

En la version web, el color se controla con `body[data-algorithm]` y variables CSS. En la version desktop, se actualizan colores de widgets Tkinter desde `update_algorithm_theme()`.

## Decisiones de implementacion

### Separacion entre estado y render

La version web mantiene un objeto `state` con el algoritmo activo, herramienta activa, puntos A/B, obstaculos, visitados y ruta. El render se deriva de ese estado mediante clases CSS.

Este enfoque hace que la grilla sea facil de recalcular y evita que el DOM sea la fuente principal de verdad.

### Render incremental

Al editar una celda, la app intenta actualizar solo las celdas afectadas cuando es posible. Si habia una busqueda previa, limpia el recorrido y vuelve a renderizar para evitar estados mezclados.

### Animacion educativa

La busqueda no se muestra de golpe. Primero se animan las celdas visitadas y luego la ruta final. Esto ayuda a entender el proceso, no solo el resultado.

### Accesibilidad basica

La version web usa botones para celdas y controles, `aria-live` en resultados y mensajes, y estados `focus-visible` para navegacion con teclado.

## Como ejecutar

### Version web

La version web puede abrirse directamente desde:

```powershell
.\index.html
```

Tambien puede servirse con cualquier servidor estatico local si se desea.

### Version desktop

Desde la raiz del proyecto:

```powershell
python .\desktop\main.py
```

### Ejecutable desktop

El ejecutable generado queda en:

```powershell
.\dist\RutasEnGrilla.exe
```

Para regenerarlo:

```powershell
python -m PyInstaller --noconfirm --clean --windowed --onefile --name RutasEnGrilla .\desktop\main.py
```

## Estado actual

La app cuenta con:

- Comparacion entre Voraz y A*.
- Edicion interactiva de grilla.
- Animacion de visitados y ruta.
- Metricas de resultado.
- Jerarquia visual de acciones.
- Layout tipo dashboard.
- Colores comparativos por algoritmo.
- Version web y version desktop funcional.

## Posibles mejoras futuras

- Agregar pesos de terreno para mostrar mejor la ventaja de A*.
- Permitir movimiento diagonal como opcion configurable.
- Agregar control de velocidad de animacion.
- Mostrar una tabla comparativa historica entre corridas.
- Agregar exportacion de escenarios.
- Agregar modo oscuro con variables CSS y tokens equivalentes en Tkinter.
- Mejorar accesibilidad con atajos de teclado para herramientas.
