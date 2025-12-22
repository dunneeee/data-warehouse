from datetime import datetime
from .utils.generator import DataGenerator
from .etl.extractor import DataExtractor
from .etl.transformer import DataTransformer
from .etl.loader import DataLoader
from .database.connection import DatabaseConnection
from .database.schema import SchemaManager


class WarehouseFacade:
    def __init__(
        self,
        db_path: str = "database/lottery_warehouse.db",
        lottery_csv: str = "data/raw/lottery_results.csv",
        revenue_csv: str = "data/raw/revenue_data.csv"
    ):
        self.db_path = db_path
        self.lottery_csv = lottery_csv
        self.revenue_csv = revenue_csv
        
        self.db_connection = None
        self.schema_manager = None
    
    def initialize_database(self):
        self.db_connection = DatabaseConnection(self.db_path)
        self.db_connection.connect()
        
        self.schema_manager = SchemaManager(self.db_connection)
        self.schema_manager.create_all_tables()
        self.schema_manager.initialize_reference_data()
        
        return self
    
    def generate_raw_data(self, start_date: str, end_date: str):
        generator = DataGenerator(self.lottery_csv, self.revenue_csv)
        lottery_df, revenue_df = generator.generate(start_date, end_date)
        
        return {
            'lottery_records': len(lottery_df),
            'revenue_records': len(revenue_df),
            'date_range': {'start': start_date, 'end': end_date}
        }
    
    def load_data_to_warehouse(self):
        if self.db_connection is None:
            raise RuntimeError("Database not initialized. Call initialize_database() first.")
        
        extractor = DataExtractor(self.lottery_csv, self.revenue_csv)
        extractor.extract()
        
        validation = extractor.validate_data()
        if not validation['valid']:
            raise ValueError(f"Data validation failed: {validation['errors']}")
        
        lottery_data = extractor.get_lottery_data()
        revenue_data = extractor.get_revenue_data()
        
        transformer = DataTransformer(lottery_data, revenue_data)
        transformer.transform_all()
        
        loader = DataLoader(self.db_connection, transformer)
        loader.load_all()
        
        return {
            'extract': {
                'lottery_records': len(lottery_data),
                'revenue_records': len(revenue_data)
            },
            'transform': transformer.get_summary(),
            'load': loader.get_load_summary()
        }
    
    def full_etl_pipeline(self, start_date: str, end_date: str):
        print("=" * 70)
        print("FULL ETL PIPELINE")
        print("=" * 70)
        
        print("\n📝 Step 1: Generate Raw Data")
        print("-" * 70)
        gen_result = self.generate_raw_data(start_date, end_date)
        print(f"✅ Generated {gen_result['lottery_records']:,} lottery records")
        print(f"✅ Generated {gen_result['revenue_records']:,} revenue records")
        
        print("\n🗄️  Step 2: Initialize Database")
        print("-" * 70)
        self.initialize_database()
        print("✅ Database schema created")
        print("✅ Reference data populated")
        
        print("\n🔄 Step 3: ETL Process")
        print("-" * 70)
        etl_result = self.load_data_to_warehouse()
        
        print(f"\n📥 Extract:")
        print(f"   - Lottery: {etl_result['extract']['lottery_records']:,} records")
        print(f"   - Revenue: {etl_result['extract']['revenue_records']:,} records")
        
        print(f"\n🔧 Transform:")
        print(f"   - Dim_Date: {etl_result['transform']['dim_date_records']:,} records")
        print(f"   - Dim_Agency: {etl_result['transform']['dim_agency_records']:,} records")
        print(f"   - Fact_Lottery: {etl_result['transform']['fact_lottery_records']:,} records")
        print(f"   - Fact_Revenue: {etl_result['transform']['fact_revenue_records']:,} records")
        
        print(f"\n💾 Load:")
        for table, count in etl_result['load']['loaded_counts'].items():
            print(f"   - {table}: {count:,} records loaded")
        print(f"   - Total: {etl_result['load']['total_loaded']:,} records")
        
        print("\n" + "=" * 70)
        print("✅ ETL PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 70)
        
        return etl_result
    
    def get_warehouse_stats(self):
        if self.db_connection is None:
            raise RuntimeError("Database not initialized.")
        
        stats = {}
        
        tables = [
            'Dim_Date', 'Dim_Station', 'Dim_Prize', 'Dim_Agency',
            'Fact_Lottery_Result', 'Fact_Revenue'
        ]
        
        for table in tables:
            result = self.db_connection.fetchone(f"SELECT COUNT(*) as cnt FROM {table}")
            stats[table] = result['cnt']
        
        return stats
    
    def close(self):
        if self.db_connection:
            self.db_connection.close()
