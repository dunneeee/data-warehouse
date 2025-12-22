import pandas as pd
from pathlib import Path


class DataExtractor:
    def __init__(self, lottery_csv_path: str, revenue_csv_path: str):
        self.lottery_csv_path = lottery_csv_path
        self.revenue_csv_path = revenue_csv_path
        self.lottery_data = None
        self.revenue_data = None
    
    def extract(self):
        self._extract_lottery_data()
        self._extract_revenue_data()
        return self
    
    def _extract_lottery_data(self):
        if not Path(self.lottery_csv_path).exists():
            raise FileNotFoundError(f"Lottery CSV not found: {self.lottery_csv_path}")
        
        self.lottery_data = pd.read_csv(self.lottery_csv_path)
        self.lottery_data['draw_date'] = pd.to_datetime(self.lottery_data['draw_date'])
        return self.lottery_data
    
    def _extract_revenue_data(self):
        if not Path(self.revenue_csv_path).exists():
            raise FileNotFoundError(f"Revenue CSV not found: {self.revenue_csv_path}")
        
        self.revenue_data = pd.read_csv(self.revenue_csv_path)
        self.revenue_data['sale_date'] = pd.to_datetime(self.revenue_data['sale_date'])
        return self.revenue_data
    
    def get_lottery_data(self):
        if self.lottery_data is None:
            self._extract_lottery_data()
        return self.lottery_data
    
    def get_revenue_data(self):
        if self.revenue_data is None:
            self._extract_revenue_data()
        return self.revenue_data
    
    def get_date_range(self):
        lottery_dates = self.get_lottery_data()['draw_date']
        revenue_dates = self.get_revenue_data()['sale_date']
        
        return {
            'lottery': {
                'min': lottery_dates.min(),
                'max': lottery_dates.max(),
                'count': len(lottery_dates.unique())
            },
            'revenue': {
                'min': revenue_dates.min(),
                'max': revenue_dates.max(),
                'count': len(revenue_dates.unique())
            }
        }
    
    def validate_data(self):
        errors = []
        
        lottery = self.get_lottery_data()
        if lottery.isnull().any().any():
            errors.append("Lottery data contains null values")
        
        revenue = self.get_revenue_data()
        if revenue.isnull().any().any():
            errors.append("Revenue data contains null values")
        
        required_lottery_cols = ['draw_date', 'station_name', 'prize_name', 'prize_sequence', 'result_number']
        missing_lottery_cols = [col for col in required_lottery_cols if col not in lottery.columns]
        if missing_lottery_cols:
            errors.append(f"Missing lottery columns: {missing_lottery_cols}")
        
        required_revenue_cols = ['sale_date', 'station_name', 'agency_name', 'tickets_sold', 
                                 'ticket_price', 'total_revenue', 'total_payout', 'commission', 'net_profit']
        missing_revenue_cols = [col for col in required_revenue_cols if col not in revenue.columns]
        if missing_revenue_cols:
            errors.append(f"Missing revenue columns: {missing_revenue_cols}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'lottery_records': len(lottery),
            'revenue_records': len(revenue)
        }
