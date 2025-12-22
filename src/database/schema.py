from .connection import DatabaseConnection


class SchemaManager:
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def create_all_tables(self):
        self._create_dim_date()
        self._create_dim_station()
        self._create_dim_prize()
        self._create_dim_agency()
        self._create_fact_lottery_result()
        self._create_fact_revenue()
    
    def _create_dim_date(self):
        query = """
        CREATE TABLE IF NOT EXISTS Dim_Date (
            date_id INTEGER PRIMARY KEY,
            full_date DATE NOT NULL UNIQUE,
            day INTEGER NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            quarter INTEGER NOT NULL,
            day_of_week TEXT NOT NULL,
            is_weekend INTEGER NOT NULL,
            is_month_start INTEGER NOT NULL,
            is_month_end INTEGER NOT NULL
        )
        """
        self.db.execute(query)
    
    def _create_dim_station(self):
        query = """
        CREATE TABLE IF NOT EXISTS Dim_Station (
            station_id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_name TEXT NOT NULL UNIQUE,
            region TEXT NOT NULL
        )
        """
        self.db.execute(query)
    
    def _create_dim_prize(self):
        query = """
        CREATE TABLE IF NOT EXISTS Dim_Prize (
            prize_id INTEGER PRIMARY KEY AUTOINCREMENT,
            prize_name TEXT NOT NULL UNIQUE,
            prize_order INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            digits INTEGER NOT NULL,
            prize_value REAL NOT NULL
        )
        """
        self.db.execute(query)
    
    def _create_dim_agency(self):
        query = """
        CREATE TABLE IF NOT EXISTS Dim_Agency (
            agency_id INTEGER PRIMARY KEY AUTOINCREMENT,
            agency_name TEXT NOT NULL UNIQUE,
            agency_type TEXT NOT NULL
        )
        """
        self.db.execute(query)
    
    def _create_fact_lottery_result(self):
        query = """
        CREATE TABLE IF NOT EXISTS Fact_Lottery_Result (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_id INTEGER NOT NULL,
            station_id INTEGER NOT NULL,
            prize_id INTEGER NOT NULL,
            prize_sequence INTEGER NOT NULL,
            result_number TEXT NOT NULL,
            FOREIGN KEY (date_id) REFERENCES Dim_Date(date_id),
            FOREIGN KEY (station_id) REFERENCES Dim_Station(station_id),
            FOREIGN KEY (prize_id) REFERENCES Dim_Prize(prize_id)
        )
        """
        self.db.execute(query)
    
    def _create_fact_revenue(self):
        query = """
        CREATE TABLE IF NOT EXISTS Fact_Revenue (
            revenue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_id INTEGER NOT NULL,
            station_id INTEGER NOT NULL,
            agency_id INTEGER NOT NULL,
            tickets_sold INTEGER NOT NULL,
            ticket_price REAL NOT NULL,
            total_revenue REAL NOT NULL,
            total_payout REAL NOT NULL,
            net_profit REAL NOT NULL,
            commission REAL NOT NULL,
            FOREIGN KEY (date_id) REFERENCES Dim_Date(date_id),
            FOREIGN KEY (station_id) REFERENCES Dim_Station(station_id),
            FOREIGN KEY (agency_id) REFERENCES Dim_Agency(agency_id)
        )
        """
        self.db.execute(query)
    
    def drop_all_tables(self):
        tables = [
            'Fact_Revenue',
            'Fact_Lottery_Result',
            'Dim_Agency',
            'Dim_Prize',
            'Dim_Station',
            'Dim_Date'
        ]
        for table in tables:
            self.db.execute(f"DROP TABLE IF EXISTS {table}")
    
    def initialize_reference_data(self):
        self._populate_dim_prize()
        self._populate_dim_station()
    
    def _populate_dim_prize(self):
        prizes = [
            ('Đặc biệt', 1, 1, 6, 2000000000),
            ('Nhất', 2, 1, 5, 30000000),
            ('Nhì', 3, 2, 5, 15000000),
            ('Ba', 4, 6, 5, 10000000),
            ('Tư', 5, 4, 4, 3000000),
            ('Năm', 6, 6, 4, 1000000),
            ('Sáu', 7, 3, 3, 400000),
            ('Bảy', 8, 4, 2, 200000)
        ]
        
        check = self.db.fetchone("SELECT COUNT(*) as cnt FROM Dim_Prize")
        if check['cnt'] == 0:
            query = """
            INSERT INTO Dim_Prize (prize_name, prize_order, quantity, digits, prize_value)
            VALUES (?, ?, ?, ?, ?)
            """
            self.db.executemany(query, prizes)
    
    def _populate_dim_station(self):
        stations = [
            ('Hà Nội', 'North'),
            ('TP Hồ Chí Minh', 'South'),
            ('Đà Nẵng', 'Central'),
            ('Cần Thơ', 'South'),
            ('An Giang', 'South'),
            ('Bình Dương', 'South'),
            ('Đồng Nai', 'South'),
            ('Kiên Giang', 'South'),
            ('Tây Ninh', 'South'),
            ('Vũng Tàu', 'South')
        ]
        
        check = self.db.fetchone("SELECT COUNT(*) as cnt FROM Dim_Station")
        if check['cnt'] == 0:
            query = "INSERT INTO Dim_Station (station_name, region) VALUES (?, ?)"
            self.db.executemany(query, stations)
