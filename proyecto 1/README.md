# Proyecto 1: Implementación del flujo completo de Microsoft con SSIS y SSAS en SQL Server

**Seminario de Sistemas 2 — Universidad San Carlos de Guatemala**  
**Facultad de Ingeniería — Ingeniería en Ciencias y Sistemas**  
**Carnet:** 201900532  
**Repositorio:** `SS22S2026_201900532`  
**Carpeta:** `Proyecto1/`

---

## Índice

1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Tecnologías Utilizadas](#tecnologías-utilizadas)
3. [Arquitectura de la Solución](#arquitectura-de-la-solución)
4. [Modelo Dimensional — Data Warehouse](#modelo-dimensional--data-warehouse)
5. [Estructura del Repositorio](#estructura-del-repositorio)
6. [Proceso ETL con SSIS](#proceso-etl-con-ssis)
7. [Modelo Analítico en SSAS](#modelo-analítico-en-ssas)
8. [Script DDL del Data Warehouse](#script-ddl-del-data-warehouse)
9. [Consultas de Validación y Analíticas](#consultas-de-validación-y-analíticas)
10. [Pasos de Implementación](#pasos-de-implementación)
11. [Resultados Obtenidos](#resultados-obtenidos)

---

## Descripción del Proyecto

Este proyecto implementa una solución completa de **Business Intelligence** para la empresa **SG-Food**, dedicada a la distribución y comercialización de productos de diversas marcas y categorías. El problema identificado es la lentitud en el procesamiento de consultas, la rigidez para generar reportes y la sobrecarga de la base de datos transaccional.

La solución consiste en tres componentes principales:

- **ETL con SSIS**: extracción desde múltiples fuentes heterogéneas, transformación y limpieza de datos, y carga al Data Warehouse.
- **Data Warehouse en SQL Server**: modelo dimensional en esquema estrella con tablas de hechos y dimensiones.
- **Modelo Analítico en SSAS**: cubo OLAP con dimensiones, jerarquías y medidas para análisis de ventas e inventarios.

---

## Tecnologías Utilizadas

| Herramienta | Uso |
|---|---|
| Microsoft SQL Server | Almacenamiento del Data Warehouse |
| SQL Server Integration Services (SSIS) | Desarrollo del proceso ETL |
| SQL Server Analysis Services (SSAS) | Modelo analítico multidimensional |
| Microsoft Visual Studio + SSDT | IDE de desarrollo para SSIS y SSAS |
| SQL Server Management Studio (SSMS) | Administración y consultas |
| GitHub | Control de versiones |

---

## Arquitectura de la Solución

```
┌─────────────────────────────────────────────────────────────┐
│                     FUENTES DE DATOS                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  BD OLTP     │  │  Archivos    │  │  BD Fabricantes  │  │
│  │ SGFood0LTP   │  │  .comp/.vent │  │  (Fabricante 2)  │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
└─────────┼─────────────────┼───────────────────┼────────────┘
          └─────────────────┼───────────────────┘
                            │
                    ┌───────▼────────┐
                    │   SSIS (ETL)   │
                    │ - Extracción   │
                    │ - Limpieza     │
                    │ - Transformac. │
                    │ - Carga        │
                    └───────┬────────┘
                            │
                    ┌───────▼────────────┐
                    │   DATA WAREHOUSE   │
                    │   (SQL Server)     │
                    │  Esquema Estrella  │
                    └───────┬────────────┘
                            │
                    ┌───────▼────────┐
                    │     SSAS       │
                    │  Cubo OLAP     │
                    │  Dimensiones   │
                    │  Jerarquías    │
                    │  Medidas       │
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │  Validación    │
                    │  SQL / MDX     │
                    └────────────────┘
```

---

## Modelo Dimensional — Data Warehouse

El Data Warehouse implementa un **esquema estrella** con la siguiente estructura:

### Diagrama

```
                    ┌─────────────┐
                    │  DimFecha   │
                    │─────────────│
                    │ FechaId (PK)│
                    │ Fecha       │
                    │ Dia         │
                    │ Mes         │
                    │ NombreMes   │
                    │ Trimestre   │
                    │ Anio        │
                    └──────┬──────┘
                           │
┌──────────────┐    ┌──────┴────────────┐    ┌───────────────┐
│  DimCliente  │    │    FactVentas     │    │  DimProducto  │
│──────────────│    │───────────────────│    │───────────────│
│ ClienteId(PK)├────┤ TransaccionId(PK) ├────┤ ProductoId(PK)│
│ ClienteNombre│    │ FechaId (FK)      │    │ ProductoSKU   │
│ Segmento     │    │ ClienteId (FK)    │    │ ProductoNombre│
└──────────────┘    │ ProductoId (FK)   │    │ Marca         │
                    │ LocalizacionId(FK)│    │ Categoria     │
┌──────────────┐    │ CanalId (FK)      │    │ Subcategoria  │
│  DimCanal    │    │ CantidadVendida   │    │ Fabricante    │
│──────────────│    │ InventarioInicial │    └───────────────┘
│ CanalId (PK) ├────┤ InventarioFinal   │
│ CanalVenta   │    │ PrecioUnitario    │    ┌───────────────────┐
└──────────────┘    │ CostoUnitario     │    │  DimLocalizacion  │
                    │ Descuento         ├────┤───────────────────│
                    │ ImporteNeto       │    │ LocalizacionId(PK)│
                    │ MargenEstimado    │    │ Departamento      │
                    └───────────────────┘    │ Municipio         │
                                             └───────────────────┘
```

### Justificación del Diseño

El esquema estrella fue elegido por su simplicidad de consulta, rendimiento en agregaciones y facilidad de integración con SSAS. Cada dimensión agrupa atributos descriptivos del negocio, mientras que la tabla de hechos centraliza las métricas numéricas de cada transacción de venta.

---

## Estructura del Repositorio

```
SS22S2026_201900532/
└── Proyecto1/
    ├── README.md                        # Este archivo
    ├── ssis/
    │   └── SGFood_ETL.sln               # Solución Visual Studio con paquetes SSIS
    ├── ssas/
    │   └── SGFood_Cubo.sln              # Proyecto SSAS con modelo analítico
    ├── sql/
    │   ├── 01_create_dw.sql             # DDL del Data Warehouse
    │   └── 02_validacion_consultas.sql  # Consultas de validación y análisis
    └── docs/
        └── modelo_estrella.png          # Diagrama del modelo dimensional
```

---

## Proceso ETL con SSIS

El proceso ETL se desarrolló en **SQL Server Integration Services (SSIS)** mediante Visual Studio con SQL Server Data Tools (SSDT).

### Fuentes de Datos

| Fuente | Tipo | Descripción |
|---|---|---|
| `SGFood0LTP` | Base de datos SQL Server | Tabla transaccional `dbo.TransaccionesVenta` |
| Archivos `.comp` | Texto delimitado por `\|` | Datos de fabricante 1 |
| Archivos `.vent` | Texto delimitado por `\|` | Datos de fabricante 2 |

### Fase 1 — Extracción

Se configuraron conexiones **OLE DB** para la base de datos OLTP y **Flat File Connections** para los archivos `.comp` y `.vent`. Cada fuente se conecta a su respectivo flujo de datos dentro del paquete SSIS.

### Fase 2 — Transformación

Las transformaciones aplicadas dentro del flujo de datos incluyen:

- **Data Conversion**: estandarización de tipos de datos entre fuentes heterogéneas.
- **Derived Column**: generación de columnas calculadas como componentes de fecha (día, mes, año, trimestre).
- **Lookup**: validación y cruce de llaves con las tablas de dimensiones ya cargadas.
- **Conditional Split**: separación de registros válidos e inválidos para manejo de errores.
- **Sort + Aggregate**: eliminación de duplicados en dimensiones.

### Fase 3 — Carga

La carga sigue el orden correcto para respetar las dependencias de llaves foráneas:

1. `DimFecha`
2. `DimCliente`
3. `DimProducto`
4. `DimLocalizacion`
5. `DimCanal`
6. `FactVentas`

Se utilizó la transformación **OLE DB Destination** con modo de carga por lotes para optimizar el rendimiento.

---

## Modelo Analítico en SSAS

El modelo analítico fue implementado en **SQL Server Analysis Services (SSAS)** en modo multidimensional, conectado directamente al Data Warehouse.

### Dimensiones Implementadas

| Dimensión | Atributos Clave | Jerarquías |
|---|---|---|
| DimFecha | Fecha, Día, Mes, Trimestre, Año | Año > Trimestre > Mes > Día |
| DimCliente | ClienteId, ClienteNombre, Segmento | Segmento > Cliente |
| DimProducto | SKU, Nombre, Marca, Categoría, Subcategoría | Categoría > Subcategoría > Producto |
| DimLocalizacion | Departamento, Municipio | Departamento > Municipio |
| DimCanal | CanalVenta | — |

### Medidas del Cubo

| Medida | Agregación | Descripción |
|---|---|---|
| Cantidad Vendida | SUM | Total de unidades vendidas |
| Importe Neto | SUM | Valor total de ventas |
| Costo Total | SUM | Costo total de los productos |
| Margen Estimado | SUM | Ganancia estimada |
| Descuento Total | SUM | Total de descuentos aplicados |
| Número de Transacciones | COUNT | Conteo de registros de venta |
| Precio Unitario Promedio | AVG | Precio promedio por unidad |

### Procesamiento del Modelo

El modelo se procesa mediante **Process Full** en SSAS para la carga inicial, y **Process Update** para cargas incrementales posteriores.

---

## Script DDL del Data Warehouse

El archivo `sql/01_create_dw.sql` contiene las sentencias de creación en el siguiente orden:

```sql
-- 1. DimFecha
CREATE TABLE DimFecha (
    FechaId     INT PRIMARY KEY,
    Fecha       DATE NOT NULL,
    Dia         INT,
    Mes         INT,
    NombreMes   VARCHAR(20),
    Trimestre   INT,
    Anio        INT
);

-- 2. DimCliente
CREATE TABLE DimCliente (
    ClienteId       VARCHAR(20) PRIMARY KEY,
    ClienteNombre   VARCHAR(100),
    SegmentoCliente VARCHAR(50)
);

-- 3. DimProducto
CREATE TABLE DimProducto (
    ProductoId      INT IDENTITY(1,1) PRIMARY KEY,
    ProductoSKU     VARCHAR(50),
    ProductoNombre  VARCHAR(150),
    Marca           VARCHAR(100),
    Categoria       VARCHAR(100),
    Subcategoria    VARCHAR(100),
    Fabricante      VARCHAR(100)
);

-- 4. DimLocalizacion
CREATE TABLE DimLocalizacion (
    LocalizacionId  INT IDENTITY(1,1) PRIMARY KEY,
    Departamento    VARCHAR(100),
    Municipio       VARCHAR(100)
);

-- 5. DimCanal
CREATE TABLE DimCanal (
    CanalId     INT IDENTITY(1,1) PRIMARY KEY,
    CanalVenta  VARCHAR(50)
);

-- 6. FactVentas
CREATE TABLE FactVentas (
    TransaccionId       INT IDENTITY(1,1) PRIMARY KEY,
    FechaId             INT FOREIGN KEY REFERENCES DimFecha(FechaId),
    ClienteId           VARCHAR(20) FOREIGN KEY REFERENCES DimCliente(ClienteId),
    ProductoId          INT FOREIGN KEY REFERENCES DimProducto(ProductoId),
    LocalizacionId      INT FOREIGN KEY REFERENCES DimLocalizacion(LocalizacionId),
    CanalId             INT FOREIGN KEY REFERENCES DimCanal(CanalId),
    CantidadVendida     INT,
    InventarioInicial   INT,
    InventarioFinal     INT,
    PrecioUnitario      DECIMAL(10,2),
    CostoUnitario       DECIMAL(10,2),
    Descuento           DECIMAL(10,2),
    ImporteNeto         DECIMAL(10,2),
    MargenEstimado      DECIMAL(10,2)
);
```

---

## Consultas de Validación y Analíticas

### Validación de Carga

```sql
-- Conteo de registros por tabla
SELECT 'FactVentas'       AS Tabla, COUNT(*) AS Total FROM FactVentas
UNION ALL
SELECT 'DimCliente',      COUNT(*) FROM DimCliente
UNION ALL
SELECT 'DimProducto',     COUNT(*) FROM DimProducto
UNION ALL
SELECT 'DimFecha',        COUNT(*) FROM DimFecha
UNION ALL
SELECT 'DimLocalizacion', COUNT(*) FROM DimLocalizacion
UNION ALL
SELECT 'DimCanal',        COUNT(*) FROM DimCanal;
```

### Consultas Analíticas

```sql
-- Ventas totales por mes y año
SELECT f.Anio, f.NombreMes, SUM(v.ImporteNeto) AS TotalVentas
FROM FactVentas v
JOIN DimFecha f ON v.FechaId = f.FechaId
GROUP BY f.Anio, f.NombreMes, f.Mes
ORDER BY f.Anio, f.Mes;

-- Top 5 productos más vendidos
SELECT TOP 5 p.ProductoNombre, SUM(v.CantidadVendida) AS TotalUnidades
FROM FactVentas v
JOIN DimProducto p ON v.ProductoId = p.ProductoId
GROUP BY p.ProductoNombre
ORDER BY TotalUnidades DESC;

-- Ventas por departamento
SELECT l.Departamento, SUM(v.ImporteNeto) AS TotalVentas
FROM FactVentas v
JOIN DimLocalizacion l ON v.LocalizacionId = l.LocalizacionId
GROUP BY l.Departamento
ORDER BY TotalVentas DESC;

-- Margen por categoría de producto
SELECT p.Categoria,
       SUM(v.ImporteNeto)    AS TotalVentas,
       SUM(v.MargenEstimado) AS TotalMargen,
       ROUND(SUM(v.MargenEstimado) / NULLIF(SUM(v.ImporteNeto), 0) * 100, 2) AS PctMargen
FROM FactVentas v
JOIN DimProducto p ON v.ProductoId = p.ProductoId
GROUP BY p.Categoria
ORDER BY TotalMargen DESC;

-- Ventas por canal
SELECT c.CanalVenta, COUNT(*) AS NumTransacciones, SUM(v.ImporteNeto) AS TotalVentas
FROM FactVentas v
JOIN DimCanal c ON v.CanalId = c.CanalId
GROUP BY c.CanalVenta
ORDER BY TotalVentas DESC;
```

---

## Pasos de Implementación

### Prerrequisitos

- Microsoft SQL Server instalado y en ejecución
- Visual Studio con extensión **SQL Server Data Tools (SSDT)**
- Acceso al servidor de datos `34.63.26.98,1433` con las credenciales provistas

### Paso 1 — Crear el Data Warehouse

1. Abrir SSMS y conectarse al servidor local
2. Ejecutar el script `sql/01_create_dw.sql` para crear todas las tablas

### Paso 2 — Ejecutar el proceso ETL (SSIS)

1. Abrir la solución `ssis/SGFood_ETL.sln` en Visual Studio
2. Configurar los **Connection Managers** con las rutas correctas a las fuentes
3. Ejecutar el paquete en modo **Debug** para verificar el flujo
4. Confirmar que todos los componentes finalizan sin errores (flechas verdes)

### Paso 3 — Implementar y procesar el modelo SSAS

1. Abrir la solución `ssas/SGFood_Cubo.sln` en Visual Studio
2. Verificar la conexión al Data Warehouse
3. Desplegar el proyecto: **Build > Deploy**
4. Procesar el cubo: clic derecho en el cubo > **Process > Process Full**

### Paso 4 — Validar resultados

1. Ejecutar las consultas de `sql/02_validacion_consultas.sql` en SSMS
2. Explorar el cubo desde la pestaña **Browser** en SSAS
3. *(Opcional)* Conectar Excel o Power BI al cubo para visualización ejecutiva

---

## Resultados Obtenidos

| Indicador | Valor |
|---|---|
| Total registros cargados en FactVentas | 1,000 |
| Clientes únicos en DimCliente | 10 |
| Productos únicos en DimProducto | 12 |
| Departamentos en DimLocalizacion | 5 (Guatemala, Sacatepéquez, Quetzaltenango, Alta Verapaz, Escuintla) |
| Canales de venta en DimCanal | 4 (Mayorista, Minorista, Institucional, Ecommerce) |
| Rango de fechas cargado | 03/12/2025 — 01/04/2026 |
| Total de ventas (ImporteNeto) | Q109,749.60 |
| Modelo SSAS procesado exitosamente | Sí |

---

*Proyecto 1 — Seminario de Sistemas 2 — Semestre 2026-1*