# 🍽️ Sistema de Gestión de Pedidos — Restaurante

Sistema digital de gestión de pedidos mediante tablets en mesa, que permite a los clientes seleccionar y personalizar sus productos de manera autónoma, optimizando el proceso de toma de pedidos y reduciendo tiempos de espera en el restaurante.

**Desarrollo de Software I — Universidad del Valle, Sede Tuluá (2025)**

---

## 👥 Integrantes

| Nombre | Rol |
|---|---|
| Juan Camilo Gil Agudelo | Product Owner / Developer (Backend) |
| Gabriel Esteban Burbano Mora | Scrum Master / Developer |
| Manuela Delgado Aguirre | Developer (Backend) |
| Paula Jimena Bohórquez | Developer (Frontend) |

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Frontend | React 18 + Vite |
| Backend | Python 3.11 + FastAPI |
| Base de datos | PostgreSQL 18 |
| ORM | SQLAlchemy |
| Contenerización | Docker + Docker Compose |
| Control de versiones | Git + GitHub |
| Metodología | Scrum + XP (Pair Programming) |

---

## 📁 Estructura del Proyecto

```
proyecto/
├── server-fastapi/           # Backend
│   ├── app/
│   │   ├── main.py           # Punto de entrada, registra los routers
│   │   ├── database.py       # Conexión a PostgreSQL
│   │   ├── models.py         # Modelos SQLAlchemy (tablas)
│   │   └── routers/
│   │       ├── menu.py           # GET menú por categorías
│   │       ├── pedidos.py        # Crear, confirmar y despachar pedidos
│   │       ├── facturas.py       # Generación y consulta de facturas
│   │       ├── estadisticas.py   # Ventas diarias, por producto y mensuales
│   │       └── usuarios.py       # Login y creación de usuarios (bcrypt)
│   ├── Dockerfile
│   └── requirements.txt
├── client-react/             # Frontend
│   ├── src/
│   └── package.json
├── data/                     # Datos de PostgreSQL (NO se sube a Git)
├── seed.sql                  # Datos iniciales compartidos
├── docker-compose.yml
└── README.md
```

---

## 🚀 Instalación y Ejecución

### Requisitos previos

- [Docker](https://www.docker.com/) y Docker Compose
- [Node.js](https://nodejs.org/) 18+ y npm

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd proyecto
```

### 2. Levantar el backend y la base de datos (Docker)

```bash
# Linux
sudo docker compose up -d --build

# Windows (con Docker Desktop abierto)
docker compose up -d --build
```

Esto levanta dos contenedores:
- **PostgreSQL** en el puerto `5432`
- **FastAPI** en el puerto `8000`

Verificar que están corriendo:

```bash
docker ps
```

### 3. Cargar los datos iniciales (seed)

```bash
# Linux
sudo docker exec -i Desarrollo psql -U postgres -d mi_base_local < seed.sql

# Windows
docker exec -i Desarrollo psql -U postgres -d mi_base_local < seed.sql
```

### 4. Levantar el frontend

```bash
cd client-react
npm install
npm run dev
```

### 5. Acceder a la aplicación

| Servicio | URL |
|---|---|
| Frontend | http://localhost:5173 |
| API Backend | http://localhost:8000 |
| Documentación interactiva (Swagger) | http://localhost:8000/docs |

---

## 🗄️ Base de Datos

Conexión desde herramientas externas (DataGrip, PgAdmin):

```
Host:     localhost
Port:     5432
Database: mi_base_local
User:     postgres
Password: postgres
```

> **Nota:** dentro de Docker el backend se conecta usando el host `db` (nombre del servicio). Desde tu máquina siempre se usa `localhost`.

### Modelo de datos

```
Mesa (1) ──── (1..*) Pedido
Usuario (1) ── (1..*) Pedido
Pedido (1) ─── (1..*) DetallePedido
DetallePedido (*) ── (1) Producto
Producto (*) ─── (1) Categoria
Pedido (1) ──── (1) Factura
```

---

## 🔌 Endpoints Principales

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/login` | Autenticación de empleados y administradores |
| POST | `/api/usuarios` | Crear usuario (contraseña hasheada con bcrypt) |
| GET | `/api/menu` | Menú completo organizado por categorías |
| POST | `/api/pedidos` | Crear pedido con productos y observaciones |
| GET | `/api/pedidos/{id}` | Detalle de un pedido |
| PUT | `/api/pedidos/{id}/confirmar` | Mesero confirma y envía a cocina |
| PUT | `/api/pedidos/{id}/despachar` | Cocina marca el pedido como listo |
| POST | `/api/facturas/{id_pedido}` | Generar factura de un pedido listo |
| GET | `/api/facturas/{id}` | Detalle de factura (sin observaciones) |
| GET | `/api/estadisticas/ventas-diarias` | Ventas del día |
| GET | `/api/estadisticas/ventas-producto` | Ranking de productos más vendidos |
| GET | `/api/estadisticas/ganancias-mes?mes=&anio=` | Ganancias de un mes |

La documentación completa e interactiva está disponible en `/docs` (Swagger UI).

---

## 🔄 Flujo del Sistema

```
Cliente (tablet)          Mesero               Cocina              Admin/Caja
     │                      │                    │                     │
     │ 1. Ve el menú        │                    │                     │
     │ 2. Personaliza       │                    │                     │
     │ 3. Confirma pedido ──► 4. Verifica        │                     │
     │                      │ 5. Envía a cocina ─► 6. Prepara          │
     │                      │                    │ 7. Despacha ────────► 8. Genera factura
     │                      │                    │                     │ 9. Consulta estadísticas
```

---

## 🧰 Comandos Útiles

```bash
# Ver logs del backend
docker logs server-fastapi

# Entrar a PostgreSQL
docker exec -it Desarrollo psql -U postgres -d mi_base_local

# Listar tablas
\dt

# Detener todo
docker compose down

# Reconstruir tras cambiar dependencias
docker compose up --build
```

---

## ⚠️ Notas para el Equipo

- La carpeta `data/` y `node_modules/` están en el `.gitignore` — **nunca se suben a Git**.
- Si clonas el proyecto en otra máquina, ejecuta `npm install` dentro de `client-react/` (los `node_modules` no son portables entre sistemas operativos).
- Si agregas una dependencia nueva en `requirements.txt`, reconstruye la imagen con `docker compose up --build`.
- Los datos de prueba compartidos se gestionan a través de `seed.sql`.
