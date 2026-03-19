Práctica 2 — Diseño de Dashboard y KPIs con Power BI

---
Descripción General
Esta práctica extiende el trabajo realizado en la Práctica 1, conectando Microsoft Power BI Desktop a la base de datos relacional `vuelos_dw` creada en SQL Server. El objetivo es construir un modelo tabular con relaciones, jerarquías y medidas DAX, y diseñar un dashboard interactivo con KPIs estratégicos que apoyen la toma de decisiones en el contexto de una aerolínea.
Los datos provienen de 10,000 registros de vuelos procesados mediante el proceso ETL de la Práctica 1, que incluyen información de aerolíneas, aeropuertos, pasajeros, tiempos de vuelo, precios y estados de vuelo.
---
Tecnologías Utilizadas
Herramienta	Versión	Uso
Microsoft Power BI Desktop	latest	Modelado tabular y dashboard
Microsoft SQL Server	2025	Fuente de datos
DAX (Data Analysis Expressions)	—	Medidas y KPIs
ODBC Driver 17	—	Conexión SQL Server ↔ Power BI
---
Configuración y Conexión a SQL Server
Requisitos previos
Power BI Desktop instalado
SQL Server 2025 corriendo con la base de datos `vuelos_dw` cargada (Práctica 1)
ODBC Driver 17 for SQL Server instalado
Pasos de conexión
Abrir Power BI Desktop
Ir a `Inicio → Obtener datos → SQL Server`
Configurar la conexión:
Campo	Valor
Servidor	`localhost`
Base de datos	`vuelos_dw`
Modo	Importar
Autenticación	Windows
Seleccionar todas las tablas del modelo:
`dim_aerolinea`, `dim_aeropuerto`, `dim_cabin_clase`
`dim_pasajero`, `dim_tiempo`, `fact_vuelo`
Click en Cargar

---
Modelo Tabular
Diagrama de Relaciones
![alt text](img/diseño%20estrella%20P2.png)
Relaciones configuradas



---
Medidas DAX
Se crearon 6 medidas DAX en la tabla `fact_vuelo` para calcular los indicadores del dashboard:
Medida 1 — Total de Vuelos
```dax
Total_Vuelos = COUNTROWS(fact_vuelo)
```
Descripción: Cuenta el total de registros en la tabla de hechos. Es la medida base para todos los análisis de volumen.
Resultado: 10,000 vuelos en el dataset completo.
Medida 2 — Ingresos Totales USD
```dax
Ingresos_Totales_USD = SUM(fact_vuelo[precio])
```
Descripción: Suma todos los precios de boletos en dólares estadounidenses (ya normalizados en el ETL de la Práctica 1).
Uso estratégico: Permite analizar la rentabilidad por aerolínea, ruta, temporada o clase de cabina.
Medida 3 — Promedio de Delay
```dax
Promedio_Delay_Min = AVERAGE(fact_vuelo[delay])
```
Descripción: Calcula el promedio de minutos de retraso por vuelo, incluyendo los vuelos sin retraso (delay = 0).
Uso estratégico: Indicador de calidad operativa. Un valor alto indica problemas de puntualidad sistemáticos.
Medida 4 — % Vuelos On Time
```dax
%_Vuelos_On_Time =
DIVIDE(
    COUNTROWS(FILTER(fact_vuelo, fact_vuelo[status] = "ON_TIME")),
    COUNTROWS(fact_vuelo),
    0
) * 100
```
Descripción: Calcula el porcentaje de vuelos que llegaron a tiempo sobre el total.
Resultado actual: 72.38% — por debajo de la meta del 80%.
Uso estratégico: Es el KPI principal de puntualidad operativa de la aerolínea.
Medida 5 — Ingreso Promedio por Vuelo
```dax
Ingreso_Promedio_Por_Vuelo =
DIVIDE([Ingresos_Totales_USD], [Total_Vuelos], 0)
```
Descripción: Calcula el precio promedio de boleto por vuelo dividiendo ingresos totales entre total de vuelos.
Uso estratégico: Permite identificar qué rutas, aerolíneas o clases generan mayor valor por vuelo.
Medida 6 — Meta de Puntualidad
```dax
Meta_Puntualidad = 80
```
Descripción: Define el valor objetivo (80%) para el KPI de puntualidad. Al ser una medida fija, puede modificarse fácilmente para ajustar la meta operativa.
Uso: Se usa como valor de referencia en el KPI con semáforo.
KPIs Implementados
KPI 1 — Puntualidad de Vuelos (con semáforo)
Parámetro	Valor
Valor actual	72.38%
Meta	80%
Diferencia	-9.52%
Estado	Por debajo de la meta
Configuración en Power BI:
Valor: `%_Vuelos_On_Time`
Eje de tendencia: `dim_tiempo[anio]`
Destino (meta): `Meta_Puntualidad`
Interpretación estratégica: Solo el 72.38% de los vuelos llegan a tiempo, lo que representa una brecha de casi 8 puntos porcentuales respecto a la meta operativa del 80%. Esto indica que aproximadamente 1 de cada 4 vuelos presenta algún tipo de irregularidad (retraso, cancelación o desvío), lo cual tiene impacto directo en la satisfacción del pasajero y los costos operativos.
Captura del KPI:
---
KPI 2 — Total de Vuelos (Tarjeta)
Parámetro	Valor
Medida	`Total_Vuelos`
Resultado	10,000 vuelos
Interpretación: Representa el volumen total de operaciones registradas en el período analizado.
---
KPI 3 — Ingresos Totales (Tarjeta)
Parámetro	Valor
Medida	`Ingresos_Totales_USD`
Resultado	Suma total en USD
Interpretación: Refleja el ingreso total generado por la venta de boletos en el período, normalizado a dólares estadounidenses.
---
KPI 4 — Promedio de Delay (Tarjeta)
Parámetro	Valor
Medida	`Promedio_Delay_Min`
Resultado	Minutos promedio
Interpretación: Indica el tiempo promedio de retraso por vuelo. Un valor superior a 15 minutos se considera crítico en la industria aérea.
---
Visualizaciones del Dashboard
Visualización 1 — KPI Puntualidad con Semáforo
Tipo: KPI visual
Medidas: `%_Vuelos_On_Time`, `Meta_Puntualidad`
Descripción: Muestra en rojo cuando la puntualidad no alcanza el 80% y en verde cuando lo supera.

---
Visualización 2 — Vuelos por Aerolínea
Tipo: Gráfico de barras agrupadas
Eje Y: `dim_aerolinea[airline_name]`
Eje X: `Total_Vuelos`
Leyenda: `fact_vuelo[status]`
Descripción: Muestra el volumen de vuelos por aerolínea desglosado por estado (ON_TIME, DELAYED, CANCELLED, DIVERTED). Permite identificar qué aerolíneas operan más y cuáles tienen mayor proporción de retrasos.
Visualización 3 — Ingresos por Período
Tipo: Gráfico de líneas
Eje X: `dim_tiempo[Jerarquía_Tiempo]`
Eje Y: `Ingresos_Totales_USD`
Descripción: Muestra la evolución temporal de los ingresos usando la jerarquía de tiempo (año → trimestre → mes → día). Permite identificar estacionalidad y tendencias de crecimiento o caída en ingresos.
---
Visualización 4 — Distribución por Clase de Cabina
Tipo: Gráfico de anillos (dona)
Leyenda: `dim_cabin_clase[cabin_clase]`
Valores: `Total_Vuelos`
Descripción: Muestra la proporción de vuelos por clase (ECONOMY, BUSINESS, FIRST, PREMIUM_ECONOMY). Permite analizar el perfil de los pasajeros y la distribución de la oferta de cabinas.

---
Visualización 5 — Top Destinos
Tipo: Gráfico de barras horizontales
Eje Y: `dim_aeropuerto[airport_code]`
Eje X: `Total_Vuelos`
Descripción: Muestra los aeropuertos de destino más frecuentes. Permite identificar las rutas más demandadas y enfocar estrategias de expansión o mejora operativa.
---
Visualización 6 — Tarjetas de Resumen
Tipo: Card (tarjeta)
Tarjeta 1: `Total_Vuelos` — volumen total de operaciones
Tarjeta 2: `Ingresos_Totales_USD` — ingresos totales en USD
Tarjeta 3: `Promedio_Delay_Min` — minutos promedio de retraso
---
Filtros y Segmentadores Interactivos
Segmentador	Campo	Tipo
Filtro por Año	`dim_tiempo[anio]`	Lista desplegable
Filtro por Aerolínea	`dim_aerolinea[airline_name]`	Lista múltiple
Funcionamiento: Al seleccionar un año o una aerolínea específica, todos los visuales del dashboard se actualizan simultáneamente, permitiendo análisis cruzados interactivos.

---
Interpretación de Resultados y Relevancia Estratégica
Hallazgo 1 — Problema de Puntualidad
El 72.38% de puntualidad está por debajo de la meta del 80%. Esto significa que casi 1 de cada 4 vuelos presenta irregularidades. Las aerolíneas con mayor cantidad de vuelos retrasados deberían ser priorizadas para revisión operativa.
Hallazgo 2 — Concentración de Ingresos
El gráfico de ingresos por período permite identificar los meses de mayor y menor facturación, lo cual es clave para planificar campañas de precios dinámicos y gestión de capacidad.
Hallazgo 3 — Perfil de Pasajeros
La distribución por clase de cabina revela la proporción de pasajeros de cada segmento. Una alta concentración en ECONOMY indica un mercado masivo, mientras que una mayor proporción de BUSINESS/FIRST sugiere un perfil de viajero corporativo.
Hallazgo 4 — Rutas Estratégicas
El top de destinos identifica los aeropuertos con mayor demanda, lo cual es fundamental para decisiones de asignación de flota, frecuencia de vuelos y negociación con aeropuertos.
---