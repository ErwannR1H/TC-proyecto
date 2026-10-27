# teoria-computacion
Curso teoria de computacion USIL 2026 - 02

Vercel : https://tc-proyecto.vercel.app

## Analizador de órdenes

La aplicación valida órdenes de compra en dos etapas: las expresiones regulares
reconocen cada lexema como un token y un analizador sintáctico Earley comprueba
si la secuencia completa puede derivarse de la gramática libre de contexto.

La gramática actual está definida en `app.py`:

```text
Orden -> ID_PRODUCTO CANTIDAD PRECIO FIN_ORDEN
```

El analizador Earley admite alternativas, recursión y producciones vacías. La
gramática se expresa como un diccionario de no terminales a listas de
producciones; los símbolos que no son claves del diccionario se interpretan
como terminales.

## Ejecución local

Necesitas tener Python 3 instalado. Desde la carpeta del proyecto, crea y
activa un entorno virtual:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

En Windows, activa el entorno con `.venv\Scripts\activate` en lugar del
comando `source`; si `python3` no está disponible, usa `python` para crear el
entorno virtual.

Instala las dependencias y arranca la aplicación:

```sh
python -m pip install -r requirements.txt
flask --app app run
```

Abre http://127.0.0.1:5000 en el navegador. Para detener la aplicación, pulsa
`Ctrl+C` en la terminal.

Para ejecutar las pruebas:

```sh
python -m unittest discover -s tests -v
```
