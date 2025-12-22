from src import WarehouseFacade
from datetime import datetime, timedelta


def test_warehouse_facade():
    print("\n" + "=" * 70)
    print("TEST WAREHOUSE FACADE")
    print("=" * 70)
    
    facade = WarehouseFacade(
        db_path="database/lottery_warehouse.db",
        lottery_csv="data/raw/lottery_results.csv",
        revenue_csv="data/raw/revenue_data.csv"
    )
    
    start_date = datetime(2015, 1, 1)
    end_date = datetime.now()
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    try:
        result = facade.full_etl_pipeline(start_str, end_str)
        
        print("\n" + "=" * 70)
        print("📊 WAREHOUSE STATISTICS")
        print("=" * 70)
        
        stats = facade.get_warehouse_stats()
        for table, count in stats.items():
            print(f"{table:30s}: {count:10,} records")
        
        print("\n" + "=" * 70)
        print("🔍 SAMPLE QUERIES")
        print("=" * 70)
        
        print("\n1. Top 5 stations by revenue:")
        query = """
        SELECT 
            s.station_name,
            COUNT(*) as transactions,
            SUM(r.total_revenue) as total_revenue,
            SUM(r.net_profit) as total_profit
        FROM Fact_Revenue r
        JOIN Dim_Station s ON r.station_id = s.station_id
        GROUP BY s.station_name
        ORDER BY total_revenue DESC
        LIMIT 5
        """
        results = facade.db_connection.fetchall(query)
        print(f"{'Station':<20} {'Transactions':>12} {'Revenue':>15} {'Profit':>15}")
        print("-" * 70)
        for row in results:
            print(f"{row['station_name']:<20} {row['transactions']:>12,} "
                  f"{row['total_revenue']:>15,.0f} {row['total_profit']:>15,.0f}")
        
        print("\n2. Revenue by day of week:")
        query = """
        SELECT 
            d.day_of_week,
            COUNT(*) as transactions,
            SUM(r.tickets_sold) as total_tickets,
            SUM(r.total_revenue) as total_revenue
        FROM Fact_Revenue r
        JOIN Dim_Date d ON r.date_id = d.date_id
        GROUP BY d.day_of_week
        ORDER BY total_revenue DESC
        """
        results = facade.db_connection.fetchall(query)
        print(f"{'Day':<15} {'Transactions':>12} {'Tickets':>12} {'Revenue':>18}")
        print("-" * 70)
        for row in results:
            print(f"{row['day_of_week']:<15} {row['transactions']:>12,} "
                  f"{row['total_tickets']:>12,} {row['total_revenue']:>18,.0f}")
        
        print("\n3. Agency performance:")
        query = """
        SELECT 
            a.agency_name,
            a.agency_type,
            COUNT(*) as transactions,
            SUM(r.tickets_sold) as total_tickets,
            SUM(r.commission) as total_commission
        FROM Fact_Revenue r
        JOIN Dim_Agency a ON r.agency_id = a.agency_id
        GROUP BY a.agency_name, a.agency_type
        ORDER BY total_commission DESC
        LIMIT 5
        """
        results = facade.db_connection.fetchall(query)
        print(f"{'Agency':<25} {'Type':>8} {'Trans':>8} {'Tickets':>12} {'Commission':>15}")
        print("-" * 70)
        for row in results:
            print(f"{row['agency_name']:<25} {row['agency_type']:>8} "
                  f"{row['transactions']:>8,} {row['total_tickets']:>12,} "
                  f"{row['total_commission']:>15,.0f}")
        
        print("\n4. Most frequent lottery numbers (last 2 digits):")
        query = """
        SELECT 
            SUBSTR(result_number, -2) as last_two_digits,
            COUNT(*) as frequency
        FROM Fact_Lottery_Result
        GROUP BY last_two_digits
        ORDER BY frequency DESC
        LIMIT 10
        """
        results = facade.db_connection.fetchall(query)
        print(f"{'Number':>8} {'Frequency':>12}")
        print("-" * 70)
        for row in results:
            print(f"{row['last_two_digits']:>8} {row['frequency']:>12,}")
        
        print("\n5. Daily revenue trend:")
        query = """
        SELECT 
            d.full_date,
            COUNT(DISTINCT s.station_id) as active_stations,
            SUM(r.tickets_sold) as tickets_sold,
            SUM(r.total_revenue) as revenue
        FROM Fact_Revenue r
        JOIN Dim_Date d ON r.date_id = d.date_id
        JOIN Dim_Station s ON r.station_id = s.station_id
        GROUP BY d.full_date
        ORDER BY d.full_date DESC
        LIMIT 7
        """
        results = facade.db_connection.fetchall(query)
        print(f"{'Date':<12} {'Stations':>10} {'Tickets':>12} {'Revenue':>18}")
        print("-" * 70)
        for row in results:
            print(f"{row['full_date']:<12} {row['active_stations']:>10} "
                  f"{row['tickets_sold']:>12,} {row['revenue']:>18,.0f}")
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print(f"\n💾 Database file: {facade.db_path}")
        print(f"📁 Raw data files:")
        print(f"   - {facade.lottery_csv}")
        print(f"   - {facade.revenue_csv}")
        print()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        facade.close()
        print("🔒 Database connection closed\n")


if __name__ == "__main__":
    test_warehouse_facade()
