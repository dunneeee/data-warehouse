import pandas as pd
from ..database.connection import DatabaseConnection


class LotteryAnalysis:
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def get_daily_lottery_results(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        query = """
        SELECT 
            d.full_date,
            d.day_of_week,
            s.station_name,
            s.region,
            p.prize_name,
            p.prize_order,
            l.prize_sequence,
            l.result_number
        FROM Fact_Lottery_Result l
        JOIN Dim_Date d ON l.date_id = d.date_id
        JOIN Dim_Station s ON l.station_id = s.station_id
        JOIN Dim_Prize p ON l.prize_id = p.prize_id
        """
        
        conditions = []
        if start_date:
            conditions.append(f"d.full_date >= '{start_date}'")
        if end_date:
            conditions.append(f"d.full_date <= '{end_date}'")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY d.full_date DESC, s.station_name, p.prize_order, l.prize_sequence"
        
        results = self.db.fetchall(query)
        df = pd.DataFrame([dict(row) for row in results])
        if not df.empty:
            df['full_date'] = pd.to_datetime(df['full_date'])
        return df
    
    def get_lottery_results_by_station(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        query = """
        SELECT 
            s.station_name,
            s.region,
            COUNT(DISTINCT l.date_id) as draw_days,
            COUNT(*) as total_results,
            COUNT(DISTINCT l.result_number) as unique_numbers
        FROM Fact_Lottery_Result l
        JOIN Dim_Station s ON l.station_id = s.station_id
        JOIN Dim_Date d ON l.date_id = d.date_id
        """
        
        conditions = []
        if start_date:
            conditions.append(f"d.full_date >= '{start_date}'")
        if end_date:
            conditions.append(f"d.full_date <= '{end_date}'")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += """
        GROUP BY s.station_name, s.region
        ORDER BY draw_days DESC
        """
        
        results = self.db.fetchall(query)
        return pd.DataFrame([dict(row) for row in results])
    
    def get_number_frequency(self, digit_length: int = None, limit: int = 20) -> pd.DataFrame:
        if digit_length:
            query = f"""
            SELECT 
                SUBSTR(l.result_number, -{digit_length}) as number_part,
                COUNT(*) as frequency,
                COUNT(DISTINCT l.date_id) as appeared_on_days
            FROM Fact_Lottery_Result l
            JOIN Dim_Prize p ON l.prize_id = p.prize_id
            WHERE p.digits >= {digit_length}
            GROUP BY number_part
            ORDER BY frequency DESC
            LIMIT {limit}
            """
        else:
            query = f"""
            SELECT 
                l.result_number,
                p.prize_name,
                COUNT(*) as frequency,
                COUNT(DISTINCT l.date_id) as appeared_on_days,
                COUNT(DISTINCT l.station_id) as appeared_on_stations
            FROM Fact_Lottery_Result l
            JOIN Dim_Prize p ON l.prize_id = p.prize_id
            GROUP BY l.result_number, p.prize_name
            ORDER BY frequency DESC
            LIMIT {limit}
            """
        
        results = self.db.fetchall(query)
        return pd.DataFrame([dict(row) for row in results])
    
    def get_prize_distribution(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        query = """
        SELECT 
            p.prize_name,
            p.prize_order,
            p.quantity as expected_per_draw,
            COUNT(*) as total_count,
            COUNT(DISTINCT l.date_id) as days_appeared,
            COUNT(DISTINCT l.station_id) as stations_appeared
        FROM Fact_Lottery_Result l
        JOIN Dim_Prize p ON l.prize_id = p.prize_id
        JOIN Dim_Date d ON l.date_id = d.date_id
        """
        
        conditions = []
        if start_date:
            conditions.append(f"d.full_date >= '{start_date}'")
        if end_date:
            conditions.append(f"d.full_date <= '{end_date}'")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += """
        GROUP BY p.prize_name, p.prize_order, p.quantity
        ORDER BY p.prize_order
        """
        
        results = self.db.fetchall(query)
        return pd.DataFrame([dict(row) for row in results])
    
    def get_hot_cold_numbers(self, digit_length: int = 2, period_days: int = 30) -> pd.DataFrame:
        query = f"""
        SELECT 
            SUBSTR(l.result_number, -{digit_length}) as number,
            COUNT(*) as frequency,
            MAX(d.full_date) as last_appeared,
            MIN(d.full_date) as first_appeared,
            CASE 
                WHEN COUNT(*) >= (
                    SELECT AVG(cnt) * 1.2 
                    FROM (
                        SELECT SUBSTR(result_number, -{digit_length}) as num, COUNT(*) as cnt
                        FROM Fact_Lottery_Result
                        JOIN Dim_Date ON Fact_Lottery_Result.date_id = Dim_Date.date_id
                        WHERE Dim_Date.full_date >= date('now', '-{period_days} days')
                        GROUP BY num
                    )
                ) THEN 'Hot'
                WHEN COUNT(*) <= (
                    SELECT AVG(cnt) * 0.8
                    FROM (
                        SELECT SUBSTR(result_number, -{digit_length}) as num, COUNT(*) as cnt
                        FROM Fact_Lottery_Result
                        JOIN Dim_Date ON Fact_Lottery_Result.date_id = Dim_Date.date_id
                        WHERE Dim_Date.full_date >= date('now', '-{period_days} days')
                        GROUP BY num
                    )
                ) THEN 'Cold'
                ELSE 'Normal'
            END as status
        FROM Fact_Lottery_Result l
        JOIN Dim_Date d ON l.date_id = d.date_id
        WHERE d.full_date >= date('now', '-{period_days} days')
        GROUP BY number
        ORDER BY frequency DESC
        """
        
        results = self.db.fetchall(query)
        return pd.DataFrame([dict(row) for row in results])
    
    def get_monthly_lottery_summary(self) -> pd.DataFrame:
        query = """
        SELECT 
            d.year,
            d.month,
            d.year || '-' || printf('%02d', d.month) as year_month,
            COUNT(DISTINCT l.date_id) as draw_days,
            COUNT(DISTINCT l.station_id) as active_stations,
            COUNT(*) as total_results,
            COUNT(DISTINCT l.result_number) as unique_numbers
        FROM Fact_Lottery_Result l
        JOIN Dim_Date d ON l.date_id = d.date_id
        GROUP BY d.year, d.month
        ORDER BY d.year, d.month
        """
        
        results = self.db.fetchall(query)
        return pd.DataFrame([dict(row) for row in results])
    
    def get_number_patterns(self, digit_length: int = 2) -> pd.DataFrame:
        query = f"""
        SELECT 
            SUBSTR(l.result_number, -{digit_length}) as number,
            COUNT(*) as frequency,
            ROUND(AVG(CAST(SUBSTR(l.result_number, -{digit_length}) AS INTEGER)), 2) as avg_value,
            MIN(CAST(SUBSTR(l.result_number, -{digit_length}) AS INTEGER)) as min_value,
            MAX(CAST(SUBSTR(l.result_number, -{digit_length}) AS INTEGER)) as max_value
        FROM Fact_Lottery_Result l
        GROUP BY number
        HAVING frequency >= 10
        ORDER BY frequency DESC
        """
        
        results = self.db.fetchall(query)
        return pd.DataFrame([dict(row) for row in results])
    
    def get_consecutive_numbers(self, digit_length: int = 2, limit: int = 20) -> pd.DataFrame:
        query = f"""
        WITH numbered_results AS (
            SELECT 
                l.result_number,
                SUBSTR(l.result_number, -{digit_length}) as number,
                d.full_date,
                ROW_NUMBER() OVER (ORDER BY d.full_date) as rn
            FROM Fact_Lottery_Result l
            JOIN Dim_Date d ON l.date_id = d.date_id
        )
        SELECT 
            number,
            COUNT(*) as appearance_count,
            COUNT(*) * 100.0 / (SELECT COUNT(*) FROM numbered_results) as appearance_rate
        FROM numbered_results
        GROUP BY number
        ORDER BY appearance_count DESC
        LIMIT {limit}
        """
        
        results = self.db.fetchall(query)
        return pd.DataFrame([dict(row) for row in results])
    
    def get_results_by_day_of_week(self) -> pd.DataFrame:
        query = """
        SELECT 
            d.day_of_week,
            d.is_weekend,
            COUNT(DISTINCT l.date_id) as draw_days,
            COUNT(DISTINCT l.station_id) as active_stations,
            COUNT(*) as total_results
        FROM Fact_Lottery_Result l
        JOIN Dim_Date d ON l.date_id = d.date_id
        GROUP BY d.day_of_week, d.is_weekend
        ORDER BY 
            CASE d.day_of_week
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
                WHEN 'Saturday' THEN 6
                WHEN 'Sunday' THEN 7
            END
        """
        
        results = self.db.fetchall(query)
        return pd.DataFrame([dict(row) for row in results])
    
    def get_special_prize_history(self, start_date: str = None, end_date: str = None, limit: int = 50) -> pd.DataFrame:
        query = """
        SELECT 
            d.full_date,
            d.day_of_week,
            s.station_name,
            l.result_number
        FROM Fact_Lottery_Result l
        JOIN Dim_Date d ON l.date_id = d.date_id
        JOIN Dim_Station s ON l.station_id = s.station_id
        JOIN Dim_Prize p ON l.prize_id = p.prize_id
        WHERE p.prize_name = 'Đặc biệt'
        """
        
        conditions = []
        if start_date:
            conditions.append(f"d.full_date >= '{start_date}'")
        if end_date:
            conditions.append(f"d.full_date <= '{end_date}'")
        
        if conditions:
            query += " AND " + " AND ".join(conditions)
        
        query += f" ORDER BY d.full_date DESC LIMIT {limit}"
        
        results = self.db.fetchall(query)
        df = pd.DataFrame([dict(row) for row in results])
        if not df.empty:
            df['full_date'] = pd.to_datetime(df['full_date'])
        return df
    
    def get_digit_frequency_analysis(self, position: int = -1) -> pd.DataFrame:
        query = f"""
        SELECT 
            SUBSTR(l.result_number, {position}, 1) as digit,
            COUNT(*) as frequency,
            COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Fact_Lottery_Result) as percentage
        FROM Fact_Lottery_Result l
        WHERE LENGTH(l.result_number) >= ABS({position})
        GROUP BY digit
        ORDER BY frequency DESC
        """
        
        results = self.db.fetchall(query)
        return pd.DataFrame([dict(row) for row in results])
    
    def get_station_prize_summary(self, station_name: str = None) -> pd.DataFrame:
        query = """
        SELECT 
            s.station_name,
            p.prize_name,
            COUNT(*) as total_count,
            COUNT(DISTINCT l.date_id) as days_appeared
        FROM Fact_Lottery_Result l
        JOIN Dim_Station s ON l.station_id = s.station_id
        JOIN Dim_Prize p ON l.prize_id = p.prize_id
        """
        
        if station_name:
            query += f" WHERE s.station_name = '{station_name}'"
        
        query += """
        GROUP BY s.station_name, p.prize_name
        ORDER BY s.station_name, p.prize_name
        """
        
        results = self.db.fetchall(query)
        return pd.DataFrame([dict(row) for row in results])
