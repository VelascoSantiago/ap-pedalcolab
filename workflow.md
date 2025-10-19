# PedalColab Workflow
Este documento describe el flujo de trabajo y la interacción entre los dos roles principales del proyecto: el Productor (en la computadora) y el Músico (en el celular).

---

## Visión General
El proyecto es un sistema de producción musical que permite a un músico grabar y subir pistas de audio desde su celular. Un productor, desde una computadora en la misma red, puede acceder a estas pistas, aplicarles efectos de audio profesionales a través de una interfaz de DAW y devolver las pistas procesadas para que el músico las escuche y descargue.

---

## Diagrama de Flujo

por agregar...

---

## Paso a Paso del Flujo de Trabajo
1. Inicio de la Aplicación (Productor)
El productor inicia la aplicación ejecutando el lanzador gráfico (launcher_pretty.py). Este no requiere conocimientos técnicos ni usar la terminal.

Aparece una ventana profesional con el logo del proyecto, una breve descripción, el autor y el nombre de la competencia.

Al hacer clic en el botón "Launch":

El servidor web (Flask) se inicia en segundo plano.

Se abre automáticamente una pestaña en el navegador web del productor, mostrando la interfaz de la DAW (http://127.0.0.1:5000).

2. El Músico se Conecta y Sube una Pista
El músico, conectado a la misma red WiFi que el productor, abre el navegador en su celular.

Ingresa la dirección IP del productor seguida del puerto y la ruta /mobile (ej. http://192.168.1.100:5000/mobile).

Se muestra la interfaz del cliente móvil, una página sencilla diseñada para:

Subir un archivo de audio: El músico selecciona una grabación de su celular y la envía. El servidor la guarda en la carpeta audio_raw.

Ver pistas procesadas: Inicialmente, esta sección está vacía.

3. El Productor Procesa el Audio
En la interfaz de la DAW en su computadora, el productor ve que la nueva pista aparece automáticamente en la lista de "Pistas Crudas".

El productor hace clic en la pista que desea procesar. La pista se carga en el "pedal de efectos".

Ajusta los sliders de los diferentes efectos (Distorsión, Reverb, Chorus, etc.) a su gusto.

Presiona el botón `Procesar Pista`.

El servidor toma el archivo de audio_raw, le aplica los efectos seleccionados usando el motor de audio (daw_app.py) y guarda el resultado en la carpeta audio_fx.

La pista recién procesada aparece en la lista de "Pistas Procesadas (FX)" en la interfaz de la DAW, lista para ser escuchada.

4. El Músico Recibe la Pista Final
En la interfaz del cliente móvil, la página se actualiza automáticamente cada pocos segundos.

La nueva pista procesada aparece en la lista de "Pistas Procesadas".

El músico ahora puede:

Reproducir la pista directamente en su celular para escuchar el resultado.

Descargar el archivo de audio procesado a su dispositivo.

---

Este ciclo completa el flujo de trabajo colaborativo, permitiendo una interacción fluida y casi en tiempo real entre el músico y el productor.