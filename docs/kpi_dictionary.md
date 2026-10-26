# KPI Dictionary: IBM Telco Customer Churn & Retention Strategy

Tài liệu định nghĩa chuẩn hóa toàn bộ các chỉ số đo lường tỷ lệ rời bỏ khách hàng (Churn Rate), phân tích nguy cơ (Hazard Rate / Odds Ratios) và tổn thất doanh thu định kỳ (MRR) theo chuẩn SaaS và Viễn thông quốc tế.

---

## 1. Bảng tra cứu KPI cốt lõi

| Mã KPI | Tên chỉ số | Công thức tính toán | Đơn vị | Grain / Phạm vi tính | Ý nghĩa kinh doanh & Ngưỡng chuẩn |
|:---|:---|:---|:---:|:---|:---|
| **KPI-01** | **Total Subscriber Base** | `COUNT(DISTINCT customerID)` | Thuê bao | Toàn mạng viễn thông | Tổng số tài khoản khách hàng đang hoạt động trong tập dữ liệu. Tổng: **7,043 tài khoản**. |
| **KPI-02** | **Monthly Recurring Revenue (MRR)** | `SUM(MonthlyCharges)` | USD ($) | Toàn mạng / Phân khúc hợp đồng | Tổng doanh thu định kỳ hàng tháng từ các gói thuê bao cố định. Hiện trạng: **$456,116 USD/tháng**. |
| **KPI-03** | **Monthly Lost MRR** | `SUMX(FILTER(Fact, Churn = 'Yes'), MonthlyCharges)` | USD ($) | Toàn mạng / Phân khúc Churn | Tổng số tiền doanh thu định kỳ bị bốc hơi mỗi tháng do khách hủy hợp đồng. Hiện trạng: **$139,131 USD/tháng**. |
| **KPI-04** | **Annualized Lost Revenue** | `[Monthly Lost MRR] * 12` | USD ($) | Toàn công ty | Thiệt hại doanh thu quy đổi theo năm. Hiện trạng: **$1,669,572 USD/năm**. |
| **KPI-05** | **Overall Churn Rate %** | `COUNT(Churn = 'Yes') / COUNT(Total Customers) * 100` | % | Toàn mạng | Tỷ lệ khách hàng rời bỏ dịch vụ. Hiện trạng: **26.54%** (Ngưỡng báo động đỏ trong ngành Telco). |
| **KPI-06** | **Average Customer Tenure** | `AVG(tenure)` | Tháng | Toàn mạng / Nhóm khách hàng | Thời gian khách hàng gắn bó với nhà mạng. Trung bình: **32.4 tháng**. |
| **KPI-07** | **Onboarding Churn Rate (0–6M)** | `COUNT(Churn='Yes' in 0-6M) / COUNT(Total in 0-6M) * 100` | % | Nhóm thuê bao mới $\le 6$ tháng | Tỷ lệ rời mạng trong giai đoạn làm quen dịch vụ ban đầu. Đạt mức thảm họa: **53.1%**. |
| **KPI-08** | **Onboarding Churn Concentration** | `COUNT(Churn in 0-6M) / Total Churned Customers * 100` | % | Tập khách hàng đã Churn | Tỷ trọng các ca rời mạng diễn ra ngay trong 6 tháng đầu. Đạt: **50.8%**. |
| **KPI-09** | **Fiber Optic Churn Gap** | `Churn Rate(Fiber without TechSupport) - Churn Rate(Fiber WITH TechSupport)` | Điểm % (pp) | Thuê bao Internet cáp quang | Đo lường hiệu ứng bảo vệ của gói hỗ trợ kỹ thuật: **49.38% vs 22.78%** (Chênh lệch: **+26.6 pp**). |
| **KPI-10** | **Contract Odds Ratio (Month-to-Month)** | $e^{\beta_{\text{month-to-month}}}$ từ mô hình hồi quy Logistic | Lần (Odds) | Loại hợp đồng | Đo lường rủi ro tương đối của hợp đồng tháng so với hợp đồng 1-2 năm. Đạt: **2.90x** ($p < 0.001$). |

---

## 2. Ma trận rủi ro theo chu kỳ gắn bó (Tenure Cohort Cliff)

| Khung thời gian (Tenure) | Số lượng khách hàng | Tỷ lệ Churn (%) | Số ca Churn | Nhận định rủi ro kinh doanh |
|---|:---:|:---:|:---:|:---|
| **0 – 6 tháng (New Onboarding)** | 1,481 | **53.1%** | 786 | **Vực thẳm nguy hiểm số 1 (Chiếm 50.8% tổng ca rời mạng toàn công ty)** |
| **7 – 12 tháng** | 699 | **33.2%** | 232 | Giai đoạn nhạy cảm sau các chương trình khuyến mãi tháng đầu |
| **13 – 24 tháng** | 1,024 | **28.6%** | 293 | Hết hạn hợp đồng cam kết 1 năm đầu tiên |
| **25 – 48 tháng** | 1,594 | **18.4%** | 294 | Khách hàng tương đối ổn định |
| **49 – 72 tháng (Mature/Loyal)**| 2,245 | **7.1%** | 160 | Nhóm khách hàng trung thành bền vững |

---

## 3. Tương tác dịch vụ Cáp quang & Hỗ trợ Kỹ thuật

- **Fiber Optic KHÔNG CÓ Tech Support:** 3,096 khách hàng $\to$ Churn rate: **49.38%** (Đóng góp lớn nhất vào thất thoát MRR).
- **Fiber Optic CÓ Tech Support:** 1,200 khách hàng $\to$ Churn rate: **22.78%** (Cắt giảm hơn 50% nguy cơ rời bỏ).
- **Phương thức thanh toán Electronic Check:** Churn rate **45.3%** vs **Auto Credit Card (15.2%)**.
