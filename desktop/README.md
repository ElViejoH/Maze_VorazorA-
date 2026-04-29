# Aplicacion de escritorio

Esta version usa Python y Tkinter, por lo que no necesita instalar librerias externas.

## Ejecutar

Desde la carpeta raiz del proyecto:

```powershell
python .\desktop\main.py
```

## Ejecutar el .exe

El ejecutable generado queda en:

```powershell
.\dist\RutasEnGrilla.exe
```

Tambien puedes abrirlo con doble clic desde la carpeta `dist`.

## Generar nuevamente el .exe

Desde la carpeta raiz del proyecto:

```powershell
python -m PyInstaller --noconfirm --clean --windowed --onefile --name RutasEnGrilla .\desktop\main.py
```

## Funciones

- Seleccionar algoritmo Voraz o A*.
- Marcar punto A y punto B.
- Agregar y borrar obstaculos.
- Animar celdas visitadas y ruta final.
- Ver cantidad de visitados y pasos de la ruta.
