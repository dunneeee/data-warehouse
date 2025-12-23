# Hướng Dẫn Generate Dữ Liệu

## Tổng Quan

Module `DataGenerator` trong `src/utils/generator.py` được thiết kế để tạo dữ liệu mô phỏng cho hệ thống kho dữ liệu xổ số. Module này tạo ra hai loại dữ liệu chính:
1. **Kết quả xổ số** (Lottery Results)
2. **Dữ liệu doanh thu** (Revenue Data)

## Cách Sử Dụng

### Khởi Tạo

```python
from src.utils.generator import DataGenerator

# Khởi tạo generator với đường dẫn file CSV
generator = DataGenerator(
    lottery_csv_path='data/raw/lottery_results.csv',
    revenue_csv_path='data/raw/revenue_data.csv'
)
```

### Generate Dữ Liệu

```python
# Generate dữ liệu từ ngày bắt đầu đến ngày kết thúc
lottery_df, revenue_df = generator.generate(
    start_date='2024-01-01',
    end_date='2024-12-31'
)
```

### Xem Tóm Tắt

```python
# Lấy thông tin tóm tắt về dữ liệu đã generate
summary = generator.get_summary()
print(summary)
```

## Cấu Trúc Dữ Liệu

### 1. Dữ Liệu Kết Quả Xổ Số

Mỗi bản ghi kết quả xổ số bao gồm các trường:

| Trường | Kiểu | Mô Tả |
|--------|------|-------|
| `draw_date` | string | Ngày quay số (YYYY-MM-DD) |
| `station_name` | string | Tên đài xổ số |
| `prize_name` | string | Tên giải thưởng |
| `prize_sequence` | int | Số thứ tự giải (nếu có nhiều giải cùng loại) |
| `result_number` | string | Số trúng thưởng |

### 2. Dữ Liệu Doanh Thu

Mỗi bản ghi doanh thu bao gồm các trường:

| Trường | Kiểu | Mô Tả |
|--------|------|-------|
| `sale_date` | string | Ngày bán (YYYY-MM-DD) |
| `station_name` | string | Tên đài xổ số |
| `agency_name` | string | Tên đại lý |
| `agency_type` | string | Loại đại lý (Cấp 1 hoặc Cấp 2) |
| `tickets_sold` | int | Số vé đã bán |
| `ticket_price` | int | Giá vé (10,000 VNĐ) |
| `total_revenue` | float | Tổng doanh thu |
| `total_payout` | float | Tổng tiền trả thưởng |
| `commission` | float | Hoa hồng đại lý |
| `net_profit` | float | Lợi nhuận ròng |

## Lịch Quay Số Các Đài

Generator mô phỏng lịch quay số thực tế của các đài xổ số tại Việt Nam:

| Đài | Ngày Quay | Mã Ngày |
|-----|-----------|---------|
| Hà Nội | Thứ 2, Thứ 5 | 0, 3 |
| TP Hồ Chí Minh | Thứ 2, Thứ 7 | 0, 5 |
| Đà Nẵng | Thứ 4, Thứ 7 | 2, 5 |
| Cần Thơ | Thứ 4 | 2 |
| An Giang | Thứ 5 | 3 |
| Bình Dương | Thứ 6 | 4 |
| Đồng Nai | Thứ 4 | 2 |
| Kiên Giang | Chủ nhật | 6 |
| Tây Ninh | Thứ 5 | 3 |
| Vũng Tàu | Thứ 3 | 1 |

*Lưu ý: 0 = Thứ 2, 1 = Thứ 3, ..., 6 = Chủ nhật*

## Cấu Trúc Giải Thưởng

Generator sử dụng cấu trúc giải thưởng miền Nam:

| Giải | Số Lượng | Số Chữ Số |
|------|----------|-----------|
| Đặc biệt | 1 | 6 |
| Nhất | 1 | 5 |
| Nhì | 1 | 5 |
| Ba | 2 | 5 |
| Tư | 7 | 4 |
| Năm | 1 | 4 |
| Sáu | 3 | 3 |
| Bảy | 1 | 2 |
| Tám | 1 | 2 |

**Tổng cộng: 18 giải mỗi kỳ quay**

## Các Đại Lý Mô Phỏng

Hệ thống bao gồm 8 đại lý:

### Đại Lý Cấp 1 (Hoa hồng 8%)
- Đại lý Trung tâm
- Đại lý Quận 1
- Đại lý Thủ Đức

### Đại Lý Cấp 2 (Hoa hồng 6%)
- Đại lý Quận 5
- Đại lý Bình Thạnh
- Đại lý Tân Bình
- Đại lý Gò Vấp
- Đại lý Phú Nhuận

## Các Yếu Tố Ảnh Hưởng Doanh Thu

Generator mô phỏng nhiều yếu tố thực tế ảnh hưởng đến doanh số bán vé:

### 1. **Yếu Tố Cuối Tuần (Weekend Multiplier)**
- Tăng 40% doanh số vào cuối tuần (Thứ 7, Chủ nhật)
- `weekend_multiplier = 1.4` nếu là cuối tuần, ngược lại `1.0`

### 2. **Yếu Tố Mùa Vụ (Seasonal Factor)**
- Biến động ngẫu nhiên từ 1.0 đến 1.2
- Mô phỏng sự thay đổi theo mùa hoặc sự kiện đặc biệt
- `seasonal_factor = 1 + 0.2 * random()`

### 3. **Xu Hướng Tăng Trưởng (Trend Factor)**
- Tăng 0.1% mỗi ngày
- Mô phỏng xu hướng phát triển của thị trường
- `trend_factor += 0.001` mỗi ngày

### 4. **Chu Kỳ Tháng (Monthly Cycle)**
- Biến động theo chu kỳ 30 ngày
- Tăng từ 0% đến 15% trong mỗi chu kỳ
- `cycle = 1 + 0.15 * (1 + (days_from_start % 30) / 30)`

### 5. **Yếu Tố Ngày Quay Số (Lottery Day Multiplier)**
- Tăng 30% doanh số trong ngày có quay số
- `lottery_multiplier = 1.3` nếu có quay số, ngược lại `1.0`

### 6. **Yếu Tố Đài Quay Số (Station Draw Bonus)**
- Tăng 50% doanh số cho đài có quay số trong ngày
- `station_draw_bonus = 1.5` cho đài có quay, ngược lại `1.0`

### 7. **Yếu Tố Đài (Station Factor)**
- Biến động ngẫu nhiên từ 0.8 đến 1.2 cho mỗi đài
- Mô phỏng sự khác biệt về quy mô và phổ biến của từng đài

### 8. **Biến Động Ngẫu Nhiên (Random Variance)**
- Biến động ±15% cho mỗi giao dịch
- `random.uniform(0.85, 1.15)`

## Công Thức Tính Toán

### Số Vé Bán Ra

```python
tickets_sold = int(
    base_tickets *           # 15,000 vé cơ sở
    weekend_multiplier *     # x1.4 nếu cuối tuần
    seasonal_factor *        # x(1.0-1.2)
    (1 + trend_factor) *     # x(1.0+trend)
    cycle *                  # x(1.0-1.15)
    station_factor *         # x(0.8-1.2)
    lottery_multiplier *     # x1.3 nếu có quay số
    station_draw_bonus *     # x1.5 nếu đài quay số
    random.uniform(0.85, 1.15)  # x(0.85-1.15)
)
```

### Doanh Thu và Lợi Nhuận

```python
# Doanh thu
total_revenue = tickets_sold * ticket_price  # ticket_price = 10,000 VNĐ

# Tiền trả thưởng (45-55% doanh thu)
win_rate = random.uniform(0.45, 0.55)
total_payout = total_revenue * win_rate

# Hoa hồng đại lý
commission_rate = 0.08 if agency_type == 'Cấp 1' else 0.06
commission = total_revenue * commission_rate

# Lợi nhuận ròng
net_profit = total_revenue - total_payout - commission
```

## Ví Dụ Sử Dụng

### Ví Dụ 1: Generate Dữ Liệu 1 Năm

```python
from src.utils.generator import DataGenerator

# Khởi tạo
generator = DataGenerator(
    lottery_csv_path='data/raw/lottery_results.csv',
    revenue_csv_path='data/raw/revenue_data.csv'
)

# Generate dữ liệu năm 2024
lottery_df, revenue_df = generator.generate(
    start_date='2024-01-01',
    end_date='2024-12-31'
)

print(f"Đã tạo {len(lottery_df)} bản ghi kết quả xổ số")
print(f"Đã tạo {len(revenue_df)} bản ghi doanh thu")
```

### Ví Dụ 2: Generate và Phân Tích

```python
# Generate dữ liệu
lottery_df, revenue_df = generator.generate('2024-01-01', '2024-03-31')

# Phân tích dữ liệu đã tạo
print("\n=== PHÂN TÍCH KẾT QUẢ XỔ SỐ ===")
print(f"Tổng số kỳ quay: {lottery_df['draw_date'].nunique()}")
print(f"Số đài tham gia: {lottery_df['station_name'].nunique()}")
print(f"Tổng số giải: {len(lottery_df)}")

print("\n=== PHÂN TÍCH DOANH THU ===")
print(f"Tổng doanh thu: {revenue_df['total_revenue'].sum():,.0f} VNĐ")
print(f"Tổng vé bán: {revenue_df['tickets_sold'].sum():,}")
print(f"Doanh thu trung bình/ngày: {revenue_df.groupby('sale_date')['total_revenue'].sum().mean():,.0f} VNĐ")
```

### Ví Dụ 3: Xem Tóm Tắt

```python
# Xem tóm tắt dữ liệu đã generate
summary = generator.get_summary()

if summary:
    print(f"Số bản ghi xổ số: {summary['lottery_records']:,}")
    print(f"Số bản ghi doanh thu: {summary['revenue_records']:,}")
    print(f"Tổng doanh thu: {summary['total_revenue']:,.0f} VNĐ")
    print(f"Tổng số vé: {summary['total_tickets']:,}")
    print(f"Khoảng thời gian xổ số: {summary['date_range']['lottery']['start']} đến {summary['date_range']['lottery']['end']}")
else:
    print("Chưa có dữ liệu")
```

## Lưu Ý Quan Trọng

### 1. **Dữ Liệu Mô Phỏng**
- Dữ liệu được tạo ra hoàn toàn ngẫu nhiên cho mục đích học tập và thử nghiệm
- Không phản ánh số liệu thực tế của bất kỳ đài xổ số nào
- Các con số và tỷ lệ được thiết kế để mô phỏng xu hướng thực tế

### 2. **Hiệu Suất**
- Generate dữ liệu cho khoảng thời gian dài có thể mất thời gian
- Với 1 năm dữ liệu, có thể tạo ra:
  - Khoảng 65,000-70,000 bản ghi kết quả xổ số
  - Khoảng 40,000-50,000 bản ghi doanh thu

### 3. **Thư Mục Tự Động**
- Generator tự động tạo thư mục nếu chưa tồn tại
- Đảm bảo không có lỗi khi thư mục `data/raw/` chưa được tạo

### 4. **Ghi Đè Dữ Liệu**
- Mỗi lần chạy `generate()` sẽ **ghi đè** file CSV cũ
- Cần backup dữ liệu quan trọng trước khi generate lại

## Tích Hợp Với Hệ Thống

Sau khi generate, dữ liệu có thể được:

1. **Load vào Database** qua ETL pipeline
2. **Phân tích** bằng các module trong `src/analysis/`
3. **Dự báo** bằng module `src/forecasting/`
4. **Hiển thị** trên Dashboard UI

Xem thêm tài liệu:
- [Cross Correlation Analysis](cross_correlation_analysis.md)
- [Forecasting Knowledge](forecasting_knowledge.md)
- [ERD Mermaid](erd_mermaid.mermaid)
