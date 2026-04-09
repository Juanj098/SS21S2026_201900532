USE P1_201900532_ss2

-- =============================================
-- MODELO ESTRELLA - SGFood
-- =============================================

-- 1. DIMENSION FECHA
CREATE TABLE DimFecha (
    FechaId         INT PRIMARY KEY,
    Fecha           DATE NOT NULL,
    Dia             INT,
    Mes             INT,
    NombreMes       VARCHAR(20),
    Trimestre       INT,
    Anio            INT
);

-- 2. DIMENSION CLIENTE
CREATE TABLE DimCliente (
    ClienteId       VARCHAR(20) PRIMARY KEY,
    ClienteNombre   VARCHAR(100) NOT NULL,
    SegmentoCliente VARCHAR(50)
);

-- 3. DIMENSION PRODUCTO
CREATE TABLE DimProducto (
    ProductoId      INT IDENTITY(1,1) PRIMARY KEY,
    ProductoSKU     VARCHAR(50) NOT NULL,
    ProductoNombre  VARCHAR(150),
    Marca           VARCHAR(100),
    Categoria       VARCHAR(100),
    Subcategoria    VARCHAR(100),
    Fabricante      VARCHAR(100)
);

-- 4. DIMENSION LOCALIZACION
CREATE TABLE DimLocalizacion (
    LocalizacionId  INT IDENTITY(1,1) PRIMARY KEY,
    Departamento    VARCHAR(100),
    Municipio       VARCHAR(100)
);

-- 5. DIMENSION CANAL
CREATE TABLE DimCanal (
    CanalId         INT IDENTITY(1,1) PRIMARY KEY,
    CanalVenta      VARCHAR(50)
);

-- 6. TABLA DE HECHOS
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