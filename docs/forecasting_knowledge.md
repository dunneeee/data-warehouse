# Phân tích Thuật toán Dự đoán Doanh thu

## 1. Tổng quan về Linear Regression

### 1.1 Định nghĩa
Linear Regression là thuật toán supervised learning dự đoán giá trị liên tục bằng cách tìm mối quan hệ tuyến tính giữa features (X) và target (y).

**Công thức:**
```
y = β₀ + β₁x₁ + β₂x₂ + ... + βₙxₙ + ε

Trong đó:
- y: Giá trị dự đoán (doanh thu)
- β₀: Bias term (hệ số chặn)
- β₁, β₂, ..., βₙ: Coefficients (trọng số các features)
- x₁, x₂, ..., xₙ: Features
- ε: Sai số
```

### 1.2 Phương pháp tối ưu
Sử dụng **Ordinary Least Squares (OLS)** để tìm coefficients tối ưu:

```
min Σ(yᵢ - ŷᵢ)²

Nghiệm:
β = (XᵀX)⁻¹Xᵀy
```

## 2. Features Engineering cho Doanh thu

### 2.1 Temporal Features (Đặc trưng thời gian)

#### a) Basic temporal
```python
month = 1-12           # Tháng trong năm
year = 2015-2025       # Năm
quarter = 1-4          # Quý
month_index = 0-n      # Vị trí tháng từ đầu dataset
```

**Lý do:**
- Xu hướng tăng trưởng dài hạn (year, month_index)
- Biến động theo mùa vụ (month, quarter)

#### b) Cyclic encoding
```python
sin_month = sin(2π * month / 12)
cos_month = cos(2π * month / 12)
```

**Lý do:**
- Tháng 12 và tháng 1 có quan hệ gần nhau (cyclic)
- Tránh model hiểu sai: month=12 khác xa month=1
- Sin/Cos transform giữ được tính chu kỳ

**Visualization:**
```
Month: 1  2  3  4  5  6  7  8  9  10 11 12 1
      └─────────────────────────────────┘
      Cyclic: 12 → 1 là liền kề
```

### 2.2 Lag Features (Đặc trưng trễ)

```python
revenue_lag1 = revenue tháng trước       # t-1
revenue_lag3 = revenue 3 tháng trước     # t-3  
revenue_lag6 = revenue 6 tháng trước     # t-6
```

**Lý do:**
- Doanh thu có tính tự tương quan (autocorrelation)
- Tháng hiện tại phụ thuộc vào các tháng trước
- Lag1: Xu hướng ngắn hạn
- Lag3, Lag6: Xu hướng trung/dài hạn

### 2.3 Moving Averages (Trung bình trượt)

```python
revenue_ma3 = mean(revenue[t-2:t])      # 3 tháng
revenue_ma6 = mean(revenue[t-5:t])      # 6 tháng
```

**Lý do:**
- Làm mịn nhiễu (smoothing)
- Nắm bắt xu hướng trung bình
- MA3: Xu hướng ngắn hạn
- MA6: Xu hướng dài hạn

## 3. Data Preprocessing

### 3.1 Feature Scaling với StandardScaler

```python
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_scaled = (X - mean) / std_dev
```

**Lý do:**
- Features có scale khác nhau: year (2015-2025) vs sin_month (-1 to 1)
- Gradient descent hội tụ nhanh hơn
- Coefficients có ý nghĩa tương đối

**Ví dụ:**
```
year:         [2015, 2016, ..., 2025] → μ=2020, σ=3.16
month_index:  [0, 1, 2, ..., 120]     → μ=60, σ=34.64
sin_month:    [-1, ..., 1]            → μ=0, σ=0.71

Sau scaling: tất cả features có μ=0, σ=1
```

### 3.2 Handling Missing Values

```python
df = df.fillna(method='bfill').fillna(0)
```

**Lý do:**
- Lag features tạo NaN ở đầu dataset
- Backward fill: dùng giá trị sau để điền
- Fallback: fill 0 nếu vẫn còn NaN

## 4. Model Training & Evaluation

### 4.1 Train-Test Split

```python
train_size = 80%
test_size = 20%
```

**Lý do:**
- Tránh overfitting
- Đánh giá performance trên unseen data
- Time series: không shuffle, giữ thứ tự thời gian

### 4.2 Metrics

#### a) R² Score (Coefficient of Determination)
```
R² = 1 - (SS_res / SS_tot)
   = 1 - Σ(y - ŷ)² / Σ(y - ȳ)²

Range: [0, 1] (càng cao càng tốt)
```

**Ý nghĩa:** Model giải thích được bao nhiêu % variance của data
- R² = 0.71 → Model giải thích 71% variance

#### b) MAE (Mean Absolute Error)
```
MAE = (1/n) Σ|yᵢ - ŷᵢ|

Unit: VND
```

**Ý nghĩa:** Sai số trung bình tuyệt đối
- MAE = 18 tỷ VND → Trung bình sai 18 tỷ mỗi dự đoán

#### c) RMSE (Root Mean Squared Error)
```
RMSE = √[(1/n) Σ(yᵢ - ŷᵢ)²]

Unit: VND
```

**Ý nghĩa:** Penalize lỗi lớn hơn MAE
- RMSE = 29 tỷ VND → Có outliers lớn

#### d) MAPE (Mean Absolute Percentage Error)
```
MAPE = (100/n) Σ|((yᵢ - ŷᵢ)/yᵢ)|

Unit: %
```

**Ý nghĩa:** Sai số tương đối trung bình
- MAPE = 2.99% → Sai khoảng 3%

## 5. Feature Importance Analysis

### 5.1 Linear Regression Coefficients

```python
importance = model.coef_
```

**Top features trong project:**
```
1. revenue_ma3:    +212.67 tỷ  → Xu hướng ngắn hạn mạnh nhất
2. revenue_lag1:    -70.95 tỷ  → Mean reversion effect
3. revenue_lag3:    +40.80 tỷ  → Xu hướng trung hạn
4. month_index:     -25.56 tỷ  → Trend giảm nhẹ theo thời gian
5. year:            -24.26 tỷ  → Tương quan với month_index
```

**Giải thích:**
- **revenue_ma3** cao nhất: Trung bình 3 tháng gần đây là predictor tốt nhất
- **revenue_lag1** âm: Hiện tượng mean reversion (tháng cao → tháng sau điều chỉnh)
- **month_index/year** âm: Dataset có xu hướng giảm nhẹ về cuối

## 6. Forecasting Process

### 6.1 Iterative Prediction

```python
for month in [1, 2, ..., 12]:
    # Predict tháng hiện tại
    pred = model.predict(features)
    
    # Update lags cho tháng sau
    lag1 = pred
    lag3 = predictions[month - 3]
    lag6 = predictions[month - 6]
    
    # Update MAs
    ma3 = mean(predictions[-3:])
    ma6 = mean(predictions[-6:])
```

**Lý do:**
- Dự đoán multi-step ahead
- Mỗi prediction trở thành input cho prediction tiếp theo
- Uncertainty tích lũy theo thời gian (càng xa càng không chắc)

### 6.2 Handling Edge Cases

```python
# Tháng đầu tiên
if i < 3:
    lag3 = last_historical_value

# Moving average
if len(predictions) < 3:
    ma3 = mean(predictions + last_historical_values)
```

## 7. Kết quả Thực tế

### 7.1 Model Performance
```
R² Score:  0.7130  → Tốt
MAE:       18.3 tỷ  → Chấp nhận được
MAPE:      2.99%   → Rất tốt (< 5%)
RMSE:      29.1 tỷ  → Có outliers
```

### 7.2 Dự đoán 2026
```
Tháng 1-4:  ~717-720 tỷ VND  (Cao nhất)
Tháng 5-12: Giảm dần ~666 tỷ VND
```

**Xu hướng:** Seasonality pattern - đầu năm cao, cuối năm giảm

## 8. Limitations & Improvements

### 8.1 Hạn chế của Linear Regression

1. **Assumptions:**
   - Quan hệ tuyến tính
   - Independence của residuals
   - Homoscedasticity (variance đồng nhất)

2. **Không xử lý:**
   - Non-linear patterns phức tạp
   - Sudden shocks (COVID, economic crisis)
   - External factors (marketing campaigns, competitor actions)

### 8.2 Cải tiến có thể áp dụng

#### a) Advanced Linear Models
```python
Ridge Regression       # L2 regularization, tránh overfitting
Lasso Regression      # L1 regularization, feature selection
ElasticNet            # L1 + L2 combined
```

#### b) Non-linear Models
```python
Polynomial Features   # Thêm x², x³, x₁*x₂
Decision Trees        # Non-linear relationships
Random Forest         # Ensemble, robust
XGBoost               # Gradient boosting, SOTA
```

#### c) Time Series Specific
```python
ARIMA                 # Autoregressive Integrated MA
SARIMA                # Seasonal ARIMA
Prophet               # Facebook's time series tool
LSTM/GRU              # Deep learning for sequences
```

#### d) Feature Engineering
```python
# External features
- Đài hoạt động (số lượng stations mở)
- Ngày lễ, Tết
- Economic indicators
- Weather data
- Marketing spend

# Advanced temporal
- Week of year
- Is holiday
- Days until Tet
- Season (Spring/Summer/Fall/Winter)
```

## 9. Kết luận

### 9.1 Điểm mạnh của giải pháp hiện tại
- ✅ Simple, interpretable
- ✅ Fast training & prediction
- ✅ Good performance (MAPE < 3%)
- ✅ Feature importance dễ hiểu
- ✅ Không cần nhiều data

### 9.2 Khi nào nên nâng cấp
- Dataset lớn hơn (> 5 năm)
- Cần accuracy cao hơn (MAPE < 1%)
- Có external features
- Pattern phức tạp hơn

### 9.3 Best Practices đã áp dụng
1. Feature engineering cẩn thận (lag, MA, cyclic)
2. Proper scaling (StandardScaler)
3. Train-test split đúng cách
4. Multiple metrics evaluation
5. Save/load model cho production
6. Modular, clean code architecture
