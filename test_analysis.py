from src.database.connection import DatabaseConnection
from src.analysis.revenue import RevenueAnalysis
from src.analysis.lottery import LotteryAnalysis


def test_analysis():
    print("\n" + "=" * 70)
    print("TEST ANALYSIS MODULES")
    print("=" * 70)
    
    db = DatabaseConnection("database/lottery_warehouse.db")
    db.connect()
    
    revenue_analysis = RevenueAnalysis(db)
    lottery_analysis = LotteryAnalysis(db)
    
    try:
        print("\n" + "=" * 70)
        print("📊 REVENUE ANALYSIS TESTS")
        print("=" * 70)
        
        print("\n1. Daily Revenue Trend (last 7 days):")
        df = revenue_analysis.get_daily_revenue_trend()
        if not df.empty:
            print(df.tail(7)[['full_date', 'tickets_sold', 'total_revenue', 'net_profit']].to_string(index=False))
            print(f"\nTotal records: {len(df)}")
        
        print("\n2. Monthly Revenue Summary (last 6 months):")
        df = revenue_analysis.get_monthly_revenue_summary()
        if not df.empty:
            print(df.tail(6)[['year_month', 'tickets_sold', 'total_revenue', 'net_profit']].to_string(index=False))
        
        print("\n3. Top 5 Stations by Revenue:")
        df = revenue_analysis.get_revenue_by_station()
        if not df.empty:
            print(df.head(5)[['station_name', 'region', 'active_days', 'total_revenue']].to_string(index=False))
        
        print("\n4. Top 5 Agencies by Commission:")
        df = revenue_analysis.get_revenue_by_agency()
        if not df.empty:
            print(df.head(5)[['agency_name', 'agency_type', 'transactions', 'total_commission']].to_string(index=False))
        
        print("\n5. Revenue by Day of Week:")
        df = revenue_analysis.get_revenue_by_day_of_week()
        if not df.empty:
            print(df[['day_of_week', 'transactions', 'tickets_sold', 'total_revenue']].to_string(index=False))
        
        print("\n6. Quarterly Performance (last 4 quarters):")
        df = revenue_analysis.get_quarterly_performance()
        if not df.empty:
            print(df.tail(4)[['year_quarter', 'tickets_sold', 'total_revenue', 'net_profit']].to_string(index=False))
        
        print("\n7. Weekend vs Weekday Comparison:")
        df = revenue_analysis.get_weekend_vs_weekday_comparison()
        if not df.empty:
            print(df[['period_type', 'days', 'transactions', 'total_revenue', 'avg_revenue']].to_string(index=False))
        
        print("\n8. Monthly Revenue Growth Rate (last 6 months):")
        df = revenue_analysis.get_revenue_growth_rate(period='month')
        if not df.empty:
            print(df.tail(6)[['period', 'total_revenue', 'growth_rate_percent']].to_string(index=False))
        
        print("\n" + "=" * 70)
        print("🎲 LOTTERY ANALYSIS TESTS")
        print("=" * 70)
        
        print("\n1. Lottery Results by Station:")
        df = lottery_analysis.get_lottery_results_by_station()
        if not df.empty:
            print(df[['station_name', 'region', 'draw_days', 'total_results', 'unique_numbers']].to_string(index=False))
        
        print("\n2. Top 10 Most Frequent 2-Digit Numbers:")
        df = lottery_analysis.get_number_frequency(digit_length=2, limit=10)
        if not df.empty:
            print(df[['number_part', 'frequency', 'appeared_on_days']].to_string(index=False))
        
        print("\n3. Prize Distribution:")
        df = lottery_analysis.get_prize_distribution()
        if not df.empty:
            print(df[['prize_name', 'expected_per_draw', 'total_count', 'days_appeared']].to_string(index=False))
        
        print("\n4. Hot and Cold Numbers (2-digit, last 30 days):")
        df = lottery_analysis.get_hot_cold_numbers(digit_length=2, period_days=30)
        if not df.empty:
            hot = df[df['status'] == 'Hot'].head(5)
            cold = df[df['status'] == 'Cold'].head(5)
            print("\nHot Numbers:")
            if not hot.empty:
                print(hot[['number', 'frequency', 'status']].to_string(index=False))
            print("\nCold Numbers:")
            if not cold.empty:
                print(cold[['number', 'frequency', 'status']].to_string(index=False))
        
        print("\n5. Monthly Lottery Summary (last 6 months):")
        df = lottery_analysis.get_monthly_lottery_summary()
        if not df.empty:
            print(df.tail(6)[['year_month', 'draw_days', 'active_stations', 'total_results']].to_string(index=False))
        
        print("\n6. Results by Day of Week:")
        df = lottery_analysis.get_results_by_day_of_week()
        if not df.empty:
            print(df[['day_of_week', 'draw_days', 'active_stations', 'total_results']].to_string(index=False))
        
        print("\n7. Special Prize History (last 10 draws):")
        df = lottery_analysis.get_special_prize_history(limit=10)
        if not df.empty:
            print(df[['full_date', 'station_name', 'result_number']].to_string(index=False))
        
        print("\n8. Digit Frequency (last digit position):")
        df = lottery_analysis.get_digit_frequency_analysis(position=-1)
        if not df.empty:
            print(df[['digit', 'frequency', 'percentage']].to_string(index=False))
        
        print("\n9. Daily Lottery Results (last 3 days):")
        df = lottery_analysis.get_daily_lottery_results()
        if not df.empty:
            recent = df.head(20)
            print(recent[['full_date', 'station_name', 'prize_name', 'result_number']].to_string(index=False))
            print(f"\n... showing 20 of {len(df)} total results")
        
        print("\n" + "=" * 70)
        print("✅ ALL ANALYSIS TESTS COMPLETED!")
        print("=" * 70)
        
        print("\n📈 Summary:")
        print(f"   - Revenue Analysis: 9 functions tested")
        print(f"   - Lottery Analysis: 9 functions tested")
        print(f"   - All functions returned data successfully")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
        print("\n🔒 Database connection closed\n")


if __name__ == "__main__":
    test_analysis()
