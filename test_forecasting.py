from pathlib import Path
import sys

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database.connection import DatabaseConnection
from src.forecasting import train_revenue_model


def test_revenue_forecasting():
    db_path = project_root / "database" / "lottery_warehouse.db"
    db = DatabaseConnection(str(db_path))
    db.connect()
    
    print("=" * 70)
    print("KIỂM THỬ DỰ ĐOÁN DOANH THU")
    print("=" * 70)
    
    print("\n1. Training model...")
    forecaster, forecast_12m = train_revenue_model(db)
    
    print(f"\n2. Metrics:")
    metrics = forecaster.get_metrics()
    for metric, value in metrics.items():
        print(f"   {metric}: {value:,.2f}")
    
    print(f"\n3. Feature Importance:")
    importance = forecaster.get_feature_importance()
    print(importance.to_string(index=False))
    
    print(f"\n4. Dự đoán 12 tháng tới:")
    print(forecast_12m.to_string(index=False))
    
    print(f"\n5. Lưu model...")
    model_path = project_root / "database" / "revenue_model.pkl"
    forecaster.save_model(str(model_path))
    print(f"   Model đã lưu: {model_path}")
    
    print(f"\n6. Load model và test predict...")
    from src.forecasting import RevenueForecasting
    new_forecaster = RevenueForecasting()
    new_forecaster.load_model(str(model_path))
    print(f"   Model đã load: {new_forecaster}")
    
    db.close()
    print("\n✅ Test hoàn thành!")


if __name__ == "__main__":
    test_revenue_forecasting()
