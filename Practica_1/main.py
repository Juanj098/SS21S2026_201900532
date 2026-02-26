import pandas as pd
import pyodbc

df = pd.read_csv('dataset_vuelos_crudo.csv')

df.dropna(subset=["passenger_nationality"],inplace=True)
df.dropna(subset=["seat"], inplace=True)
df = df.dropna(subset=["passenger_id"])
df["passenger_gender"] = df["passenger_gender"].replace({   
   "Masculino": "M",
   "masculino": "M",
   "m": "M",
   "M": "M",
   "Femenino": "F",
   "femenino": "F",
   "f": "F",
   "F": "F",
   "X": "X",
   "x": "X"
  })

median_passenger_age = df["passenger_age"].median()
df["passenger_age"] = df["passenger_age"].fillna(median_passenger_age)

median_sales_channel = df["sales_channel"].mode()[0]
df["sales_channel"] = df["sales_channel"].fillna(median_sales_channel)

df["ticket_price"] = df["ticket_price"].str.replace(",",".",regex=False)
df["ticket_price"] = pd.to_numeric(df["ticket_price"], errors="coerce")
df["ticket_price"] = df["ticket_price"].round(2)

df["arrival_datetime"] = pd.to_datetime(df["arrival_datetime"], format="mixed", dayfirst=True, errors="coerce")
df["departure_datetime"] = pd.to_datetime(df["departure_datetime"], format="mixed", dayfirst=True, errors="coerce")
df["booking_datetime"] = pd.to_datetime(df["booking_datetime"], format="mixed", dayfirst=True, errors="coerce")

df["airline_code"] = df["airline_code"].str.strip().str.upper()
df["airline_name"] = df["airline_name"].str.strip()
airline_unique = df[["airline_code", "airline_name"]].drop_duplicates(subset=['airline_code']) 

df["origin_airport"] = df["origin_airport"].str.strip().str.upper()
df["destination_airport"] = df["destination_airport"].str.strip().str.upper()
airport_unique = pd.concat([df["origin_airport"],df["destination_airport"]]).drop_duplicates().reset_index(drop=True)


print("--------------------")


try:
    connection = pyodbc.connect('DRIVER={SQL Server};SERVER=JGERAARDI;DATABASE=Practica1_semi2;Trusted_Connection=yes;')
    print("conexion exitosa!")
    cursor = connection.cursor()

    # 1. nombre de DB    
    cursor.execute("SELECT DB_NAME()")
    print("Base actual:", cursor.fetchone()[0])

    # 2. usuario
    cursor.execute("SELECT USER_NAME()")
    usuario = cursor.fetchone()[0]
    print(f"👤 Usuario actual: {usuario}")

    # 3. Verificar permisos (opcional)
    cursor.execute("SELECT IS_SRVROLEMEMBER('sysadmin')")
    is_admin = cursor.fetchone()[0]
    print(f"👑 Es administrador: {is_admin}")

      # 4. Buscar tablas (múltiples métodos)
    print("\n🔍 Buscando tablas...")
    
    # Método 1: INFORMATION_SCHEMA
    cursor.execute("""
    SELECT TABLE_SCHEMA, TABLE_NAME 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_TYPE = 'BASE TABLE'
    """)
    
    rows = cursor.fetchall()
    
    if rows:
        print(f"\n📊 Se encontraron {len(rows)} tablas:")
        for i, row in enumerate(rows, 1):
            print(f"  {i}.{row[1]}")
 
    cursor.execute("DELETE FROM equipaje")
    cursor.execute("DELETE FROM pagos")
    cursor.execute("DELETE FROM reservas")
    cursor.execute("DELETE FROM vuelos")
    cursor.execute("DELETE FROM pasajeros")
    cursor.execute("DELETE FROM aeropuertos")
    cursor.execute("DELETE FROM aerolineas")
    cursor.commit() 

    #  insertar pasajeros
    for _, r in df.iterrows():
        cursor.execute("""
            INSERT INTO pasajeros (genero, edad, nacionalidad) VALUES (?,?,?)
        """,
            r["passenger_gender"],
            int(r["passenger_age"]),
            r["passenger_nationality"]
        )

    # insertar aerolineas
    for _, row in airline_unique.iterrows():
        try:
            cursor.execute("""
                INSERT INTO aerolineas (codigo_aerolinea, nombre_aerolinea) 
                VALUES (?, ?)
            """, row["airline_code"], row["airline_name"])
        except Exception as ex:
            print(ex)

    for r in airport_unique:
        try:
            cursor.execute("""
                INSERT INTO aeropuertos (codigo_aeropuerto) VALUES (?)
            """,
            r)
        except Exception as ex:
            print(ex)

    cursor.commit()
    connection.close()


except Exception as ex:
    print(ex)