USE Practica1_semi2;

SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME

DROP TABLE Dim_Flight;

/*=================================
			Dim_Flight
=================================*/
CREATE TABLE Dim_Flight (
	flight_id INT IDENTITY(1,1) PRIMARY KEY,
	airline_code VARCHAR(15) NOT NULL,
	airline_name VARCHAR(255) NOT NULL,
	flight_number VARCHAR(25) NOT NULL,
	aircraft_type VARCHAR(56) NOT NULL,
	cabin_class VARCHAR(255) NOT NULL,
	seat VARCHAR(16) 
);

/*================================
			Dim_Route
================================*/
CREATE TABLE Dim_Route (
	route_id INT IDENTITY(1,1) PRIMARY KEY,
	origin_airport VARCHAR(64) NOT NULL,
	destination_airport VARCHAR(64) NOT NULL
);

/*================================
			Dim_Payment
================================*/
CREATE TABLE Dim_Payment (
	payment_id INT IDENTITY(1,1) PRIMARY KEY,
	sales_channel VARCHAR(64) NOT NULL,
	payment_method VARCHAR(255) NOT NULL,
	currency VARCHAR(15) NOT NULL
);

/*================================
			Dim_Date
================================*/
CREATE TABLE Dim_Date (
	date_id INT IDENTITY(1,1) PRIMARY KEY,
	full_date date NOT NULL,
	anio int NOT NULL,
	mes int NOT NULL,
	dia int NOT NULL
);

/*================================
			Dim_Passenger
================================*/
CREATE TABLE Dim_Passenger (
	passenger_id INT IDENTITY(1,1) PRIMARY KEY,
	passenger_gender VARCHAR(16) NOT NULL,
	passenger_age INT NOT NULL,
	passenger_nationality VARCHAR(255) NOT NULL
);

/*================================
			Fact_Reservas
================================*/
CREATE TABLE Fact_Reservas (
	Record_id INT PRIMARY KEY, 
	flight_id INT NOT NULL,
	route_id INT NOT NULL,
	payment_id

	CONSTRAINT FK_DimFlight
	FOREIGN KEY (flight_id)
	REFERENCES Dim_Flight(flight_id),

	CONSTRAINT FK_DimRoute
	FOREIGN KEY (route_id)
	REFERENCES Dim_Route(route_id),
);