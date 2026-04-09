USE Practica1_semi2;

SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME

/*DROP TABLE Dim_Flight;*/

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
	passenger_id VARCHAR(255) PRIMARY KEY,
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
	payment_id INT NOT NULL,
	passenger_id VARCHAR(255),
	booking_date_id INT NOT NULL,
	departure_date_id INT NOT NULL,
	arrival_date_id INT NOT NULL,
	ticket_price_usd_est FLOAT NOT NULL,
	ticket_price FLOAT NOT NULL,
	total_bags INT NOT NULL,
	bags_checked INT NOT NULL,
	delay_min INT NOT NULL,
	duration_min INT NOT NULL,

	CONSTRAINT FK_DimFlight
	FOREIGN KEY (flight_id)
	REFERENCES Dim_Flight(flight_id),

	CONSTRAINT FK_DimRoute
	FOREIGN KEY (route_id)
	REFERENCES Dim_Route(route_id),

	CONSTRAINT FK_DimPayment
	FOREIGN KEY (payment_id)
	REFERENCES Dim_Payment(payment_id),

	CONSTRAINT FK_DimPassenger
	FOREIGN KEY (passenger_id)
	REFERENCES Dim_Passenger(passenger_id),

	CONSTRAINT FK_DimDate_Booking
    FOREIGN KEY (booking_date_id)    
	REFERENCES Dim_Date(date_id),

	CONSTRAINT FK_DimDate_Departure
    FOREIGN KEY (departure_date_id)  
	REFERENCES Dim_Date(date_id),

	CONSTRAINT FK_DimDate_Arrival
    FOREIGN KEY (arrival_date_id)    
	REFERENCES Dim_Date(date_id)
);

SELECT * FROM Fact_Reservas;
SELECT * FROM Dim_Flight;