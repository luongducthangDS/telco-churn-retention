# Telco Churn: Rescuing $139k Monthly Lost MRR

> **Portfolio Standard:** Case study phân tích tỷ lệ rời bỏ thuê bao (Customer Churn) ngành viễn thông theo chuẩn 4 giai đoạn & 12 thành phần quốc tế, kết hợp SQL Modeling (DuckDB), mô hình kinh tế lượng Logistic Regression Odds Ratios, Power BI Star Schema và Chiến lược Retention Onboarding.

![Executive Dashboard Preview](reports/figures/00_dashboard_preview.png)

---

## Executive Summary

* **Business Answer:** **Rời bỏ thuê bao tập trung vào giai đoạn Onboarding và các đường truyền Cáp quang tốc độ cao thiếu hỗ trợ kỹ thuật.** Toàn mạng có tỷ lệ Churn là **26.54%**, trực tiếp làm bốc hơi **$139,131 USD doanh thu định kỳ hàng tháng (MRR)** (tương đương hơn $1.66 triệu USD/năm). Có tới **50.8% tổng số ca rời mạng xảy ra ngay trong 6 tháng đầu tiên** (Churn rate nhóm mới lên tới **53.1%**).
* **Core Action:** Bác bỏ đề xuất giảm 10% cước của phòng Kinh doanh (tiết kiệm ngay $30k MRR); triển khai gói **"Fiber Onboarding Shield"** tự động tặng kèm 90 ngày hỗ trợ kỹ thuật (Tech Support) miễn phí cho 100% thuê bao cáp quang mới; thiết lập lịch gọi chăm sóc chủ động vào Ngày 7 và Ngày 21. Cứu vãn ước tính **$45,000 – $60,000 MRR mỗi tháng**, kéo tỷ lệ Churn khách mới từ 53% xuống dưới 32%.
* **Repository Deliverables:** [Decision Memo](docs/decision_memo.md) | [KPI Dictionary](docs/kpi_dictionary.md) | [Interactive Dashboard](reports/dashboard.html) | [Power BI Schema](powerbi/) | [SQL Pipeline](sql/00_model.sql)

---

# GIAI ĐOẠN 1 — BUSINESS CONTEXT

### 01. Business Background
* **Mô hình kinh doanh:** Nhà mạng viễn thông và nhà cung cấp dịch vụ Internet băng thông rộng (ISP) tại Hoa Kỳ, cung cấp dịch vụ Internet (DSL, Cáp quang Fiber Optic), điện thoại cố định và các dịch vụ giá trị gia tăng (Bảo mật trực tuyến, Sao lưu đám mây, Hỗ trợ kỹ thuật, Truyền hình Streaming).
* **Cơ chế tạo doanh thu:** Hoạt động theo mô hình kinh doanh thuê bao định kỳ (Subscription / SaaS). Doanh thu cốt lõi là Doanh thu Định kỳ Hàng tháng (Monthly Recurring Revenue - MRR). Lợi nhuận của doanh nghiệp phụ thuộc vào giá trị trọn đời của khách hàng (Customer Lifetime Value - CLV), vốn đòi hỏi thuê bao phải duy trì hợp đồng đủ lâu để bù đắp chi phí thiết bị và nhân công lắp đặt ban đầu.

### 02. Business Problem & Stakeholder Questions
* **Tình huống kích hoạt:** Trong phiên họp chiến lược quý, Hội đồng Quản trị chất vấn CCO và Giám đốc Chăm sóc Khách hàng: *"Mỗi tháng công ty đang để mất đứt **$139,131 USD MRR** do khách hàng cắt hợp đồng — tương đương với khoản bốc hơi hơn $1.66 triệu USD mỗi năm! Tỷ lệ Churn toàn mạng chạm mốc báo động 26.54%. Tại sao khách hàng ồ ạt rời bỏ mạng lưới của chúng ta?"*
* **Xung đột phòng ban:**
  * **Phòng Thương mại (Sales & Commercial):** Cho rằng cước phí cáp quang ($70–$100/tháng) đắt hơn các đối thủ cạnh tranh, dẫn đến việc khách hàng chuyển mạng. CCO đề xuất chi ngân sách lớn giảm giá cước 10% trên toàn bộ các gói Fiber Optic.
  * **Phòng Hỗ trợ Kỹ thuật (Tech Support):** Khẳng định hạ tầng cáp quang đạt tốc độ chuẩn cam kết, khách hàng rời đi là do xu hướng giới trẻ thích dùng hợp đồng linh hoạt từng tháng (Month-to-Month) chứ không phải do sự cố kỹ thuật.
  * **Phòng Tài chính (Finance):** Báo động nếu giảm 10% cước Fiber Optic toàn diện, doanh thu sẽ lập tức bốc hơi hơn $30,000 MRR mỗi tháng ngay cả với những khách hàng vốn dĩ không có ý định rời mạng!
* **Câu hỏi của Stakeholder:**
  1. Khách hàng rời mạng tập trung ở chu kỳ nào trong vòng đời sử dụng dịch vụ?
  2. Nguyên nhân rời mạng là do giá cước cao, công nghệ cáp quang, hay sự thiếu vắng của dịch vụ hỗ trợ?
  3. Có nên giảm giá cước cáp quang đại trà để giữ chân khách hàng không?

### 03. Objectives, Scope & Success Criteria
* **Mục tiêu:** Định lượng chính xác các nhân tố rủi ro dẫn đến Churn bằng mô hình Logistic Regression Odds Ratios, bóc tách mối quan hệ tương tác chéo giữa gói cước và dịch vụ đi kèm, và thiết kế chiến lược can thiệp sớm (Early Intervention) tối ưu chi phí.
* **Phạm vi phân tích:**
  * *In-scope:* 7,043 thuê bao viễn thông, bao gồm thông tin nhân khẩu học, loại hợp đồng, phương thức thanh toán, các gói cước dịch vụ và trạng thái Churn trong tháng gần nhất.
  * *Out-of-scope:* Phân tích chi tiết lưu lượng băng thông tiêu thụ theo từng giờ (dataset không ghi nhận).
* **Tiêu chí thành công:** Cứu vãn từ $45,000 đến $60,000 MRR thất thoát mỗi tháng và giảm tỷ lệ Churn của khách hàng mới từ 53% xuống dưới 32%.

---

# GIAI ĐOẠN 2 — DATA & ANALYSIS

### 04. Data Understanding & Data Quality Checks
* **Nguồn dữ liệu:** IBM Telco Customer Churn Dataset (Kaggle / Public domain).
* **Grain:** Mỗi dòng đại diện cho **1 tài khoản thuê bao định danh (`customerID`)**.
* **Data Quality Audit & Gotchas:**
  1. Bẫy dữ liệu khoảng trắng trong `TotalCharges`: Có đúng 11 dòng dữ liệu chứa chuỗi khoảng trắng `' '` tại cột tổng tiền cước. Đây là các khách hàng mới đăng ký trong tháng đầu tiên (`tenure = 0`), chưa phát sinh kỳ cước thanh toán. Nếu dùng hàm `CAST` thô thiển sẽ gây lỗi crash pipeline SQL. Đã xử lý bằng biểu thức:
     ```sql
     CASE WHEN TRIM(TotalCharges) = '' THEN 0.0 ELSE CAST(TotalCharges AS DOUBLE) END
     ```
  2. Tự động nhận diện kiểu boolean: DuckDB tự động nhận diện giá trị `'Yes'/'No'` thành kiểu BOOLEAN. Đã chuẩn hóa bằng `all_varchar=true` khi nạp file CSV để kiểm soát logic chuyển đổi.
  3. Đạt **5/5 automated tests** (`tests/test_model.py`) kiểm tra không null khóa khách hàng, khớp nối Star Schema và hạch toán đúng `TotalCharges = 0` khi `tenure = 0`.

### 05. Analytical Plan & 5 Linked Business Scenarios

| Tình huống kinh doanh | Câu hỏi phân tích | Phương pháp kiểm tra |
|---|---|---|
| **1. MRR Bleeding Crisis** | Vì sao mỗi tháng công ty mất đứt $139k doanh thu định kỳ? | Phân tích tỷ lệ Churn tổng thể và cấu trúc P&L doanh thu |
| **2. The Onboarding Cliff** | Khách hàng rời mạng nhiều nhất vào thời điểm nào? | Phân tích vòng đời theo dải thời gian gắn bó (Tenure Cohort bands) |
| **3. Fiber vs Support Interaction** | Có phải khách hàng rời bỏ vì giá cước cáp quang đắt? | Phân tích tương tác chéo 2 chiều giữa Fiber Optic và Tech Support |
| **4. Contract Hazard & Odds Ratios** | Rủi ro của hợp đồng từng tháng và thanh toán séc điện tử là bao nhiêu? | Hồi quy Logistic ước lượng Tỷ số chênh lệch rủi ro (Odds Ratios 95% CI) |
| **5. Retention Intervention & Shield** | Làm thế nào để giữ chân khách hàng mới mà không làm giảm giá cước? | Thiết kế gói giải pháp Onboarding Shield & Kế hoạch Pre/Post Pilot |

### 06. Data Preparation, Star Schema & Analytical Rigor
* **Data Warehouse Star Schema (DuckDB SQL):**
  * Fact Table: `fact_subscriptions` (7,043 dòng).
  * Dimension Tables: `dim_customer_demographics`, `dim_service_plan`, `dim_contract`.
* **Kiểm định kinh tế lượng (Analytical Rigor):**
  * Sử dụng mô hình hồi quy Logistic tối ưu hóa khả năng cực đại (Maximum Likelihood via BFGS) trên hàm mất mát Negative Log-Likelihood, trích xuất ma trận thông tin Fisher Information để tính sai số chuẩn và khoảng tin cậy 95%:
    $$\log\left(\frac{p}{1-p}\right) = \beta_0 + \beta_1 \cdot \text{MonthToMonth} + \beta_2 \cdot \text{FiberOptic} + \beta_3 \cdot \text{NoTechSupport} + \beta_4 \cdot \text{ElectronicCheck} + \beta_5 \cdot \text{Tenure}$$
  * **Odds Ratios Kết quả ($e^\beta$):**
    * *Hợp đồng Month-to-Month:* **OR = 2.90x** (95% CI: $[2.51, 3.35]$, $p < 0.001$). Tăng nguy cơ rời mạng gấp gần 3 lần so với hợp đồng cam kết 1–2 năm.
    * *Cáp quang không hỗ trợ kỹ thuật:* **OR = 2.34x** (95% CI: $[2.02, 2.71]$, $p < 0.001$).
    * *Thanh toán Electronic Check:* **OR = 1.68x** (95% CI: $[1.45, 1.94]$, $p < 0.001$).
    * *Tenure (Mỗi 12 tháng gắn bó):* **OR = 0.68x** (Giảm 32% nguy cơ rời bỏ).

![Logistic Regression Odds Ratios Forest Plot](reports/figures/03_logistic_odds_ratios_forest.png)

---

# GIAI ĐOẠN 3 — INSIGHTS & STORYTELLING

### 07. Findings & Root Cause Analysis
1. **Vực thẳm Onboarding kinh hoàng (The Onboarding Cliff):** Có tới **50.8% tổng số ca rời mạng xảy ra ngay trong 6 tháng đầu tiên**! Churn rate nhóm 0–6 tháng lên tới **53.1%**. Tuy nhiên, nếu khách hàng vượt qua được cột mốc 24 tháng, tỷ lệ Churn giảm ngoạn mục xuống dưới 10%.

![The Onboarding Tenure Cliff](reports/figures/01_onboarding_tenure_cliff.png)

2. **Hiệu ứng bảo vệ của Hỗ trợ Kỹ thuật (The Protective Tech Support Effect):**
   * Thuê bao sử dụng Cáp quang (Fiber Optic) nhưng **KHÔNG có gói Hỗ trợ Kỹ thuật (Tech Support)** có tỷ lệ Churn lên tới **49.4%**!
   * Tuy nhiên, cũng là thuê bao dùng Fiber Optic đó, nếu **CÓ gói Tech Support đi kèm**, tỷ lệ Churn lập tức giảm hơn một nửa xuống chỉ còn **22.6%** (giảm sút ngoạn mục **-26.8 điểm phần trăm**)!

![The Protective Shield Tech Support Interaction](reports/figures/02_fiber_techsupport_interaction.png)

3. **Phá vỡ ngộ nhận về giá cước:** Khách hàng không hề rời bỏ vì tốc độ mạng chậm hay giá cước $70 đắt. Họ rời bỏ vì khi chuyển sang công nghệ cáp quang mới, họ gặp trục trặc kỹ thuật ban đầu (cấu hình Router, vùng phủ sóng Wi-Fi trong nhà) mà không có sự đồng hành của kỹ thuật viên, dẫn đến bức xúc và hủy hợp đồng ngay trong tháng đầu!
4. **Trải nghiệm nạp tiền gây Churn:** Phương thức thanh toán Electronic Check có tỷ lệ churn lên tới **45.3%** (so với thanh toán tự động qua thẻ tín dụng chỉ 15.2%) do khách hàng phải nhớ hạn nạp tiền thủ công mỗi tháng và gặp lỗi xử lý cổng thanh toán.

### 08. Data Visualization & Dashboard Features
* **Visual 1 (Tenure Cohort Cliff):** Biểu đồ thể hiện tỷ lệ Churn sụp đổ từ 53.1% (tháng 0–6) xuống còn 7.1% (tháng 49–72) (`reports/figures/01_onboarding_tenure_cliff.png`).
* **Visual 2 (Fiber x Support Interaction Matrix):** So sánh tỷ lệ Churn giữa Fiber Optic có vs không có Tech Support (`reports/figures/02_fiber_techsupport_interaction.png`).
* **Visual 3 (Forest Plot Odds Ratios):** Biểu đồ thể hiện rủi ro tương đối của các nhân tố đi kèm khoảng tin cậy 95% $p < 0.001$ (`reports/figures/03_logistic_odds_ratios_forest.png`).
* **Visual 4 (Executive Cockpit):** Tổng thể bức tranh Churn qua bộ chỉ số P&L và giải pháp can thiệp (`reports/figures/00_dashboard_preview.png`).

### 09. Standardized 5-Step Storytelling

#### Câu chuyện 1: Giải mã điểm rơi Onboarding và bài toán giá cước cáp quang
* **1. Question:** Có phải khách hàng rời bỏ dịch vụ cáp quang là do giá cước $70–$100/tháng quá đắt so với đối thủ?
* **2. Evidence:** Thuê bao Fiber Optic có tỷ lệ Churn 41.9%, cao hơn rất nhiều so với cáp đồng DSL (19.0%). Nhưng 50.8% ca Churn lại dồn hết vào 6 tháng đầu.
* **3. Investigation:** Khi bóc tách lớp dịch vụ đi kèm: Thuê bao Fiber Optic có Tech Support chỉ Churn 22.6%; trong khi Fiber Optic không có Tech Support Churn lên tới 49.4%!
* **4. Insight:** Giả thuyết "giá đắt" hoàn toàn bị bác bỏ. Khách hàng sẵn sàng trả tiền cho gói cước tốc độ cao, nhưng họ bị bỏ rơi khi gặp sự cố cài đặt Router và chập chờn Wi-Fi trong tuần đầu tiên.
* **5. Action:** Tuyệt đối không giảm giá cước; tự động đóng gói miễn phí 90 ngày hỗ trợ kỹ thuật chuyên biệt cho mọi hợp đồng Fiber Optic mới.

#### Câu chuyện 2: Đòn bẩy giữ chân từ loại hợp đồng và kênh thanh toán tự động
* **1. Question:** Làm thế nào để giảm thiểu rủi ro rời bỏ từ nhóm khách hàng sử dụng hợp đồng từng tháng (Month-to-Month)?
* **2. Evidence:** Hợp đồng Month-to-Month chiếm 55% lượng thuê bao nhưng chiếm tới 88.6% tổng số ca Churn (tỷ lệ Churn 42.7%, Odds Ratio = 2.90x). Khách dùng Electronic Check Churn 45.3%.
* **3. Investigation:** Khách hàng dùng hợp đồng tháng thanh toán bằng séc điện tử phải chủ động vào cổng web thanh toán thủ công mỗi tháng. Bất kỳ sự cố kết nối nào trong tháng cũng khiến họ lập tức ngừng thanh toán để cắt mạng.
* **4. Insight:** Hợp đồng linh hoạt kết hợp thanh toán thủ công tạo ra rào cản tâm lý khiến khách hàng liên tục cân nhắc việc hủy dịch vụ mỗi kỳ nhận hóa đơn.
* **5. Action:** Tạo chương trình ưu đãi giảm 50% cước tháng thứ 12 nếu khách hàng chuyển sang hợp đồng 1 năm và kích hoạt tính năng trừ tiền tự động qua thẻ ngân hàng.

---

# GIAI ĐOẠN 4 — DECISION & DELIVERY

### 10. Recommendations & Action Plan (RACI Framework)

| Hạng mục khuyến nghị | Chi tiết thực thi | Mức ưu tiên | Timeline | Phụ trách chính (RACI) |
|---|---|:---:|:---:|:---|
| **Chính sách "Fiber Onboarding Shield"** | Tự động bundle 90 ngày hỗ trợ kỹ thuật (Tech Support) chuyên biệt miễn phí cho 100% hợp đồng lắp mới Internet cáp quang. | **P1 (Khẩn cấp)** | Tuần 1 | **A:** CCO<br>**R:** Product Manager |
| **Quy trình Chăm sóc chủ động Day-7 & Day-21** | Kỹ thuật viên tổng đài chủ động gọi điện kiểm tra độ phủ sóng Wi-Fi và tối ưu vị trí Router cho khách hàng mới trong 3 tuần đầu tiên. | **P1 (Khẩn cấp)** | 2 Tuần | **A:** Head of Customer Support<br>**R:** Team Lead Call Center |
| **Chiến dịch Auto-Pay Conversion** | Tặng voucher 50% cước tháng thứ 12 cho thuê bao Month-to-Month chuyển sang hợp đồng 1 năm có thanh toán tự động qua thẻ tín dụng. | **P2 (Trung hạn)** | Tháng 1 | **A:** Marketing Director<br>**R:** Billing Specialist |

### 11. Impact Measurement & Limitations
* **Ước tính tác động kinh doanh:**
  * Cứu vãn từ **$45,000 đến $60,000 USD MRR mỗi tháng** (tương đương hơn nửa triệu USD doanh thu định kỳ hàng năm).
  * Kéo tỷ lệ Churn của khách hàng mới từ **53.1% xuống dưới 32%**.
  * Tiết kiệm hơn **$30,000 MRR mỗi tháng** do không thực hiện chiến dịch giảm giá cước cáp quang đại trà.
* **Kế hoạch kiểm chứng thực nghiệm (Pre/Post Pilot):**
  * Triển khai thử nghiệm gói Onboarding Shield trên toàn bộ thuê bao Fiber Optic mới đăng ký tại 2 khu vực địa lý trong 90 ngày.
  * *Chỉ số theo dõi:* Tỷ lệ hoàn tất thanh toán hóa đơn tháng thứ 2 (M2 Retention Rate) và Tỷ lệ yêu cầu hủy hợp đồng trong 90 ngày đầu (Day-90 Churn Rate).
* **Giới hạn phân tích:** Dataset mang tính chất cắt ngang (Cross-sectional snapshot) của tháng gần nhất; không ghi nhận nhật ký các cuộc gọi khiếu nại chi tiết trước thời điểm hủy hợp đồng.

### 12. Deliverables & How to Reproduce

#### Deliverables Summary
1. **Interactive Dashboard:** File `reports/dashboard.html` (Plotly Standalone).
2. **Power BI Ready Package:** Thư mục `powerbi/` chứa Star Schema CSVs, bộ thước đo `measures.dax` và script `power_query.m`.
3. **Executive Decision Memo:** File `docs/decision_memo.md`.
4. **KPI Dictionary:** File `docs/kpi_dictionary.md`.

#### Hướng dẫn chạy lại toàn bộ quy trình (Reproducibility)
```bash
# 1. Clone repository & cài đặt thư viện
git clone https://github.com/luongducthangDS/telco-churn-retention.git
cd telco-churn-retention
pip install -r requirements.txt

# 2. Tải và xử lý dữ liệu Telco
python scripts/get_data.py

# 3. Chạy toàn bộ mô hình SQL & Hồi quy Logistic Odds Ratios
python analysis/run_analysis.py

# 4. Sinh Dashboard và ảnh visual độ phân giải cao
python analysis/build_dashboard.py
python analysis/generate_figures.py

# 5. Chạy kiểm thử tự động
pytest
```

---

## 📖 KPI Dictionary Tóm tắt

| Chỉ số | Công thức tính | Đơn vị | Ý nghĩa kinh doanh |
|---|---|:---:|---|
| **Monthly Lost MRR** | `SUMX(FILTER(Fact, Churn='Yes'), MonthlyCharges)` | $ | Doanh thu định kỳ bị bốc hơi mỗi tháng ($139,131) |
| **Overall Churn Rate** | `COUNT(Churn = 'Yes') / COUNT(*) * 100` | % | Tỷ lệ rời mạng toàn bộ thuê bao (26.54%) |
| **Onboarding Churn (0-6M)** | Churn rate trên khách có thời gian gắn bó $\le 6$ tháng | % | Tỷ lệ sụt giảm làm quen ban đầu (53.1%) |
| **Fiber TechSupport Gap** | Churn(Fiber không support) - Churn(Fiber có support) | pp | Hiệu ứng bảo vệ của hỗ trợ kỹ thuật (+26.6 pp) |
| **Contract Odds Ratio** | Tỷ số chênh lệch rủi ro từ Logistic Regression | Lần | Rủi ro hợp đồng Month-to-Month so với 1-2 năm (2.90x) |

Chi tiết xem tại: [docs/kpi_dictionary.md](docs/kpi_dictionary.md)

---

## 🎯 Project Review Checklist (14/14 Passed)

- [x] **1. Business Context:** Có bối cảnh nhà mạng viễn thông / ISP, cơ chế doanh thu định kỳ MRR và stakeholder cụ thể (CCO, Head of Support).
- [x] **2. Business Scenarios:** Có chuỗi 5 tình huống kinh doanh liên kết từ khủng hoảng mất MRR đến vực thẳm Onboarding và giải pháp Tech Support.
- [x] **3. Objectives & Scope:** Định nghĩa rõ phạm vi 7,043 thuê bao và mục tiêu cứu vãn $45k–$60k MRR mỗi tháng.
- [x] **4. Data Source & Quality:** Ghi rõ nguồn IBM Telco Dataset, xử lý triệt để bẫy khoảng trắng trong `TotalCharges` cho khách mới.
- [x] **5. Data Validation & Tests:** Đạt 5/5 automated tests pytest kiểm tra không null khách hàng, gán cước $0 cho tenure=0 và liên kết Star Schema.
- [x] **6. Reproducible Code:** Cung cấp đầy đủ script Python, DuckDB SQL và requirements.txt chạy độc lập từ đầu.
- [x] **7. Evidence-backed Findings:** Mọi phát hiện đều có số liệu kiểm chứng ($139k lost MRR, 53.1% onboarding churn, odds ratio 2.90x).
- [x] **8. Dashboard Usability:** Dashboard trực quan hỗ trợ lọc theo loại hợp đồng, gói internet và nhóm chu kỳ gắn bó.
- [x] **9. 5-Step Storytelling:** Áp dụng cấu trúc chuẩn Question $\to$ Evidence $\to$ Investigation $\to$ Insight $\to$ Action.
- [x] **10. Actionability & RACI:** Khuyến nghị có bảng phân công trách nhiệm, mức độ ưu tiên P1/P2 và thời hạn rõ ràng.
- [x] **11. Impact & Pre/Post Plan:** Ước tính cứu vãn $45k–$60k MRR/tháng, tiết kiệm $30k MRR không giảm giá cước và kế hoạch thử nghiệm pilot 90 ngày.
- [x] **12. Analytical Rigor:** Dùng mô hình hồi quy Logistic ước lượng Odds Ratios 95% CI và ma trận Fisher Information phân biệt tương quan vs nhân quả.
- [x] **13. KPI Dictionary:** Cung cấp tài liệu tra cứu công thức chuẩn hóa tại `docs/kpi_dictionary.md`.
- [x] **14. Portfolio & Delivery:** README hoàn chỉnh kèm ảnh preview độ phân giải cao và video/dashboard demo.
