import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path


class DataGenerator:
    def __init__(self, lottery_csv_path: str, revenue_csv_path: str):
        self.lottery_csv_path = lottery_csv_path
        self.revenue_csv_path = revenue_csv_path
        self._ensure_directories()
        
        self.station_schedule = {
            'Hà Nội': [0, 3],  # Thứ 2, Thứ 5
            'TP Hồ Chí Minh': [0, 5],  # Thứ 2, Thứ 7
            'Đà Nẵng': [2, 5],  # Thứ 4, Thứ 7
            'Cần Thơ': [2],  # Thứ 4
            'An Giang': [3],  # Thứ 5
            'Bình Dương': [4],  # Thứ 6
            'Đồng Nai': [2],  # Thứ 4
            'Kiên Giang': [6],  # Chủ nhật
            'Tây Ninh': [3],  # Thứ 5
            'Vũng Tàu': [1]  # Thứ 3
        }
        
        self.prizes_south = [
            {'name': 'Đặc biệt', 'quantity': 1, 'digits': 6},
            {'name': 'Nhất', 'quantity': 1, 'digits': 5},
            {'name': 'Nhì', 'quantity': 1, 'digits': 5},
            {'name': 'Ba', 'quantity': 2, 'digits': 5},
            {'name': 'Tư', 'quantity': 7, 'digits': 4},
            {'name': 'Năm', 'quantity': 1, 'digits': 4},
            {'name': 'Sáu', 'quantity': 3, 'digits': 3},
            {'name': 'Bảy', 'quantity': 1, 'digits': 2},
            {'name': 'Tám', 'quantity': 1, 'digits': 2}
        ]
        
        self.agencies = [
            {'name': 'Đại lý Trung tâm', 'type': 'Cấp 1'},
            {'name': 'Đại lý Quận 1', 'type': 'Cấp 1'},
            {'name': 'Đại lý Quận 5', 'type': 'Cấp 2'},
            {'name': 'Đại lý Thủ Đức', 'type': 'Cấp 1'},
            {'name': 'Đại lý Bình Thạnh', 'type': 'Cấp 2'},
            {'name': 'Đại lý Tân Bình', 'type': 'Cấp 2'},
            {'name': 'Đại lý Gò Vấp', 'type': 'Cấp 2'},
            {'name': 'Đại lý Phú Nhuận', 'type': 'Cấp 2'}
        ]
    
    def _ensure_directories(self):
        Path(self.lottery_csv_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.revenue_csv_path).parent.mkdir(parents=True, exist_ok=True)
    
    def generate(self, start_date: str, end_date: str):
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        lottery_data = self._generate_lottery_results(start, end)
        revenue_data = self._generate_revenue(start, end)
        
        lottery_df = pd.DataFrame(lottery_data)
        revenue_df = pd.DataFrame(revenue_data)
        
        lottery_df.to_csv(self.lottery_csv_path, index=False)
        revenue_df.to_csv(self.revenue_csv_path, index=False)
        
        return lottery_df, revenue_df
    
    def _generate_lottery_results(self, start_date: datetime, end_date: datetime):
        data = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            day_of_week = current_date.weekday()
            
            for station_name, schedule_days in self.station_schedule.items():
                if day_of_week in schedule_days:
                    for prize_info in self.prizes_south:
                        for seq in range(1, prize_info['quantity'] + 1):
                            max_number = 10 ** prize_info['digits'] - 1
                            result_number = f"{random.randint(0, max_number):0{prize_info['digits']}d}"
                            
                            data.append({
                                'draw_date': date_str,
                                'station_name': station_name,
                                'prize_name': prize_info['name'],
                                'prize_sequence': seq,
                                'result_number': result_number
                            })
            
            current_date += timedelta(days=1)
        
        return data
    
    def _generate_revenue(self, start_date: datetime, end_date: datetime):
        data = []
        current_date = start_date
        base_tickets = 15000
        trend_factor = 0
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            day_of_week = current_date.weekday()
            is_weekend = 1 if day_of_week >= 5 else 0
            
            weekend_multiplier = 1.4 if is_weekend else 1.0
            
            seasonal_factor = 1 + 0.2 * random.random()
            trend_factor += 0.001
            
            days_from_start = (current_date - start_date).days
            cycle = 1 + 0.15 * (1 + (days_from_start % 30) / 30)
            
            has_lottery_today = any(day_of_week in schedule for schedule in self.station_schedule.values())
            lottery_multiplier = 1.3 if has_lottery_today else 1.0
            
            stations_with_draws = [s for s, sched in self.station_schedule.items() if day_of_week in sched]
            active_stations = stations_with_draws if stations_with_draws else random.sample(list(self.station_schedule.keys()), k=random.randint(3, 5))
            
            for station_name in active_stations:
                station_factor = random.uniform(0.8, 1.2)
                station_draw_bonus = 1.5 if station_name in stations_with_draws else 1.0
                
                num_agencies = random.randint(2, 4)
                selected_agencies = random.sample(self.agencies, k=num_agencies)
                
                for agency in selected_agencies:
                    tickets_sold = int(
                        base_tickets * 
                        weekend_multiplier * 
                        seasonal_factor * 
                        (1 + trend_factor) *
                        cycle *
                        station_factor *
                        lottery_multiplier *
                        station_draw_bonus *
                        random.uniform(0.85, 1.15)
                    )
                    
                    ticket_price = 10000
                    total_revenue = tickets_sold * ticket_price
                    
                    win_rate = random.uniform(0.45, 0.55)
                    total_payout = total_revenue * win_rate
                    
                    commission_rate = 0.08 if agency['type'] == 'Cấp 1' else 0.06
                    commission = total_revenue * commission_rate
                    
                    net_profit = total_revenue - total_payout - commission
                    
                    data.append({
                        'sale_date': date_str,
                        'station_name': station_name,
                        'agency_name': agency['name'],
                        'agency_type': agency['type'],
                        'tickets_sold': tickets_sold,
                        'ticket_price': ticket_price,
                        'total_revenue': round(total_revenue, 2),
                        'total_payout': round(total_payout, 2),
                        'commission': round(commission, 2),
                        'net_profit': round(net_profit, 2)
                    })
            
            current_date += timedelta(days=1)
        
        return data
    
    def get_summary(self):
        try:
            lottery_df = pd.read_csv(self.lottery_csv_path)
            revenue_df = pd.read_csv(self.revenue_csv_path)
            
            return {
                'lottery_records': len(lottery_df),
                'revenue_records': len(revenue_df),
                'date_range': {
                    'lottery': {
                        'start': lottery_df['draw_date'].min(),
                        'end': lottery_df['draw_date'].max()
                    },
                    'revenue': {
                        'start': revenue_df['sale_date'].min(),
                        'end': revenue_df['sale_date'].max()
                    }
                },
                'total_revenue': revenue_df['total_revenue'].sum(),
                'total_tickets': revenue_df['tickets_sold'].sum()
            }
        except FileNotFoundError:
            return None
