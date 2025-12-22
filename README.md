# Data Warehouse - Lottery & Revenue Analytics

Hệ thống kho dữ liệu phân tích xổ số và doanh thu với khả năng dự đoán sử dụng Machine Learning.

## Tính năng

- ✅ ETL Pipeline với Star Schema (SQLite)
- ✅ Phân tích doanh thu và xổ số (21 query methods)
- ✅ Dashboard trực quan với Streamlit & Altair
- ✅ Dự đoán doanh thu 12 tháng (Linear Regression)
- ✅ Cross-correlation analysis (Lottery → Revenue impact)
- ✅ UI tiếng Việt với date range filter

## Yêu cầu hệ thống

- Python 3.12+
- SQLite3
- 2GB RAM
- 500MB disk space

## Cài đặt

### 1. Clone repository
```bash
cd /path/to/your/projects
git clone https://github.com/dunneeee/data-warehouse.git
cd data-warehouse
```

### 2. Tạo virtual environment
```bash
python -m venv venv
source venv/bin/activate.fish  # Fish shell
# hoặc
source venv/bin/activate       # Bash/Zsh
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

**Packages:**
- pandas>=2.0.0
- streamlit>=1.29.0
- altair>=5.0.0
- scikit-learn>=1.3.0

## Khởi tạo Database

### Option 1: Chạy full ETL pipeline
```bash
python test_warehouse.py
```

Tạo database với 10 năm dữ liệu (2015-2025):
- ~3,650 ngày lottery results
- ~180,000 lottery records
- ~36,500 revenue records

### Option 2: Custom date range
```python
from src.warehouse_facade import WarehouseFacade

facade = WarehouseFacade()
facade.full_etl_pipeline(
    start_date='2020-01-01',
    end_date='2025-12-22'
)
facade.close()
```

## Chạy Dashboard

```bash
streamlit run src/ui/dashboard.py
```

Dashboard sẽ mở tại: http://localhost:8501

### Các tab chính

1. **Phân tích Doanh thu**
   - Xu hướng theo ngày/tháng
   - Doanh thu theo đài/đại lý
   - Tỷ lệ tăng trưởng
   - So sánh cuối tuần vs ngày thường

2. **Phân tích Xổ số**
   - Top số xuất hiện nhiều nhất
   - Số nóng và số lạnh
   - Phân bố giải thưởng
   - Tần suất chữ số

3. **Thông tin Tổng hợp**
   - Tổng hợp theo tháng (revenue + lottery)
   - Hiệu suất đài
   - **Cross-correlation: Lottery → Revenue impact**

4. **Dự đoán Doanh thu**
   - Chọn năm dự đoán (2026-2030)
   - Metrics: R², MAE, RMSE, MAPE
   - Biểu đồ dự đoán 12 tháng
   - Feature importance

## Cấu trúc Project

```
data-warehouse-v2/
├── data/raw/                    # CSV data files
├── database/                    # SQLite database
│   └── lottery_warehouse.db
├── docs/                        # Documentation
│   ├── forecasting_knowledge.md
│   ├── cross_correlation_analysis.md
│   └── erd_mermaid.mermaid
├── src/
│   ├── analysis/               # Query modules
│   │   ├── revenue.py
│   │   └── lottery.py
│   ├── database/               # DB connection & schema
│   │   ├── connection.py
│   │   └── schema.py
│   ├── etl/                    # ETL pipeline
│   │   ├── extractor.py
│   │   ├── transformer.py
│   │   └── loader.py
│   ├── forecasting/            # ML prediction
│   │   ├── strategy.py
│   │   └── revenue_forecasting.py
│   ├── ui/                     # Dashboard UI
│   │   ├── dashboard.py
│   │   ├── revenue_tab.py
│   │   ├── lottery_tab.py
│   │   ├── insights_tab.py
│   │   └── forecasting_tab.py
│   ├── utils/                  # Data generator
│   │   └── generator.py
│   └── warehouse_facade.py     # Main orchestrator
├── test_*.py                   # Test files
└── requirements.txt
```

## Database Schema (Star Schema)

### Dimension Tables
- **Dim_Date**: Ngày, tháng, năm, quý, ngày trong tuần
- **Dim_Station**: 10 đài xổ số (Miền Bắc, Trung, Nam)
- **Dim_Prize**: 9 cấp giải (Đặc biệt → Tám)
- **Dim_Agency**: Đại lý bán vé

### Fact Tables
- **Fact_Lottery_Result**: Kết quả xổ số theo ngày
- **Fact_Revenue**: Doanh thu bán vé theo ngày

## API Usage

### Revenue Analysis
```python
from src.database.connection import DatabaseConnection
from src.analysis.revenue import RevenueAnalysis

db = DatabaseConnection("database/lottery_warehouse.db")
db.connect()

revenue = RevenueAnalysis(db)

# Daily trend
df = revenue.get_daily_revenue_trend()

# Monthly summary
df = revenue.get_monthly_revenue_summary()

# Cross-correlation
df = revenue.get_lottery_number_revenue_impact()

db.close()
```

### Lottery Analysis
```python
from src.analysis.lottery import LotteryAnalysis

lottery = LotteryAnalysis(db)

# Hot/cold numbers
df = lottery.get_hot_cold_numbers(digit_length=2, period_days=30)

# Number frequency
df = lottery.get_number_frequency(digit_length=2, limit=10)

# Special prize history
df = lottery.get_special_prize_history(limit=20)
```

### Forecasting
```python
from src.forecasting import train_revenue_model

forecaster, forecast_12m = train_revenue_model(db)

# Metrics
metrics = forecaster.get_metrics()
print(f"R²: {metrics['R2']:.4f}")
print(f"MAPE: {metrics['MAPE']:.2f}%")

# Feature importance
importance = forecaster.get_feature_importance()
print(importance.head())

# Save/load model
forecaster.save_model("my_model.pkl")
forecaster.load_model("my_model.pkl")
```

## Testing

### Test data generator
```bash
python test_generator.py
```

### Test ETL pipeline
```bash
python test_warehouse.py
```

### Test analysis queries
```bash
python test_analysis.py
```

### Test forecasting
```bash
python test_forecasting.py
```

## Troubleshooting

### Database locked
```bash
# Đóng tất cả connections
rm -f database/lottery_warehouse.db-journal
```

### Streamlit cache issues
```bash
# Xóa cache
find . -type d -name __pycache__ -exec rm -rf {} +
streamlit cache clear
```

### Model not found
```bash
# Train lại model
python test_forecasting.py
```

### Import errors
```bash
# Cài lại dependencies
pip install -r requirements.txt --force-reinstall
```

## Performance Tips

1. **Database optimization**
   - Index đã tạo sẵn trên foreign keys
   - Use EXPLAIN QUERY PLAN để analyze slow queries

2. **Memory management**
   - Streamlit auto-reload khi file thay đổi
   - Đóng database connections sau khi xong

3. **Data size**
   - 1 năm data ≈ 5MB
   - 10 năm data ≈ 50MB
   - Optimal: 5-10 năm

## Documentation

- [Forecasting Knowledge](docs/forecasting_knowledge.md) - Linear Regression analysis
- [Cross-Correlation Analysis](docs/cross_correlation_analysis.md) - Lottery impact study
- [ERD Diagram](docs/erd_mermaid.mermaid) - Database schema

## Tech Stack

- **Database:** SQLite3
- **Data Processing:** Pandas
- **ML:** scikit-learn (LinearRegression, StandardScaler)
- **Visualization:** Streamlit, Altair
- **Language:** Python 3.12

## License

Educational project - DNVKU Data Warehouse Lab

## Contact

Project maintained by: Dunn
