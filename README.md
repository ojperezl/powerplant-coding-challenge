# ENGIE Challenge API

API desarrollada en FastAPI para optimizar la producción eléctrica calculando el plan óptimo de despacho de centrales eléctricas basado en costes marginales y restricciones técnicas.

## 🚀 Características

- **Optimización por orden de mérito**: Despacha centrales de menor a mayor coste marginal
- **Gestión de renovables**: Integra automáticamente la energía eólica según disponibilidad
- **Restricciones técnicas**: Respeta límites mínimos y máximos de cada central
- **Validación robusta**: Modelos Pydantic con validación automática de datos
- **API REST**: Endpoint único y bien documentado
- **Dockerizado**: Fácil despliegue con contenedores

## 📋 Requisitos

- Python 3.10+ (recomendado 3.11)
- Docker (opcional)

## 🛠️ Instalación y Uso

### Instalación local

```bash
# Clonar o navegar al directorio del proyecto
cd engie_challenge

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
uvicorn app.main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`

### Con Docker

#### Construcción de la imagen

```bash
# Construir imagen desde el directorio engie_challenge
docker build -t engie-challenge .

# Verificar que la imagen se construyó correctamente
docker images engie-challenge
```

#### Ejecución del contenedor

```bash
# Ejecutar contenedor básico
docker run -p 8000:8000 engie-challenge

# Ejecutar en modo detached (en segundo plano)
docker run -d -p 8000:8000 --name engie-api engie-challenge

# Ejecutar con variables de entorno personalizadas
docker run -p 8000:8000 -e PORT=8000 engie-challenge

# Ejecutar con volúmenes para desarrollo
docker run -p 8000:8000 -v $(pwd)/app:/app/app engie-challenge
```

#### Comandos útiles de Docker

```bash
# Ver logs del contenedor
docker logs engie-api

# Detener el contenedor
docker stop engie-api

# Eliminar el contenedor
docker rm engie-api

# Eliminar la imagen
docker rmi engie-challenge

# Ejecutar comandos dentro del contenedor
docker exec -it engie-api /bin/bash
```

#### Docker Compose (opcional)

Crea un archivo `docker-compose.yml` en el directorio raíz:

```yaml
version: "3.8"
services:
  engie-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
    restart: unless-stopped
```

Ejecutar con Docker Compose:

```bash
# Construir y ejecutar
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d

# Detener servicios
docker-compose down
```

## 📡 API Endpoints

### POST `/productionplan`

Calcula el plan óptimo de producción eléctrica.

**Request Body:**

```json
{
  "load": 480,
  "fuels": {
    "gas(euro/MWh)": 13.4,
    "kerosine(euro/MWh)": 50.8,
    "co2(euro/ton)": 20,
    "wind(%)": 60
  },
  "powerplants": [
    {
      "name": "gasfiredbig1",
      "type": "gasfired",
      "efficiency": 0.53,
      "pmin": 100,
      "pmax": 460
    },
    {
      "name": "windpark1",
      "type": "windturbine",
      "efficiency": 1,
      "pmin": 0,
      "pmax": 150
    }
  ]
}
```

**Response:**

```json
[
  { "name": "gasfiredbig1", "p": 230.0 },
  { "name": "windpark1", "p": 90.0 }
]
```

### GET `/`

Endpoint de salud que devuelve el estado de la API.

## 🔧 Algoritmo de Optimización

### 1. Cálculo de Costes Marginales

- **Gas**: `precio_gas / eficiencia`
- **Turbojet**: `precio_queroseno / eficiencia`
- **Eólica**: `0` (sin coste de combustible)

### 2. Orden de Mérito

Las centrales se ordenan de menor a mayor coste marginal.

### 3. Despacho

1. **Renovables**: Se despachan primero las eólicas según disponibilidad (`wind(%)`)
2. **Térmicas**: Se cubre la demanda restante siguiendo el orden de mérito
3. **Restricciones**: Se respetan `pmin` y `pmax` de cada central
4. **Ajuste final**: Se optimiza para alcanzar exactamente la carga solicitada

## 📁 Estructura del Proyecto

```
engie_challenge/
├── app/
│   ├── __init__.py
│   ├── main.py          # API FastAPI
│   ├── models.py        # Modelos Pydantic
│   └── logic.py         # Algoritmo de optimización
├── requirements.txt     # Dependencias Python
├── Dockerfile          # Imagen Docker
└── README.md           # Este archivo
```

## 🧪 Pruebas

### Ejemplo con cURL

```bash
curl -X POST "http://127.0.0.1:8000/productionplan" \
     -H "Content-Type: application/json" \
     -d '{
       "load": 480,
       "fuels": {
         "gas(euro/MWh)": 13.4,
         "kerosine(euro/MWh)": 50.8,
         "co2(euro/ton)": 20,
         "wind(%)": 60
       },
       "powerplants": [
         {
           "name": "gasfiredbig1",
           "type": "gasfired",
           "efficiency": 0.53,
           "pmin": 100,
           "pmax": 460
         },
         {
           "name": "windpark1",
           "type": "windturbine",
           "efficiency": 1,
           "pmin": 0,
           "pmax": 150
         }
       ]
     }'
```

### Documentación Interactiva

Visita `http://127.0.0.1:8000/docs` para acceder a la documentación automática de Swagger UI.

## 🔍 Validaciones

- **Carga**: Debe ser un número positivo
- **Combustibles**: Precios válidos para gas, queroseno, CO₂ y viento
- **Centrales**: Eficiencia > 0, pmin ≥ 0, pmax ≥ pmin
- **Tipos**: Solo acepta "gasfired", "turbojet", "windturbine"

## ⚠️ Limitaciones Actuales

- No incluye coste de CO₂ para centrales de gas (se puede añadir fácilmente)
- Algoritmo greedy simple (no optimización lineal completa)
- Sin gestión de rampas de potencia
- Sin consideración de reservas operativas

## 🚀 Mejoras Futuras

- [ ] Incluir costes de CO₂ en el cálculo
- [ ] Implementar optimización lineal (PuLP/CVXPY)
- [ ] Gestión de reservas primaria y secundaria
- [ ] Consideración de rampas de potencia
- [ ] Tests unitarios y de integración
- [ ] Logging y métricas de rendimiento
