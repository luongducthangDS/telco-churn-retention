# Telco Churn: Rescuing $139k Monthly Lost MRR

Analysis of **7,043 subscriber accounts** ($456k baseline MRR) from the IBM Telco Customer Churn dataset. It moves from business diagnosis, cleans missing billing data in DuckDB SQL, models subscriber retention hazard using Logistic Regression Odds Ratios, and delivers a [one-page decision memo](docs/decision_memo.md) and an interactive dashboard.

![Dashboard](reports/figures/00_dashboard_preview.png)

## Executive Answer

**Churn is concentrated in the onboarding window and high-speed fiber lines without technical support.** Overall churn stands at **26.54%**, costing **$139,131 in lost MRR every month** (30.5% of gross revenue). 

| Finding | Metric |
|---|---|
| Total Subscriber Base | **7,043 accounts** |
| Total MRR & Lost MRR | **$456,116 MRR** $\to$ **$139,131 Lost MRR/mo** |
| Average Customer Tenure | **32.4 months** |
| Month 0–6 Onboarding Cliff | **53.1% churn rate** (50.8% of all churn occurs in first 6 months) |
| Month-to-Month Contract Risk | **42.7% churn** (Odds Ratio = **2.90x**, $p < 0.001$) vs. 1-2 Year at **7.1%** |
| Fiber Optic without TechSupport | **49.38% churn rate** (high price without support) |
| Fiber Optic WITH TechSupport | **22.78% churn rate** (protective effect cut churn by >50%) |
| Electronic Check Churn | **45.3%** vs. Auto Credit Card at **15.2%** |

**So what:** Stop offering standalone unassisted Fiber Optic plans; automatically bundle 90 days of complimentary Tech Support with Fiber installations; launch automated customer success check-ins at Day 7 and Day 21 to navigate the onboarding cliff.

## 📖 Business Storytelling & Problem Statement

### 1. Tình huống kích hoạt (The Trigger Scenario)
Trong phiên họp điều hành chiến lược quý, **Hội đồng Quản trị** chất vấn gay gắt **Giám đốc Thương mại (CCO)** và **Giám đốc Dịch vụ Khách hàng (Head of Customer Service)**:
> *"Mỗi tháng công ty chúng ta đang để mất đứt **$139,131 USD doanh thu định kỳ hàng tháng (MRR)** do khách hàng cắt hợp đồng — tương đương với khoản bốc hơi hơn $1.66 triệu USD mỗi năm! Tỷ lệ Churn toàn mạng chạm mốc báo động 26.54%. Tại sao khách hàng ồ ạt rời bỏ mạng lưới của chúng ta?"*

Để ngăn chặn chảy máu doanh thu, CCO đề xuất chi ngân sách lớn thực hiện chiến dịch giảm giá cước 10% trên toàn bộ các gói thuê bao Internet cáp quang Fiber Optic. Trước khi phê duyệt khoản giảm giá khổng lồ này, Tổng Giám đốc yêu cầu Data Analyst phân tích toàn diện tập dữ liệu 7,043 thuê bao để tìm ra sự thật khách quan.

### 2. Xung đột nghiệp vụ & Bẫy ngộ nhận (The Core Problem & Conflict)
* **Xung đột phòng ban:**
  * **Phòng Thương mại (Sales & Commercial):** Cho rằng cước phí cáp quang ($70 – $100/tháng) đắt hơn các đối thủ cạnh tranh, dẫn đến việc khách hàng chuyển mạng. Họ kiên quyết bảo vệ quan điểm: *"Chỉ có hạ giá cước trên diện rộng mới cứu được tỷ lệ Churn."*
  * **Phòng Hỗ trợ Kỹ thuật (Tech Support):** Khẳng định chất lượng đường truyền cáp quang đạt tốc độ chuẩn cam kết, khách hàng rời đi là do xu hướng giới trẻ thích dùng hợp đồng linh hoạt từng tháng (Month-to-Month) chứ không phải do sự cố kỹ thuật.
  * **Phòng Tài chính (Finance):** Báo động nếu giảm 10% cước Fiber Optic toàn diện, doanh thu sẽ lập tức bốc hơi hơn $30,000 MRR mỗi tháng ngay cả với những khách hàng vốn dĩ không có ý định rời mạng!
* **Bẫy ngộ nhận (False Intuition):** Ban điều hành mặc định rằng *"Khách hàng rời bỏ dịch vụ viễn thông chủ yếu là vì giá cước đắt; chỉ cần giảm giá cước là khách hàng sẽ ở lại"*.

### 3. Cung bậc câu chuyện dữ liệu (The Data Story Arc)
* **Hồi 1 - Ảo tưởng ban đầu (The False Comfort):** Tổng doanh thu định kỳ đạt $456k MRR/tháng, thời gian gắn bó bình quân của thuê bao là 32.4 tháng — các chỉ số trung bình tổng thể tạo cảm giác tập khách hàng khá trung thành và ổn định.
* **Hồi 2 - Vết nứt xuất hiện (The Investigation):**
  * Khi phân tích tỷ lệ rời mạng theo các dải thời gian gắn bó (Tenure Cohort Analysis), dữ liệu làm lộ ra một **vực thẳm Onboarding kinh hoàng**: Có tới **50.8% tổng số ca rời mạng xảy ra ngay trong 6 tháng đầu tiên**!
  * Tỷ lệ Churn của nhóm thuê bao mới (0–6 tháng) lên tới **53.1%**. Tuy nhiên, nếu khách hàng vượt qua được cột mốc 24 tháng, tỷ lệ Churn giảm ngoạn mục xuống dưới 10%.
* **Hồi 3 - Điểm bùng nổ "Aha!" (The Naked Truth):**
  * Khi đào sâu ma trận tương tác giữa gói cước và dịch vụ gia tăng, Data Analyst phát hiện ra sự thật chấn động:
    * Thuê bao sử dụng Cáp quang (Fiber Optic) nhưng **KHÔNG có gói Hỗ trợ Kỹ thuật (Tech Support)** có tỷ lệ Churn kỷ lục: **49.38%**!
    * Ngược lại, cũng là thuê bao dùng Fiber Optic đó, nếu **CÓ gói Tech Support đi kèm**, tỷ lệ Churn lập tức giảm hơn một nửa xuống chỉ còn **22.78%**!
  * **Sự thật thức tỉnh:** Khách hàng không hề rời bỏ vì tốc độ mạng chậm hay giá cước $70 đắt. Họ rời bỏ vì khi chuyển sang công nghệ cáp quang mới, họ gặp trục trặc kỹ thuật ban đầu (cấu hình Router, vùng phủ sóng Wi-Fi trong nhà, tường lửa) mà không có sự đồng hành của kỹ thuật viên, dẫn đến bức xúc và hủy hợp đồng ngay trong tháng đầu!
  * Mô hình kinh tế lượng Logistic Regression (kiểm soát đa biến) chứng minh: Hợp đồng từng tháng (Month-to-Month) làm tăng nguy cơ churn gấp **2.90 lần** (Odds Ratio = 2.90, $p < 0.001$), trong khi phương thức thanh toán Electronic Check có tỷ lệ churn lên tới **45.3%** do trải nghiệm nạp tiền thủ công phiền phức.
* **Hồi 4 - Tháo gỡ nút thắt (The Strategic Resolution):**
  1. **Bác bỏ đề xuất giảm giá cước:** Tiết kiệm ngay hơn $30,000 MRR không bị cắt giảm lãng phí.
  2. **Gói giải pháp "Fiber Onboarding Shield":** Tự động tặng kèm 90 ngày hỗ trợ kỹ thuật chuyên biệt (Tech Support) miễn phí cho 100% hợp đồng lắp mới cáp quang.
  3. **Quy trình Chăm sóc chủ động Day-7 & Day-21:** Tổng đài kỹ thuật chủ động gọi kiểm tra chất lượng kết nối và tối ưu vị trí đặt Router cho khách hàng mới trong tháng đầu tiên.
  4. **Khuyến mãi chuyển đổi hợp đồng:** Tặng ưu đãi giảm 50% cước tháng thứ 12 cho thuê bao Month-to-Month đồng ý ký hợp đồng cam kết 1 năm và kích hoạt tính năng trừ tiền tự động qua Thẻ tín dụng (Auto Credit Card).
* **Hồi 5 - Tác động kinh doanh (The Business Impact):**
  * Cứu vãn ước tính **$45,000 – $60,000 MRR mỗi tháng** (tương đương hơn nửa triệu USD doanh thu định kỳ hàng năm).
  * Kéo tỷ lệ rời mạng của khách hàng mới từ **53.1% xuống dưới 32%** với chi phí vận hành gần như bằng 0.

## Architecture & Method

1. **Model** (`sql/00_model.sql`, DuckDB): Grain is 1 row per subscriber. Handles edge-case blank strings in `TotalCharges` for zero-tenure accounts (`tenure = 0`), builds tenure cohort bands, and constructs service bundle density counts.
2. **Checks** (`tests/test_model.py`, pytest): 5 tests verifying exact row volume (7,043), zero charges for zero tenure, binary churn target flags, dimension surrogate key uniqueness, and star schema referential integrity.
3. **Statistical Analysis** (`analysis/run_analysis.py`):
   - Logistic regression estimating Fisher Information and Odds Ratios for key risk drivers.
   - Cross-feature interaction isolating the protective effect of Tech Support on high-speed Fiber Optic lines.
4. **Outputs**:
   - `reports/results.json` (reproducible metrics).
   - `reports/dashboard.html` (interactive Plotly dashboard).
   - `powerbi/`: Star schema CSVs (`fact_subscriptions.csv`, `dim_customer_demographics.csv`, `dim_service_plan.csv`, `dim_contract.csv`), `measures.dax`, and `power_query.m`.

## How to Run It

```bash
pip install -r requirements.txt
python scripts/get_data.py              # Downloads raw Telco Churn CSV
pytest -q                               # Runs 5 data integrity and referential checks
python analysis/run_analysis.py         # Produces reports/results.json
python analysis/build_dashboard.py      # Exports powerbi/*.csv & reports/dashboard.html
```

## Decisions Worth Defending in an Interview

- **Why Odds Ratios rather than raw correlation coefficients?** Churn is a binary classification target (0/1). Pearson correlation assumes continuous normal distributions and can severely underestimate relationships for binary categories. Odds Ratios from Logistic Regression provide the true multiplicative change in odds of churn while holding all other features constant.
- **Why does Fiber Optic have a higher churn rate than DSL?** Fiber Optic is $33/month more expensive ($91 vs $58) and customers expect pristine performance. Without Tech Support, setup friction and router issues lead to immediate cancellations. When Tech Support is present, Fiber churn drops to 22.8%, proving it is a support issue, not a product issue.
- **How did you clean `TotalCharges`?** 11 rows had blank strings `' '` because the customers had `tenure = 0` (signed up within the last month). Converting directly causes errors; setting them to $0.00 preserves the accounts without dropping valuable new-customer data.

## Interview Questions this Project Prepares For

1. How did you diagnose the root cause of the Fiber Optic paradox?
2. If you built a churn prediction ML model, why would you optimize for Precision/Recall threshold rather than default 0.5 Accuracy?
3. How would you quantify the ROI of offering free Tech Support for 3 months versus the cost of churned MRR?
