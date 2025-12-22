from src.utils.generator import DataGenerator
from datetime import datetime, timedelta


def test_generator():
    print("=" * 60)
    print("TEST DATA GENERATOR")
    print("=" * 60)
    
    lottery_path = "data/raw/lottery_results.csv"
    revenue_path = "data/raw/revenue_data.csv"
    
    generator = DataGenerator(lottery_path, revenue_path)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    print(f"\n📅 Tạo dữ liệu từ {start_date.strftime('%Y-%m-%d')} đến {end_date.strftime('%Y-%m-%d')}")
    print(f"   (90 ngày)\n")
    
    lottery_df, revenue_df = generator.generate(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    
    print("✅ Đã tạo xong dữ liệu!\n")
    
    print("-" * 60)
    print("📊 THỐNG KÊ DỮ LIỆU XỔ SỐ")
    print("-" * 60)
    print(f"Tổng số records: {len(lottery_df):,}")
    print(f"Số ngày có quay: {lottery_df['draw_date'].nunique()}")
    print(f"Số đài: {lottery_df['station_name'].nunique()}")
    print(f"\nPhân bố theo đài:")
    print(lottery_df['station_name'].value_counts().to_string())
    
    print(f"\n\nPhân bố theo giải:")
    print(lottery_df['prize_name'].value_counts().to_string())
    
    print("\n" + "-" * 60)
    print("💰 THỐNG KÊ DỮ LIỆU DOANH THU")
    print("-" * 60)
    print(f"Tổng số records: {len(revenue_df):,}")
    print(f"Số ngày bán hàng: {revenue_df['sale_date'].nunique()}")
    print(f"Số đài: {revenue_df['station_name'].nunique()}")
    print(f"Số đại lý: {revenue_df['agency_name'].nunique()}")
    
    print(f"\n\nTổng vé bán: {revenue_df['tickets_sold'].sum():,.0f}")
    print(f"Tổng doanh thu: {revenue_df['total_revenue'].sum():,.2f} VNĐ")
    print(f"Tổng tiền thưởng: {revenue_df['total_payout'].sum():,.2f} VNĐ")
    print(f"Tổng hoa hồng: {revenue_df['commission'].sum():,.2f} VNĐ")
    print(f"Lợi nhuận ròng: {revenue_df['net_profit'].sum():,.2f} VNĐ")
    
    print(f"\n\nPhân bố theo loại đại lý:")
    print(revenue_df.groupby('agency_type').agg({
        'tickets_sold': 'sum',
        'total_revenue': 'sum',
        'commission': 'sum'
    }).to_string())
    
    print("\n" + "-" * 60)
    print("🔍 XEM MẪU DỮ LIỆU")
    print("-" * 60)
    print("\n📋 Kết quả xổ số (5 dòng đầu):")
    print(lottery_df.head().to_string(index=False))
    
    print("\n\n💵 Doanh thu (5 dòng đầu):")
    print(revenue_df.head().to_string(index=False))
    
    print("\n" + "=" * 60)
    print("✅ KIỂM TRA HOÀN TẤT!")
    print("=" * 60)
    print(f"\n📁 Files đã tạo:")
    print(f"   - {lottery_path}")
    print(f"   - {revenue_path}")
    print("\n💡 Sử dụng DataExtractor để load dữ liệu vào RAM cho ETL\n")


if __name__ == "__main__":
    test_generator()
