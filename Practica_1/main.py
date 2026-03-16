import pandas as pd
import pyodbc


# ---------------------------------------------------------
# FASE 1: LIMPIEZA
# ---------------------------------------------------------
print("\n-- Fase 1: Limpieza de datos --")

df = pd.read_csv('dataset_vuelos_crudo.csv')
print(f"Registros cargados: {len(df)}")

df.dropna(subset=["passenger_nationality"], inplace=True)
df.dropna(subset=["seat"], inplace=True)
df = df.dropna(subset=["passenger_id"])
print(f"Registros tras limpiar nulos: {len(df)}")

df["passenger_gender"] = df["passenger_gender"].replace({
    "Masculino": "M", "masculino": "M", "m": "M", "M": "M",
    "Femenino":  "F", "femenino":  "F", "f": "F", "F": "F",
    "X": "X", "x": "X"
})

median_passenger_age = df["passenger_age"].median()
df["passenger_age"] = df["passenger_age"].fillna(median_passenger_age)

median_sales_channel = df["sales_channel"].mode()[0]
df["sales_channel"] = df["sales_channel"].fillna(median_sales_channel)

df["ticket_price"] = df["ticket_price"].str.replace(",", ".", regex=False)
df["ticket_price"] = pd.to_numeric(df["ticket_price"], errors="coerce")
df["ticket_price"] = df["ticket_price"].round(2)

df["arrival_datetime"]   = pd.to_datetime(df["arrival_datetime"],   format="mixed", dayfirst=True, errors="coerce")
df["departure_datetime"] = pd.to_datetime(df["departure_datetime"], format="mixed", dayfirst=True, errors="coerce")
df["booking_datetime"]   = pd.to_datetime(df["booking_datetime"],   format="mixed", dayfirst=True, errors="coerce")

df["airline_code"] = df["airline_code"].str.strip().str.upper()
df["airline_name"] = df["airline_name"].str.strip()
airline_unique = df[["airline_code", "airline_name"]].drop_duplicates(subset=["airline_code"])

df.dropna(subset=["origin_airport", "destination_airport"], inplace=True)
df["origin_airport"]      = df["origin_airport"].str.strip().str.upper()
df["destination_airport"] = df["destination_airport"].str.strip().str.upper()
airport_unique = pd.concat([df["origin_airport"], df["destination_airport"]]).drop_duplicates().reset_index(drop=True)

print("Limpieza completada.")


try:
    # ---------------------------------------------------------
    # FASE 2: CARGA
    # ---------------------------------------------------------
    print("\n-- Fase 2: Carga a base de datos --")

    connection = pyodbc.connect('DRIVER={SQL Server};SERVER=JGERAARDI;DATABASE=Practica1_semi2;Trusted_Connection=yes;')
    print("Conexion exitosa.")
    cursor = connection.cursor()

    cursor.execute("SELECT DB_NAME()")
    print("Base de datos:", cursor.fetchone()[0])

    cursor.execute("SELECT USER_NAME()")
    print("Usuario:", cursor.fetchone()[0])

    # Limpiar tablas
    for tabla in ["equipaje", "pagos", "reservas", "vuelos", "pasajeros", "aeropuertos", "aerolineas"]:
        cursor.execute(f"DELETE FROM {tabla}")
    cursor.commit()
    print("Tablas vaciadas.")

    # Pasajeros
    for _, r in df.iterrows():
        cursor.execute("""
            INSERT INTO pasajeros (id_pasajero, genero, edad, nacionalidad) VALUES (?,?,?,?)
        """, r["passenger_id"], r["passenger_gender"], int(r["passenger_age"]), r["passenger_nationality"])
    print(f"Pasajeros insertados: {len(df)}")

    # Aerolineas
    for _, row in airline_unique.iterrows():
        try:
            cursor.execute("""
                INSERT INTO aerolineas (codigo_aerolinea, nombre_aerolinea) VALUES (?, ?)
            """, row["airline_code"], row["airline_name"])
        except Exception as ex:
            print(ex)
    print(f"Aerolineas insertadas: {len(airline_unique)}")

    # Aeropuertos
    for r in airport_unique:
        try:
            cursor.execute("INSERT INTO aeropuertos (codigo_aeropuerto) VALUES (?)", r)
        except Exception as ex:
            print(ex)
    print(f"Aeropuertos insertados: {len(airport_unique)}")

    cursor.commit()

    cursor.execute("SELECT id_aeropuerto, codigo_aeropuerto FROM aeropuertos")
    aeropuerto_map = {row[1]: row[0] for row in cursor.fetchall()}

    cursor.execute("SELECT id_aerolinea, codigo_aerolinea FROM aerolineas")
    aerolinea_map = {row[1]: row[0] for row in cursor.fetchall()}

    # Vuelos
    vuelo_map = {}
    for _, r in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO vuelos (
                    id_registro, id_aerolinea, numero_vuelo,
                    id_aeropuerto_origen, id_aeropuerto_destino,
                    fecha_hora_salida, fecha_hora_llegada,
                    duracion_minutos, estado_vuelo, tipo_aeronave
                ) OUTPUT INSERTED.id_vuelo VALUES (?,?,?,?,?,?,?,?,?,?)
            """,
                r["record_id"],
                aerolinea_map.get(str(r["airline_code"]).strip().upper()),
                r["flight_number"],
                aeropuerto_map.get(str(r["origin_airport"]).strip().upper()),
                aeropuerto_map.get(str(r["destination_airport"]).strip().upper()),
                r["departure_datetime"], r["arrival_datetime"],
                int(r["duration_min"]), r["status"], r["aircraft_type"]
            )
            vuelo_map[int(r["record_id"])] = cursor.fetchone()[0]
        except Exception as ex:
            print(ex)
    cursor.commit()
    print(f"Vuelos insertados: {len(vuelo_map)}")

    # Reservas
    reserva_map = {}
    for _, r in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO reservas (
                    id_pasajero, id_vuelo, fecha_hora_reserva,
                    clase_cabina, asiento, canal_venta
                ) OUTPUT INSERTED.id_reserva VALUES (?,?,?,?,?,?)
            """,
                str(r["passenger_id"]),
                vuelo_map.get(int(r["record_id"])),
                r["booking_datetime"], r["cabin_class"],
                r["seat"], r["sales_channel"]
            )
            reserva_map[int(r["record_id"])] = cursor.fetchone()[0]
        except Exception as ex:
            print(ex)
    print(f"Reservas insertadas: {len(reserva_map)}")

    # Pagos
    for _, r in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO pagos (id_reserva, metodo_pago, precio_boleto, moneda, precio_estimado_usd)
                VALUES (?,?,?,?,?)
            """,
                reserva_map.get(int(r["record_id"])),
                r["payment_method"], r["ticket_price"],
                r["currency"], r["ticket_price_usd_est"]
            )
        except Exception as ex:
            print(ex)

    # Equipaje
    for _, r in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO equipaje (id_reserva, total_maletas, maletas_documentadas)
                VALUES (?, ?, ?)
            """,
                reserva_map.get(int(r["record_id"])),
                int(r["bags_total"])   if pd.notna(r["bags_total"])   else 0,
                int(r["bags_checked"]) if pd.notna(r["bags_checked"]) else 0
            )
        except Exception as ex:
            print(ex)

    cursor.commit()
    print("Pagos y equipaje insertados.")
    print("Carga completada.")


    # ---------------------------------------------------------
    # FASE 3: EXTRACCION DE INDICADORES
    # ---------------------------------------------------------
    print("\n-- Fase 3: Extraccion de indicadores --")

    print("\nDistribucion por Genero")
    cursor.execute("""
        SELECT genero, COUNT(*) AS total,
               ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS porcentaje
        FROM pasajeros
        GROUP BY genero
    """)
    rows = cursor.fetchall()
    print(f"  {'Genero':<15} {'Total':<10} {'Porcentaje'}")
    print("  " + "-"*35)
    for row in rows:
        print(f"  {str(row[0]):<15} {str(row[1]):<10} {str(row[2])}%")

    print("\nVuelos por Aerolinea")
    cursor.execute("""
        SELECT a.nombre_aerolinea, COUNT(v.id_vuelo) AS total_vuelos
        FROM aerolineas a
        JOIN vuelos v ON a.id_aerolinea = v.id_aerolinea
        GROUP BY a.nombre_aerolinea
        ORDER BY total_vuelos DESC
    """)
    rows = cursor.fetchall()
    print(f"  {'Aerolinea':<30} {'Total Vuelos'}")
    print("  " + "-"*45)
    for row in rows:
        print(f"  {str(row[0]):<30} {str(row[1])}")

    print("\nTop 10 Destinos mas frecuentes")
    cursor.execute("""
        SELECT TOP 10 ap.codigo_aeropuerto AS destino, COUNT(*) AS total_vuelos
        FROM vuelos v
        JOIN aeropuertos ap ON v.id_aeropuerto_destino = ap.id_aeropuerto
        GROUP BY ap.codigo_aeropuerto
        ORDER BY total_vuelos DESC
    """)
    rows = cursor.fetchall()
    print(f"  {'Destino':<15} {'Total Vuelos'}")
    print("  " + "-"*30)
    for i, row in enumerate(rows, 1):
        print(f"  {i}. {str(row[0]):<12} {str(row[1])}")

    print("\nTop 10 Rutas mas frecuentes")
    cursor.execute("""
        SELECT TOP 10
            ao.codigo_aeropuerto + ' -> ' + ad.codigo_aeropuerto AS ruta,
            COUNT(*) AS total_vuelos
        FROM vuelos v
        JOIN aeropuertos ao ON v.id_aeropuerto_origen  = ao.id_aeropuerto
        JOIN aeropuertos ad ON v.id_aeropuerto_destino = ad.id_aeropuerto
        GROUP BY ao.codigo_aeropuerto, ad.codigo_aeropuerto
        ORDER BY total_vuelos DESC
    """)
    rows = cursor.fetchall()
    print(f"  {'Ruta':<20} {'Total Vuelos'}")
    print("  " + "-"*35)
    for i, row in enumerate(rows, 1):
        print(f"  {i}. {str(row[0]):<18} {str(row[1])}")

    print("\nDuracion promedio de vuelo por aerolinea (min)")
    cursor.execute("""
        SELECT a.nombre_aerolinea,
               ROUND(AVG(CAST(v.duracion_minutos AS FLOAT)), 1) AS duracion_promedio_min,
               MIN(v.duracion_minutos) AS duracion_minima,
               MAX(v.duracion_minutos) AS duracion_maxima
        FROM vuelos v
        JOIN aerolineas a ON v.id_aerolinea = a.id_aerolinea
        GROUP BY a.nombre_aerolinea
        ORDER BY duracion_promedio_min DESC
    """)
    rows = cursor.fetchall()
    print(f"  {'Aerolinea':<30} {'Promedio':<12} {'Minimo':<10} {'Maximo'}")
    print("  " + "-"*60)
    for row in rows:
        print(f"  {str(row[0]):<30} {str(row[1]):<12} {str(row[2]):<10} {str(row[3])}")

    print("\nDistribucion por rango de edad")
    cursor.execute("""
        SELECT
            CASE
                WHEN edad < 18              THEN 'Menor de 18'
                WHEN edad BETWEEN 18 AND 30 THEN '18 - 30'
                WHEN edad BETWEEN 31 AND 45 THEN '31 - 45'
                WHEN edad BETWEEN 46 AND 60 THEN '46 - 60'
                ELSE 'Mayor de 60'
            END AS rango_edad,
            COUNT(*) AS total_pasajeros
        FROM pasajeros
        GROUP BY
            CASE
                WHEN edad < 18              THEN 'Menor de 18'
                WHEN edad BETWEEN 18 AND 30 THEN '18 - 30'
                WHEN edad BETWEEN 31 AND 45 THEN '31 - 45'
                WHEN edad BETWEEN 46 AND 60 THEN '46 - 60'
                ELSE 'Mayor de 60'
            END
        ORDER BY MIN(edad)
    """)
    rows = cursor.fetchall()
    print(f"  {'Rango':<15} {'Total'}")
    print("  " + "-"*28)
    for row in rows:
        print(f"  {str(row[0]):<15} {str(row[1])}")

    print("\nTop 10 nacionalidades")
    cursor.execute("""
        SELECT TOP 10 nacionalidad, COUNT(*) AS total_pasajeros
        FROM pasajeros
        GROUP BY nacionalidad
        ORDER BY total_pasajeros DESC
    """)
    rows = cursor.fetchall()
    print(f"  {'Nacionalidad':<25} {'Total'}")
    print("  " + "-"*38)
    for i, row in enumerate(rows, 1):
        print(f"  {i}. {str(row[0]):<23} {str(row[1])}")

    print("\nIngresos por aerolinea (USD)")
    cursor.execute("""
        SELECT a.nombre_aerolinea,
               COUNT(pg.id_pago)                     AS total_boletos,
               ROUND(SUM(pg.precio_estimado_usd), 2) AS ingreso_total_usd,
               ROUND(AVG(pg.precio_estimado_usd), 2) AS precio_promedio_usd,
               ROUND(MIN(pg.precio_estimado_usd), 2) AS precio_minimo_usd,
               ROUND(MAX(pg.precio_estimado_usd), 2) AS precio_maximo_usd
        FROM pagos pg
        JOIN reservas r   ON pg.id_reserva  = r.id_reserva
        JOIN vuelos v     ON r.id_vuelo     = v.id_vuelo
        JOIN aerolineas a ON v.id_aerolinea = a.id_aerolinea
        GROUP BY a.nombre_aerolinea
        ORDER BY ingreso_total_usd DESC
    """)
    rows = cursor.fetchall()
    print(f"  {'Aerolinea':<25} {'Boletos':<10} {'Total USD':<15} {'Promedio':<12} {'Minimo':<10} {'Maximo'}")
    print("  " + "-"*85)
    for row in rows:
        print(f"  {str(row[0]):<25} {str(row[1]):<10} {str(row[2]):<15} {str(row[3]):<12} {str(row[4]):<10} {str(row[5])}")

    print("\nProceso finalizado.")
    connection.close()

except Exception as ex:
    print(ex)