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
    "X": "X", "x": "X",
    "NoBinario": "NB", "nobinario": "NB", "nb": "NB", "NB": "NB"
})

print(df["passenger_gender"].value_counts())

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
#airport_unique = pd.concat([df["origin_airport"], df["destination_airport"]]).drop_duplicates().reset_index(drop=True)

print("Limpieza completada.")

# ---------------------------------------------------------
# FASE 2: CARGA
# ---------------------------------------------------------
try:
    print("\n -- Fase 2: Carga a base de datos --")
    connection = pyodbc.connect('DRIVER={SQL Server};SERVER=JGERAARDI;DATABASE=Practica1_semi2;Trusted_Connection=yes;')
    print("Conexion exitosa")
    cursor = connection.cursor()

    cursor.execute("SELECT DB_NAME()")
    print(f"Base de datos {cursor.fetchone()[0]}")

    cursor.execute("SELECT USER_NAME()")
    print(f"Usuario: {cursor.fetchone()[0]}")

    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME")
    tablas = cursor.fetchall()
    if tablas:
        print("** Tablas Encontradas **")
        for tabla in tablas:
            print(f"~ {tabla[0]}")
    else:
        print("no hay tablas para mostrar")
    


    # --------------------------------------------------
    # Limpiar tablas en orden (primero hechos, luego dims)
    # --------------------------------------------------
    print("Limpiando tablas existentes...")
    for tabla in ["Fact_Reservas", "Dim_Flight", "Dim_Route", "Dim_Payment", "Dim_Date", "Dim_Passenger"]:
        cursor.execute(f"DELETE FROM {tabla}")
    connection.commit()
    print("Tablas limpias.\n")
 
    # --------------------------------------------------
    # DIM_PASSENGER  (usa el UUID del CSV como PK directamente)
    # --------------------------------------------------
    print("Cargando Dim_Passenger...")
    dim_passenger = (
        df[["passenger_id", "passenger_gender", "passenger_age", "passenger_nationality"]]
        .drop_duplicates(subset=["passenger_id"])
        .reset_index(drop=True)
    )
    for _, row in dim_passenger.iterrows():
        cursor.execute("""
            INSERT INTO Dim_Passenger (passenger_id, passenger_gender, passenger_age, passenger_nationality)
            VALUES (?, ?, ?, ?)
        """, row["passenger_id"], row["passenger_gender"],
             int(row["passenger_age"]), row["passenger_nationality"])
 
    connection.commit()
    print(f"  -> {len(dim_passenger)} registros insertados en Dim_Passenger")
 
    # --------------------------------------------------
    # DIM_FLIGHT
    # --------------------------------------------------
    print("Cargando Dim_Flight...")
    dim_flight = (
        df[["airline_code", "airline_name", "flight_number", "aircraft_type", "cabin_class", "seat"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    flight_map = {}  # (airline_code, flight_number, cabin_class, seat) -> flight_id
    for _, row in dim_flight.iterrows():
        cursor.execute("""
            INSERT INTO Dim_Flight (airline_code, airline_name, flight_number, aircraft_type, cabin_class, seat)
            OUTPUT INSERTED.flight_id
            VALUES (?, ?, ?, ?, ?, ?)
        """, row["airline_code"], row["airline_name"], row["flight_number"],
             row["aircraft_type"], row["cabin_class"], row["seat"])
        fid = cursor.fetchone()[0]
        flight_map[(row["airline_code"], row["flight_number"], row["cabin_class"], row["seat"])] = fid
 
    connection.commit()
    print(f"  -> {len(flight_map)} registros insertados en Dim_Flight")
 
    # --------------------------------------------------
    # DIM_ROUTE
    # --------------------------------------------------
    print("Cargando Dim_Route...")
    dim_route = (
        df[["origin_airport", "destination_airport"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    route_map = {}  # (origin, destination) -> route_id
    for _, row in dim_route.iterrows():
        cursor.execute("""
            INSERT INTO Dim_Route (origin_airport, destination_airport)
            OUTPUT INSERTED.route_id
            VALUES (?, ?)
        """, row["origin_airport"], row["destination_airport"])
        rid = cursor.fetchone()[0]
        route_map[(row["origin_airport"], row["destination_airport"])] = rid
 
    connection.commit()
    print(f"  -> {len(route_map)} registros insertados en Dim_Route")
 
    # --------------------------------------------------
    # DIM_PAYMENT
    # --------------------------------------------------
    print("Cargando Dim_Payment...")
    dim_payment = (
        df[["sales_channel", "payment_method", "currency"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    payment_map = {}  # (sales_channel, payment_method, currency) -> payment_id
    for _, row in dim_payment.iterrows():
        cursor.execute("""
            INSERT INTO Dim_Payment (sales_channel, payment_method, currency)
            OUTPUT INSERTED.payment_id
            VALUES (?, ?, ?)
        """, row["sales_channel"], row["payment_method"], row["currency"])
        pid = cursor.fetchone()[0]
        payment_map[(row["sales_channel"], row["payment_method"], row["currency"])] = pid
 
    connection.commit()
    print(f"  -> {len(payment_map)} registros insertados en Dim_Payment")
 
    # --------------------------------------------------
    # DIM_DATE  (fechas únicas de las 3 columnas de fecha)
    # --------------------------------------------------
    print("Cargando Dim_Date...")
    fechas = set()
    for col in ["booking_datetime", "departure_datetime", "arrival_datetime"]:
        fechas.update(df[col].dropna().dt.date)

    date_map = {}
    for fecha in sorted(fechas):
        cursor.execute("""
            INSERT INTO Dim_Date (full_date, anio, mes, dia)
            OUTPUT INSERTED.date_id
            VALUES (?, ?, ?, ?)
        """, 
            str(fecha),          # <-- convertir a string "YYYY-MM-DD"
            int(fecha.year), 
            int(fecha.month), 
            int(fecha.day)
        )
        did = cursor.fetchone()[0]
        date_map[fecha] = did

    connection.commit()
    print(f"  -> {len(date_map)} registros insertados en Dim_Date")
    # --------------------------------------------------
    # FACT_RESERVAS
    # --------------------------------------------------
    print("Cargando Fact_Reservas...")
    insertados = 0
    errores    = 0
 
    for _, row in df.iterrows():
        try:
            fk_flight = flight_map[(
                row["airline_code"], row["flight_number"],
                row["cabin_class"],  row["seat"]
            )]
            fk_route   = route_map[(row["origin_airport"], row["destination_airport"])]
            fk_payment = payment_map[(row["sales_channel"], row["payment_method"], row["currency"])]
 
            booking_date   = row["booking_datetime"].date()   if pd.notna(row["booking_datetime"])   else None
            departure_date = row["departure_datetime"].date() if pd.notna(row["departure_datetime"]) else None
            arrival_date   = row["arrival_datetime"].date()   if pd.notna(row["arrival_datetime"])   else None
 
            fk_booking   = date_map.get(booking_date)
            fk_departure = date_map.get(departure_date)
            fk_arrival   = date_map.get(arrival_date)   # puede ser None si no hay arrival
 
            cursor.execute("""
                INSERT INTO Fact_Reservas (
                    Record_id, flight_id, route_id, payment_id, passenger_id,
                    booking_date_id, departure_date_id, arrival_date_id,
                    ticket_price_usd_est, ticket_price,
                    total_bags, bags_checked, delay_min, duration_min
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                int(row["record_id"]),
                fk_flight,
                fk_route,
                fk_payment,
                row["passenger_id"],
                fk_booking,
                fk_departure,
                fk_arrival,                  # NULL si el vuelo no tiene llegada (ej. CANCELLED)
                float(row["ticket_price_usd_est"]) if pd.notna(row["ticket_price_usd_est"]) else 0.0,
                float(row["ticket_price"])         if pd.notna(row["ticket_price"])         else 0.0,
                int(row["bags_total"]),
                int(row["bags_checked"]),
                int(row["delay_min"]),
                int(row["duration_min"])
            )
            insertados += 1
 
        except Exception as e:
            errores += 1
            print(f"  [!] Error en record_id={row.get('record_id', '?')}: {e}")
 
    connection.commit()
    print(f"  -> {insertados} registros insertados en Fact_Reservas ({errores} errores)")
    print("\n✓ Carga dimensional completada exitosamente.")

except Exception as ex:
    print(ex)