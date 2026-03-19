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

    # limpiar tablas
#   for tabla in ["equipaje", "pagos", "reservas", "vuelos", "pasajeros", "aeropuertos", "aerolineas"]:
#       cursor.execute(f"DELETE FROM {tabla}")
#   cursor.commit()

    # eliminar tablas
#    for tabla in ["equipaje", "pagos", "reservas", "vuelos", "pasajeros", "aeropuertos", "aerolineas"]:
#        cursor.execute(f"DROP TABLE {tabla}")
#   cursor.commit()

    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME")
    tablas = cursor.fetchall()
    if tablas:
        print("** Tablas Encontradas **")
        for tabla in tablas:
            print(f"~ {tabla[0]}")
    else:
        print("no hay tablas para mostrar")

except Exception as ex:
    print(ex)