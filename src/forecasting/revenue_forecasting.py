from typing import Dict, Tuple
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

from .strategy import ForecastingStrategy


class RevenueForecasting(ForecastingStrategy):
    
    def __init__(self):
        super().__init__("Revenue Forecasting - Linear Regression")
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        self.feature_names = []
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['year_month'] = pd.to_datetime(df['year_month'])
        df = df.sort_values('year_month')
        
        df['month'] = df['year_month'].dt.month
        df['year'] = df['year_month'].dt.year
        df['quarter'] = df['year_month'].dt.quarter
        df['month_index'] = range(len(df))
        
        df['sin_month'] = np.sin(2 * np.pi * df['month'] / 12)
        df['cos_month'] = np.cos(2 * np.pi * df['month'] / 12)
        
        if len(df) > 1:
            df['revenue_lag1'] = df['total_revenue'].shift(1)
            df['revenue_lag3'] = df['total_revenue'].shift(3)
            df['revenue_lag6'] = df['total_revenue'].shift(6)
            df['revenue_ma3'] = df['total_revenue'].rolling(window=3, min_periods=1).mean()
            df['revenue_ma6'] = df['total_revenue'].rolling(window=6, min_periods=1).mean()
        
        df = df.fillna(method='bfill').fillna(0)
        
        return df
    
    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> 'RevenueForecasting':
        self.feature_names = X_train.columns.tolist()
        X_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_scaled, y_train)
        self.is_trained = True
        return self
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_trained:
            raise ValueError("Model chưa được huấn luyện")
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
        y_pred = self.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
        
        self.metrics = {
            'MAE': mae,
            'RMSE': rmse,
            'R2': r2,
            'MAPE': mape
        }
        return self.metrics
    
    def get_feature_importance(self) -> pd.DataFrame:
        if not self.is_trained:
            return None
        
        importance = pd.DataFrame({
            'feature': self.feature_names,
            'coefficient': self.model.coef_
        })
        importance['abs_coefficient'] = importance['coefficient'].abs()
        importance = importance.sort_values('abs_coefficient', ascending=False)
        return importance
    
    def forecast_next_months(self, historical_data: pd.DataFrame, months: int = 12) -> pd.DataFrame:
        if not self.is_trained:
            raise ValueError("Model chưa được huấn luyện")
        
        df = self.prepare_features(historical_data)
        
        last_date = df['year_month'].max()
        last_revenue = df['total_revenue'].iloc[-1]
        last_index = df['month_index'].iloc[-1]
        
        future_dates = pd.date_range(
            start=last_date + pd.DateOffset(months=1),
            periods=months,
            freq='MS'
        )
        
        predictions = []
        current_lags = {
            'lag1': df['total_revenue'].iloc[-1],
            'lag3': df['total_revenue'].iloc[-3] if len(df) >= 3 else last_revenue,
            'lag6': df['total_revenue'].iloc[-6] if len(df) >= 6 else last_revenue,
            'ma3': df['total_revenue'].iloc[-3:].mean() if len(df) >= 3 else last_revenue,
            'ma6': df['total_revenue'].iloc[-6:].mean() if len(df) >= 6 else last_revenue
        }
        
        for i, date in enumerate(future_dates):
            month_idx = last_index + i + 1
            month = date.month
            year = date.year
            quarter = (month - 1) // 3 + 1
            
            features = {
                'month': month,
                'year': year,
                'quarter': quarter,
                'month_index': month_idx,
                'sin_month': np.sin(2 * np.pi * month / 12),
                'cos_month': np.cos(2 * np.pi * month / 12),
                'revenue_lag1': current_lags['lag1'],
                'revenue_lag3': current_lags['lag3'],
                'revenue_lag6': current_lags['lag6'],
                'revenue_ma3': current_lags['ma3'],
                'revenue_ma6': current_lags['ma6']
            }
            
            X_future = pd.DataFrame([features])[self.feature_names]
            pred = self.predict(X_future)[0]
            
            predictions.append({
                'year_month': date.strftime('%Y-%m'),
                'predicted_revenue': max(0, pred)
            })
            
            current_lags['lag1'] = pred
            if i >= 2:
                current_lags['lag3'] = predictions[i-2]['predicted_revenue']
            if i >= 5:
                current_lags['lag6'] = predictions[i-5]['predicted_revenue']
            
            recent_preds = [p['predicted_revenue'] for p in predictions[-3:]]
            current_lags['ma3'] = np.mean(recent_preds)
            recent_preds_6 = [p['predicted_revenue'] for p in predictions[-6:]]
            current_lags['ma6'] = np.mean(recent_preds_6)
        
        return pd.DataFrame(predictions)


def train_revenue_model(db_connection) -> Tuple[RevenueForecasting, pd.DataFrame]:
    from src.analysis.revenue import RevenueAnalysis
    
    revenue_analysis = RevenueAnalysis(db_connection)
    df = revenue_analysis.get_monthly_revenue_summary()
    
    if df.empty:
        raise ValueError("Không có dữ liệu để train")
    
    forecaster = RevenueForecasting()
    df_features = forecaster.prepare_features(df)
    
    feature_cols = ['month', 'year', 'quarter', 'month_index', 
                   'sin_month', 'cos_month', 'revenue_lag1', 
                   'revenue_lag3', 'revenue_lag6', 'revenue_ma3', 'revenue_ma6']
    
    train_size = int(len(df_features) * 0.8)
    train_data = df_features.iloc[:train_size]
    test_data = df_features.iloc[train_size:]
    
    X_train = train_data[feature_cols]
    y_train = train_data['total_revenue']
    X_test = test_data[feature_cols]
    y_test = test_data['total_revenue']
    
    forecaster.fit(X_train, y_train)
    metrics = forecaster.evaluate(X_test, y_test)
    
    forecast_12m = forecaster.forecast_next_months(df, months=12)
    
    return forecaster, forecast_12m
