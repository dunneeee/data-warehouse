import pandas as pd
from typing import Dict
from .transformer import DataTransformer
from ..database.connection import DatabaseConnection


class DataLoader:
    def __init__(self, db_connection: DatabaseConnection, transformer: DataTransformer):
        self.db = db_connection
        self.transformer = transformer
        self.loaded_counts = {}
    
    def load_all(self):
        self._load_dim_date()
        self._load_dim_agency()
        self._load_fact_lottery()
        self._load_fact_revenue()
        return self
    
    def _load_dim_date(self):
        dim_date = self.transformer.get_dim_date()
        
        existing_dates = self.db.fetchall("SELECT date_id FROM Dim_Date")
        existing_ids = {row['date_id'] for row in existing_dates}
        
        new_records = dim_date[~dim_date['date_id'].isin(existing_ids)]
        
        if len(new_records) > 0:
            query = """
            INSERT INTO Dim_Date (date_id, full_date, day, month, year, quarter, 
                                   day_of_week, is_weekend, is_month_start, is_month_end)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            records = [tuple(row) for row in new_records.values]
            self.db.executemany(query, records)
        
        self.loaded_counts['dim_date'] = len(new_records)
        return len(new_records)
    
    def _load_dim_agency(self):
        dim_agency = self.transformer.get_dim_agency()
        
        existing_agencies = self.db.fetchall("SELECT agency_name FROM Dim_Agency")
        existing_names = {row['agency_name'] for row in existing_agencies}
        
        new_records = dim_agency[~dim_agency['agency_name'].isin(existing_names)]
        
        if len(new_records) > 0:
            query = "INSERT INTO Dim_Agency (agency_name, agency_type) VALUES (?, ?)"
            records = [tuple(row) for row in new_records.values]
            self.db.executemany(query, records)
        
        self.loaded_counts['dim_agency'] = len(new_records)
        return len(new_records)
    
    def _load_fact_lottery(self):
        fact_lottery = self.transformer.get_fact_lottery()
        
        station_map = self._get_station_id_map()
        prize_map = self._get_prize_id_map()
        
        records = []
        for _, row in fact_lottery.iterrows():
            station_id = station_map.get(row['station_name'])
            prize_id = prize_map.get(row['prize_name'])
            
            if station_id and prize_id:
                records.append((
                    row['date_id'],
                    station_id,
                    prize_id,
                    row['prize_sequence'],
                    row['result_number']
                ))
        
        if len(records) > 0:
            query = """
            INSERT INTO Fact_Lottery_Result (date_id, station_id, prize_id, prize_sequence, result_number)
            VALUES (?, ?, ?, ?, ?)
            """
            self.db.executemany(query, records)
        
        self.loaded_counts['fact_lottery'] = len(records)
        return len(records)
    
    def _load_fact_revenue(self):
        fact_revenue = self.transformer.get_fact_revenue()
        
        station_map = self._get_station_id_map()
        agency_map = self._get_agency_id_map()
        
        records = []
        for _, row in fact_revenue.iterrows():
            station_id = station_map.get(row['station_name'])
            agency_id = agency_map.get(row['agency_name'])
            
            if station_id and agency_id:
                records.append((
                    row['date_id'],
                    station_id,
                    agency_id,
                    row['tickets_sold'],
                    row['ticket_price'],
                    row['total_revenue'],
                    row['total_payout'],
                    row['net_profit'],
                    row['commission']
                ))
        
        if len(records) > 0:
            query = """
            INSERT INTO Fact_Revenue (date_id, station_id, agency_id, tickets_sold, ticket_price,
                                       total_revenue, total_payout, net_profit, commission)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.db.executemany(query, records)
        
        self.loaded_counts['fact_revenue'] = len(records)
        return len(records)
    
    def _get_station_id_map(self) -> Dict[str, int]:
        stations = self.db.fetchall("SELECT station_id, station_name FROM Dim_Station")
        return {row['station_name']: row['station_id'] for row in stations}
    
    def _get_prize_id_map(self) -> Dict[str, int]:
        prizes = self.db.fetchall("SELECT prize_id, prize_name FROM Dim_Prize")
        return {row['prize_name']: row['prize_id'] for row in prizes}
    
    def _get_agency_id_map(self) -> Dict[str, int]:
        agencies = self.db.fetchall("SELECT agency_id, agency_name FROM Dim_Agency")
        return {row['agency_name']: row['agency_id'] for row in agencies}
    
    def get_load_summary(self) -> Dict:
        return {
            'loaded_counts': self.loaded_counts,
            'total_loaded': sum(self.loaded_counts.values())
        }
