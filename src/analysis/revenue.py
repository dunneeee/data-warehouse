import pandas as pd
from ..database.connection import DatabaseConnection


class RevenueAnalysis:
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def get_daily_revenue_trend(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        query = """
        SELECT 
            d.full_date,
            d.day_of_week,
            d.is_weekend,
            SUM(r.tickets_sold) as tickets_sold,
            SUM(r.total_revenue) as total_revenue,
            SUM(r.total_payout) as total_payout,
            SUM(r.net_profit) as net_profit,
            SUM(r.commission) as commission,
            COUNT(DISTINCT r.station_id) as active_stations,
            COUNT(DISTINCT r.agency_id) as active_agencies
        FROM Fact_Revenue r
        JOIN Dim_Date d ON r.date_id = d.date_id
        """
        
        conditions = []
        if start_date:
            conditions.append(f"d.full_date >= '{start_date}'")
        if end_date:
            conditions.append(f"d.full_date <= '{end_date}'")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += """
        GROUP BY d.full_date, d.day_of_week, d.is_weekend
        ORDER BY d.full_date
        """
        
        results = self.db.fetchall(query)
        df = pd.DataFrame([dict(row) for row in results])
        if not df.empty:
            df['full_date'] = pd.to_datetime(df['full_date'])
        return df
    
    def get_monthly_revenue_summary(self) -> pd.DataFrame:
        query = """
        SELECT 
            d.year,
            d.month,
            d.year || '-' || printf('%02d', d.month) as year_month,
            SUM(r.tickets_sold) as tickets_sold,
            SUM(r.total_revenue) as total_revenue,
            SUM(r.total_payout) as total_payout,
            SUM(r.net_profit) as net_profit,
            SUM(r.commission) as commission,
            AVG(r.total_revenue) as avg_daily_revenue
        FROM Fact_Revenue r
        JOIN Dim_Date d ON r.date_id = d.date_id
        GROUP BY d.year, d.month
        ORDER BY d.year, d.month
        """
        
        results = self.db.fetchall(query)
        return pd.DataFrame([dict(row) for row in results])
    
    def get_revenue_by_station(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        query = """
        SELECT 
            s.station_name,
            s.region,
            COUNT(DISTINCT r.date_id) as active_days,
            SUM(r.tickets_sold) as tickets_sold,
            SUM(r.total_revenue) as total_revenue,
            SUM(r.total_payout) as total_payout,
            SUM(r.net_profit) as net_profit,
            AVG(r.total_revenue) as avg_revenue_per_day
        FROM Fact_Revenue r
        JOIN Dim_Station s ON r.station_id = s.station_id
        JOIN Dim_Date d ON r.date_id = d.date_id
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
        ORDER BY total_revenue DESC
        """
        
        results = self.db.fetchall(query)
        return pd.DataFrame([dict(row) for row in results])
    
    def get_revenue_by_agency(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        query = """
        SELECT 
            a.agency_name,
            a.agency_type,
            COUNT(*) as transactions,
            SUM(r.tickets_sold) as tickets_sold,
            SUM(r.total_revenue) as total_revenue,
            SUM(r.commission) as total_commission,
            AVG(r.total_revenue) as avg_revenue_per_transaction
        FROM Fact_Revenue r
        JOIN Dim_Agency a ON r.agency_id = a.agency_id
        JOIN Dim_Date d ON r.date_id = d.date_id
        """
        
        conditions = []
        if start_date:
            conditions.append(f"d.full_date >= '{start_date}'")
        if end_date:
            conditions.append(f"d.full_date <= '{end_date}'")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += """
        GROUP BY a.agency_name, a.agency_type
        ORDER BY total_revenue DESC
        """
        
        results = self.db.fetchall(query)
        return pd.DataFrame([dict(row) for row in results])
    
    def get_revenue_by_day_of_week(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        query = """
        SELECT 
            d.day_of_week,
            d.is_weekend,
            COUNT(*) as transactions,
            SUM(r.tickets_sold) as tickets_sold,
            SUM(r.total_revenue) as total_revenue,
            AVG(r.total_revenue) as avg_revenue
        FROM Fact_Revenue r
        JOIN Dim_Date d ON r.date_id = d.date_id
        """
        
        conditions = []
        if start_date:
            conditions.append(f"d.full_date >= '{start_date}'")
        if end_date:
            conditions.append(f"d.full_date <= '{end_date}'")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += """
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
    
    def get_quarterly_performance(self) -> pd.DataFrame:
        query = """
        SELECT 
            d.year,
            d.quarter,
            d.year || '-Q' || d.quarter as year_quarter,
            SUM(r.tickets_sold) as tickets_sold,
            SUM(r.total_revenue) as total_revenue,
            SUM(r.total_payout) as total_payout,
            SUM(r.net_profit) as net_profit,
            AVG(r.total_revenue) as avg_daily_revenue
        FROM Fact_Revenue r
        JOIN Dim_Date d ON r.date_id = d.date_id
        GROUP BY d.year, d.quarter
        ORDER BY d.year, d.quarter
        """
        
        results = self.db.fetchall(query)
        return pd.DataFrame([dict(row) for row in results])
    
    def get_top_performing_combinations(self, limit: int = 10) -> pd.DataFrame:
        query = f"""
        SELECT 
            s.station_name,
            a.agency_name,
            a.agency_type,
            COUNT(*) as transactions,
            SUM(r.tickets_sold) as tickets_sold,
            SUM(r.total_revenue) as total_revenue,
            AVG(r.total_revenue) as avg_revenue
        FROM Fact_Revenue r
        JOIN Dim_Station s ON r.station_id = s.station_id
        JOIN Dim_Agency a ON r.agency_id = a.agency_id
        GROUP BY s.station_name, a.agency_name, a.agency_type
        ORDER BY total_revenue DESC
        LIMIT {limit}
        """
        
        results = self.db.fetchall(query)
        return pd.DataFrame([dict(row) for row in results])
    
    def get_weekend_vs_weekday_comparison(self) -> pd.DataFrame:
        query = """
        SELECT 
            CASE WHEN d.is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END as period_type,
            COUNT(DISTINCT d.date_id) as days,
            COUNT(*) as transactions,
            SUM(r.tickets_sold) as tickets_sold,
            SUM(r.total_revenue) as total_revenue,
            AVG(r.total_revenue) as avg_revenue
        FROM Fact_Revenue r
        JOIN Dim_Date d ON r.date_id = d.date_id
        GROUP BY d.is_weekend
        """
        
        results = self.db.fetchall(query)
        return pd.DataFrame([dict(row) for row in results])
    
    def get_revenue_growth_rate(self, period: str = 'month') -> pd.DataFrame:
        if period == 'month':
            query = """
            WITH monthly_revenue AS (
                SELECT 
                    d.year,
                    d.month,
                    d.year || '-' || printf('%02d', d.month) as period,
                    SUM(r.total_revenue) as total_revenue
                FROM Fact_Revenue r
                JOIN Dim_Date d ON r.date_id = d.date_id
                GROUP BY d.year, d.month
                ORDER BY d.year, d.month
            )
            SELECT 
                period,
                total_revenue,
                LAG(total_revenue) OVER (ORDER BY period) as prev_revenue,
                ROUND(
                    (total_revenue - LAG(total_revenue) OVER (ORDER BY period)) * 100.0 / 
                    LAG(total_revenue) OVER (ORDER BY period), 2
                ) as growth_rate_percent
            FROM monthly_revenue
            ORDER BY period
            """
        else:  # quarterly
            query = """
            WITH quarterly_revenue AS (
                SELECT 
                    d.year,
                    d.quarter,
                    d.year || '-Q' || d.quarter as period,
                    SUM(r.total_revenue) as total_revenue
                FROM Fact_Revenue r
                JOIN Dim_Date d ON r.date_id = d.date_id
                GROUP BY d.year, d.quarter
                ORDER BY d.year, d.quarter
            )
            SELECT 
                period,
                total_revenue,
                LAG(total_revenue) OVER (ORDER BY period) as prev_revenue,
                ROUND(
                    (total_revenue - LAG(total_revenue) OVER (ORDER BY period)) * 100.0 / 
                    LAG(total_revenue) OVER (ORDER BY period), 2
                ) as growth_rate_percent
            FROM quarterly_revenue
            ORDER BY period
            """
        
        results = self.db.fetchall(query)
        return pd.DataFrame([dict(row) for row in results])
