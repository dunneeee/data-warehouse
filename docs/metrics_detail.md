Giải thích **khái niệm** các metrics thường dùng (đúng ngữ cảnh hồi quy / forecasting):

---

## 1. R² (Coefficient of Determination)

**Trả lời câu hỏi:** *Model giải thích được bao nhiêu % biến động của dữ liệu?*

* R² ∈ (−∞, 1]
* R² = 1 → fit hoàn hảo
* R² = 0 → không tốt hơn đoán trung bình
* R² < 0 → tệ hơn baseline (mean)

**Bản chất:**
So sánh **lỗi của model** với **lỗi khi luôn đoán bằng giá trị trung bình**.

**Lưu ý quan trọng:**

* R² **không phản ánh độ lớn sai số**
* Dễ “đẹp giả” khi có nhiều feature
* Không dùng để so sánh giữa các tập dữ liệu khác nhau

---

## 2. MAE (Mean Absolute Error)

**Trả lời câu hỏi:** *Trung bình mỗi lần dự đoán sai bao nhiêu?*

[
MAE = \frac{1}{n} \sum |y - \hat y|
]

**Bản chất:**

* Lấy **khoảng cách tuyệt đối**
* Mỗi lỗi được đối xử **như nhau**

**Ưu điểm:**

* Dễ hiểu
* Ít bị ảnh hưởng bởi outlier
* Cùng đơn vị với target (VND)

**Nhược điểm:**

* Không “phạt nặng” lỗi lớn

👉 Dùng khi muốn **độ chính xác trung bình thực tế**

---

## 3. RMSE (Root Mean Squared Error)

**Trả lời câu hỏi:** *Model có mắc lỗi lớn không?*

[
RMSE = \sqrt{\frac{1}{n} \sum (y - \hat y)^2}
]

**Bản chất:**

* Bình phương lỗi → **lỗi lớn bị phạt mạnh**
* Nhạy với outlier

**Ưu điểm:**

* Phản ánh rủi ro
* Tốt khi lỗi lớn rất nguy hiểm

**Nhược điểm:**

* Bị kéo lên bởi vài điểm cực đoan

👉 Dùng khi **sai số lớn là không chấp nhận được**

---

## 4. MAPE (Mean Absolute Percentage Error)

**Trả lời câu hỏi:** *Sai bao nhiêu % so với giá trị thật?*

[
MAPE = \frac{100}{n} \sum \left| \frac{y - \hat y}{y} \right|
]

**Bản chất:**

* Đo **sai số tương đối**
* Không phụ thuộc đơn vị

**Ưu điểm:**

* Dễ diễn giải cho business
* So sánh giữa các tập dữ liệu

**Nhược điểm nghiêm trọng:**

* Không dùng được khi `y ≈ 0`
* Bias khi giá trị nhỏ

👉 Dùng khi **target luôn dương và đủ lớn**

---

## 5. So sánh nhanh

| Metric | Đo cái gì      | Nhạy outlier | Dễ hiểu    | Khi dùng           |
| ------ | -------------- | ------------ | ---------- | ------------------ |
| R²     | Mức giải thích | ❌            | Trung bình | Đánh giá tổng quát |
| MAE    | Sai số TB      | ❌            | ✅          | Thực tế, ổn định   |
| RMSE   | Lỗi lớn        | ✅            | ⚠️         | Rủi ro cao         |
| MAPE   | Sai %          | ⚠️           | ✅          | Báo cáo business   |

---

## 6. Best practice (rất quan trọng)

* **Không dùng 1 metric**
* Thường dùng combo:

  * **MAE + RMSE** → kỹ thuật
  * **MAPE** → business
  * **R²** → mức độ mô hình hóa

Ví dụ diễn giải đúng:

> R² = 0.71 (model giải thích tốt)
> MAE = 18 tỷ (sai trung bình chấp nhận được)
> RMSE = 29 tỷ (có vài tháng lệch lớn)
> MAPE = 2.99% (độ chính xác cao về mặt kinh doanh)

---

Nếu bạn muốn, mình có thể:

* So sánh **MAE vs RMSE bằng hình học**
* Giải thích **vì sao time series không nên chỉ nhìn R²**
* Gợi ý **metric phù hợp cho forecasting dài hạn**
