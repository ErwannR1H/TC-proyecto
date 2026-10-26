# teoria-computacion
Curso teoria de computacion USIL 2026 - 02

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

Para ejecutar las pruebas:

```sh
python -m unittest discover -s tests -v
```
