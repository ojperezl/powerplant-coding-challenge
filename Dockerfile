# Dockerfile

# ---- Etapa 1: Imagen base ----
# Usamos una imagen oficial y ligera de Python 3.9, coincidiendo con tu entorno de conda.
# La etiqueta '-slim' asegura que la imagen base sea lo más pequeña posible.
FROM python:3.9-slim

# ---- Etapa 2: Configuración del entorno ----
# Establecemos el directorio de trabajo dentro del contenedor.
WORKDIR /code

# ---- Etapa 3: Instalación de dependencias ----
# Copiamos primero el archivo de dependencias. Esto aprovecha el cache de Docker:
# si no cambias las dependencias, esta capa no se reconstruirá, acelerando los builds.
COPY ./requirements.txt /code/requirements.txt

# Instalamos las dependencias. '--no-cache-dir' evita guardar la caché de pip, reduciendo el tamaño de la imagen.
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# ---- Etapa 4: Copia del código de la aplicación ----
# Copiamos el código de nuestra aplicación al directorio de trabajo del contenedor.
COPY ./app /code/app

# ---- Etapa 5: Exposición del puerto y ejecución ----
# Le decimos a Docker que el contenedor escuchará en el puerto 8888.
EXPOSE 8888

# El comando que se ejecutará cuando el contenedor se inicie.
# Ejecuta el servidor Uvicorn y lo expone a todas las interfaces de red (0.0.0.0).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8888"]
