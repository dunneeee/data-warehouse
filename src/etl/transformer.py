import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple


class DataTransformer:
    def __init__(self, lottery_df: pd.DataFrame, revenue_df: pd.DataFrame):
        self.lottery_df = lottery_df.copy()
        self.revenue_df = revenue_df.copy()
        
        self.dim_date = None
        self.dim_agency = None
        self.fact_lottery = None
        self.fact_revenue = None
    
    def transform_all(self):
        self._transform_dim_date()
        self._transform_dim_agency()
        self._transform_fact_lottery()
        self._transform_fact_revenue()
        return self
    
    def _transform_dim_date(self):
        all_dates = pd.concat([
            self.lottery_df['draw_date'],
            self.revenue_df['sale_date']
        ]).unique()
        
        dates_list = []
        for date in sorted(all_dates):
            dt = pd.to_datetime(date)
            date_id = int(dt.strftime('%Y%m%d'))
            
            dates_list.append({
                'date_id': date_id,
                'full_date': dt.strftime('%Y-%m-%d'),
                'day': dt.day,
                'month': dt.month,
                'year': dt.year,
                'quarter': (dt.month - 1) // 3 + 1,
                'day_of_week': dt.strftime('%A'),
                'is_weekend': 1 if dt.weekday() >= 5 else 0,
                'is_month_start': 1 if dt.day == 1 else 0,
                'is_month_end': 1 if dt.day == dt.days_in_month else 0
            })
        
        self.dim_date = pd.DataFrame(dates_list)
        return self.dim_date
    
    def _transform_dim_agency(self):
        agencies = self.revenue_df[['agency_name', 'agency_type']].drop_duplicates()
        agencies = agencies.sort_values('agency_name').reset_index(drop=True)
        self.dim_agency = agencies
        return self.dim_agency
    
    def _transform_fact_lottery(self):
        fact_data = self.lottery_df.copy()
        
        fact_data['date_id'] = pd.to_datetime(fact_data['draw_date']).dt.strftime('%Y%m%d').astype(int)
        
        fact_lottery = fact_data[[
            'date_id',
            'station_name',
            'prize_name',
            'prize_sequence',
            'result_number'
        ]].copy()
        
        self.fact_lottery = fact_lottery
        return self.fact_lottery
    
    def _transform_fact_revenue(self):
        fact_data = self.revenue_df.copy()
        
        fact_data['date_id'] = pd.to_datetime(fact_data['sale_date']).dt.strftime('%Y%m%d').astype(int)
        
        fact_revenue = fact_data[[
            'date_id',
            'station_name',
            'agency_name',
            'tickets_sold',
            'ticket_price',
            'total_revenue',
            'total_payout',
            'net_profit',
            'commission'
        ]].copy()
        
        self.fact_revenue = fact_revenue
        return self.fact_revenue
    
    def get_dim_date(self) -> pd.DataFrame:
        if self.dim_date is None:
            self._transform_dim_date()
        return self.dim_date
    
    def get_dim_agency(self) -> pd.DataFrame:
        if self.dim_agency is None:
            self._transform_dim_agency()
        return self.dim_agency
    
    def get_fact_lottery(self) -> pd.DataFrame:
        if self.fact_lottery is None:
            self._transform_fact_lottery()
        return self.fact_lottery
    
    def get_fact_revenue(self) -> pd.DataFrame:
        if self.fact_revenue is None:
            self._transform_fact_revenue()
        return self.fact_revenue
    
    def get_summary(self) -> Dict:
        return {
            'dim_date_records': len(self.get_dim_date()),
            'dim_agency_records': len(self.get_dim_agency()),
            'fact_lottery_records': len(self.get_fact_lottery()),
            'fact_revenue_records': len(self.get_fact_revenue()),
            'date_range': {
                'start': self.dim_date['full_date'].min(),
                'end': self.dim_date['full_date'].max()
            }
        }
