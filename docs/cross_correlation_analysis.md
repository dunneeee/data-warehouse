# Cross-Correlation Analysis: Lottery Numbers vs Revenue

## 1. Giả thuyết nghiên cứu

**Câu hỏi:** Kết quả xổ số ngày T có ảnh hưởng đến doanh thu bán vé ngày T+1?

**Giả thuyết:** Khi một số xuất hiện trong kết quả xổ số (đặc biệt là giải đặc biệt), người chơi có xu hướng mua vé với số đó hoặc các số liên quan vào ngày hôm sau, dẫn đến tăng doanh thu.

**Ví dụ thực tế:**
- Ngày 1: Giải đặc biệt về số **68**
- Ngày 2: Người chơi đổ xô mua vé có số 68, 86, 6x, x8 → doanh thu tăng

## 2. SQL Query Analysis

### 2.1 Query Structure

```sql
SELECT 
    SUBSTR(lr.result_number, -2) as last_two_digits,
    COUNT(DISTINCT d1.full_date) as occurrence_count,
    AVG(r.total_revenue) as avg_next_day_revenue,
    SUM(r.total_revenue) as total_next_day_revenue,
    MIN(r.total_revenue) as min_next_day_revenue,
    MAX(r.total_revenue) as max_next_day_revenue
FROM Fact_Lottery_Result lr
JOIN Dim_Date d1 ON lr.date_id = d1.date_id
JOIN Dim_Date d2 ON d2.full_date = DATE(d1.full_date, '+1 day')
JOIN Fact_Revenue r ON r.date_id = d2.date_id
WHERE lr.result_number IS NOT NULL 
AND LENGTH(lr.result_number) >= 2
GROUP BY last_two_digits
HAVING COUNT(DISTINCT d1.full_date) >= 3
ORDER BY avg_next_day_revenue DESC
```

### 2.2 Query Breakdown

#### Step 1: Extract 2-digit numbers
```sql
SUBSTR(lr.result_number, -2) as last_two_digits
```
- Lấy 2 chữ số cuối của kết quả xổ số
- Ví dụ: `123456` → `56`, `000768` → `68`
- Phạm vi: 00-99 (100 số khác nhau)

#### Step 2: Time series join (Day T → Day T+1)
```sql
JOIN Dim_Date d1 ON lr.date_id = d1.date_id          -- Ngày T (lottery)
JOIN Dim_Date d2 ON d2.full_date = DATE(d1.full_date, '+1 day')  -- Ngày T+1
JOIN Fact_Revenue r ON r.date_id = d2.date_id         -- Revenue ngày T+1
```

**Visualization:**
```
Timeline:
Day T    Day T+1
  |        |
  v        v
[Lottery] [Revenue]
  68   →  Increased?
```

#### Step 3: Aggregation metrics
```sql
COUNT(DISTINCT d1.full_date) as occurrence_count    -- Số lần số xuất hiện
AVG(r.total_revenue) as avg_next_day_revenue        -- Doanh thu TB ngày sau
SUM(r.total_revenue) as total_next_day_revenue      -- Tổng doanh thu
MIN/MAX(r.total_revenue)                            -- Range analysis
```

#### Step 4: Filtering & Sorting
```sql
WHERE lr.result_number IS NOT NULL 
AND LENGTH(lr.result_number) >= 2    -- Valid numbers only
GROUP BY last_two_digits
HAVING COUNT(DISTINCT d1.full_date) >= 3  -- Statistical significance (n≥3)
ORDER BY avg_next_day_revenue DESC        -- Highest impact first
```

## 3. Statistical Concepts

### 3.1 Cross-Correlation

**Definition:** Cross-correlation đo lường mối quan hệ giữa hai time series với time lag.

```
Corr(X_t, Y_{t+k})

Trong đó:
- X_t: Kết quả xổ số tại thời điểm t
- Y_{t+k}: Doanh thu tại thời điểm t+k
- k=1: Lag 1 day (ngày hôm sau)
```

### 3.2 Interpretation

**High avg_next_day_revenue:**
- Correlation dương: Số này xuất hiện → doanh thu ngày sau cao
- Possible reasons:
  * Lucky number belief (số may mắn)
  * Gambler's fallacy (số hot tiếp tục hot)
  * Social influence (người khác mua → mình cũng mua)

**Low avg_next_day_revenue:**
- Correlation thấp hoặc âm: Không có ảnh hưởng rõ rệt
- Possible reasons:
  * Số không phổ biến
  * Superstition (số xui)
  * Random variation

### 3.3 Minimum Sample Size

```sql
HAVING COUNT(DISTINCT d1.full_date) >= 3
```

**Rationale:**
- n < 3: Không đủ để kết luận (outlier/noise)
- n ≥ 3: Basic statistical validity
- Optimal: n ≥ 10 cho confidence cao

## 4. Visualization Design

### 4.1 Bar Chart Structure

```
Horizontal Bar Chart:
┌────────────────────────────────────┐
│ 68 ████████████████████ 720B       │ ← Highest impact
│ 86 ███████████████████ 715B        │
│ 28 ██████████████████ 710B         │
│ 13 █████████████████ 705B          │
│ ...                                │
│ 04 ██████ 550B                     │ ← Lowest impact
└────────────────────────────────────┘
  Doanh thu TB ngày sau (VND)
```

**Design choices:**
- **Horizontal bars:** Dễ đọc số (00-99) trên trục Y
- **Sort descending:** Highest impact ở trên cùng
- **Color gradient:** Blues scheme (càng đậm = impact càng cao)
- **Top 20 only:** Tránh chart quá đông

### 4.2 Metrics Panel

```
┌─────────────────────────┐
│ Tổng số phân tích: 87   │
├─────────────────────────┤
│ Số impact cao nhất:     │
│    68 → 720B VND        │
├─────────────────────────┤
│ Số impact thấp nhất:    │
│    04 → 550B VND        │
├─────────────────────────┤
│ Top 10 Table            │
│ ┌────┬──────┬─────────┐ │
│ │ Số │ Lần  │ Doanh thu│ │
│ ├────┼──────┼─────────┤ │
│ │ 68 │  45  │ 720B    │ │
│ │ 86 │  42  │ 715B    │ │
│ └────┴──────┴─────────┘ │
└─────────────────────────┘
```

## 5. Interpretation Examples

### 5.1 Strong Positive Correlation

**Scenario:** Số 68 xuất hiện 45 lần, avg revenue = 720B VND

**Analysis:**
```
Sample size: 45 (Good!)
Baseline average revenue: 600B VND
Impact: +120B VND (+20%)

Conclusion: Số 68 có ảnh hưởng mạnh đến doanh thu ngày sau
```

**Possible explanations:**
1. Superstition: 68 = "lộc phát" (phát tài)
2. Hot number effect: Người chơi tin số sẽ tiếp tục ra
3. Marketing: Đại lý quảng cáo số này

### 5.2 Weak/No Correlation

**Scenario:** Số 04 xuất hiện 30 lần, avg revenue = 550B VND

**Analysis:**
```
Sample size: 30 (Good!)
Baseline average revenue: 600B VND
Impact: -50B VND (-8.3%)

Conclusion: Số 04 không có ảnh hưởng tích cực (có thể âm)
```

**Possible explanations:**
1. Unlucky number: 04 = "tứ" (âm tương tự "tử")
2. Avoid effect: Người chơi tránh số này ngày hôm sau
3. Random variation

## 6. Statistical Considerations

### 6.1 Confounding Variables

Query hiện tại **KHÔNG** kiểm soát:

1. **Day of week effect**
   - Weekends thường có doanh thu cao hơn
   - Solution: Add `d2.is_weekend` filter

2. **Seasonality**
   - Tết, holidays ảnh hưởng lớn
   - Solution: Add seasonal controls

3. **Station effect**
   - Đài khác nhau có pattern khác nhau
   - Solution: Group by station

4. **Prize level**
   - Giải đặc biệt vs giải khuyến khích có impact khác nhau
   - Solution: Join with prize_id

### 6.2 Advanced Analysis

#### A. Control for day-of-week
```sql
WITH baseline AS (
    SELECT d.day_of_week, AVG(r.total_revenue) as baseline_revenue
    FROM Fact_Revenue r
    JOIN Dim_Date d ON r.date_id = d.date_id
    GROUP BY d.day_of_week
)
SELECT 
    SUBSTR(lr.result_number, -2) as number,
    AVG(r.total_revenue) as actual_revenue,
    AVG(b.baseline_revenue) as expected_revenue,
    AVG(r.total_revenue) - AVG(b.baseline_revenue) as impact
FROM Fact_Lottery_Result lr
JOIN Dim_Date d1 ON lr.date_id = d1.date_id
JOIN Dim_Date d2 ON d2.full_date = DATE(d1.full_date, '+1 day')
JOIN Fact_Revenue r ON r.date_id = d2.date_id
JOIN baseline b ON d2.day_of_week = b.day_of_week
GROUP BY number
ORDER BY impact DESC
```

#### B. By prize level
```sql
SELECT 
    p.prize_name,
    SUBSTR(lr.result_number, -2) as number,
    AVG(r.total_revenue) as avg_next_day_revenue
FROM Fact_Lottery_Result lr
JOIN Dim_Prize p ON lr.prize_id = p.prize_id
JOIN Dim_Date d1 ON lr.date_id = d1.date_id
JOIN Dim_Date d2 ON d2.full_date = DATE(d1.full_date, '+1 day')
JOIN Fact_Revenue r ON r.date_id = d2.date_id
WHERE p.prize_name = 'Đặc biệt'  -- Special prize only
GROUP BY p.prize_name, number
ORDER BY avg_next_day_revenue DESC
```

#### C. Time-lagged analysis (T+2, T+3)
```sql
-- Check impact after 2 days
JOIN Dim_Date d2 ON d2.full_date = DATE(d1.full_date, '+2 days')

-- Check impact after 7 days
JOIN Dim_Date d2 ON d2.full_date = DATE(d1.full_date, '+7 days')
```

## 7. Business Implications

### 7.1 For Operators

**If strong correlation exists:**

1. **Dynamic pricing**
   - Increase ticket prices for hot numbers
   - Maximize profit during demand surge

2. **Inventory management**
   - Stock more tickets with popular numbers
   - Reduce stock for unpopular numbers

3. **Marketing**
   - Promote lucky numbers in advertising
   - Send SMS alerts when hot numbers appear

### 7.2 For Players

**Understanding patterns:**

1. **Avoid herd mentality**
   - Popular numbers = lower payout ratio (shared jackpot)
   - Consider contrarian strategy

2. **Exploit superstition**
   - If operators adjust prices, unpopular numbers = better value
   - Rational play vs emotional play

## 8. Limitations

### 8.1 Data Quality

1. **Sample size variance**
   - Some numbers appear 50+ times, others only 3-5 times
   - Confidence levels vary significantly

2. **Missing data**
   - Days without lottery draws (holidays)
   - Revenue data gaps

### 8.2 Causation vs Correlation

**Critical question:** Correlation ≠ Causation

```
Scenario 1: True causation
Lottery result → Player behavior → Revenue increase
         (68)        (Buy more 68)       (Higher)

Scenario 2: Spurious correlation
Lottery result (68) ─┐
                     ├→ Both correlated with
Revenue increase     ─┘    hidden variable (Holiday)
```

**Validation needed:**
- A/B testing
- Controlled experiments
- External validation dataset

## 9. Implementation Notes

### 9.1 Performance

**Query optimization:**
- Index on `date_id`, `result_number`
- Materialized view for daily aggregations
- Cache results (update hourly)

### 9.2 Real-time Updates

```python
# Scheduler: Update every night after lottery draw
schedule.every().day.at("20:00").do(update_correlation_data)

def update_correlation_data():
    df = revenue_analysis.get_lottery_number_revenue_impact()
    cache.set('correlation_data', df, ttl=86400)  # 24h cache
```

## 10. Conclusion

### 10.1 Key Takeaways

1. ✅ Query successfully links lottery results (Day T) to revenue (Day T+1)
2. ✅ Provides multiple metrics (avg, sum, count) for robust analysis
3. ✅ Filters for statistical significance (n≥3)
4. ⚠️ Needs controls for confounding variables
5. ⚠️ Correlation does not prove causation

### 10.2 Next Steps

1. **Statistical validation**
   - Chi-square test for independence
   - Regression analysis with controls
   - Time series decomposition

2. **Feature expansion**
   - Prize level granularity
   - Station-specific patterns
   - Multi-day lag analysis (T+2, T+3, T+7)

3. **Business integration**
   - Predictive model for next-day revenue
   - Alert system for hot numbers
   - Dynamic pricing recommendations
