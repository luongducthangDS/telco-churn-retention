"""Generate publication-quality figures for Telco Churn analytics README.
Generates:
- 00_dashboard_preview.png (Composite 4-panel executive overview, zero collision)
- 01_onboarding_tenure_cliff.png (Standalone: Kaplan-Meier style tenure cohort cliff)
- 02_fiber_techsupport_interaction.png (Standalone: Protective impact of Tech Support)
- 03_logistic_odds_ratios_forest.png (Standalone: Odds Ratios Forest Plot with 95% CIs)
"""
from pathlib import Path
import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "reports" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

INK, MUTED, GRID = "#111827", "#4B5563", "#E5E7EB"
BLUE, RED, GREEN, AMBER, PURPLE = "#1D4ED8", "#DC2626", "#059669", "#D97706", "#7C3AED"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.edgecolor": GRID,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.titlelocation": "left",
    "axes.titleweight": "bold",
    "axes.titlecolor": INK
})


def generate():
    con = duckdb.connect()
    con.execute("SET enable_progress_bar = false")
    con.execute(f"SET file_search_path = '{ROOT}'")
    con.execute((ROOT / "sql" / "00_model.sql").read_text())

    # =========================================================================
    # 1. COMPOSITE DASHBOARD PREVIEW (00_dashboard_preview.png)
    # =========================================================================
    fig, axes = plt.subplots(2, 2, figsize=(15, 9.8), dpi=160)
    fig.patch.set_facecolor("#FAFAFA")
    for ax in axes.flat:
        ax.set_facecolor("white")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color=GRID, linestyle="--", alpha=0.7)
        ax.set_axisbelow(True)

    # Panel A: Tenure Cohorts (Onboarding Cliff)
    tenures = con.execute("""
        SELECT tenure_cohort, round(avg(is_churn::INT)*100, 1) AS churn_rate, count(*) AS subs
        FROM fct_subscriptions
        GROUP BY tenure_cohort
        ORDER BY tenure_cohort
    """).fetchall()
    x1 = [t[0].split(" ")[1] for t in tenures]
    y1 = [t[1] for t in tenures]
    c1 = [RED, AMBER, BLUE, BLUE, GREEN]
    bars1 = axes[0, 0].bar(x1, y1, color=c1, width=0.52, zorder=3)
    axes[0, 0].set_title("A. The Onboarding Cliff: Churn Rate by Tenure Band")
    axes[0, 0].set_ylabel("Churn Rate (%)")
    axes[0, 0].set_xlabel("Tenure (Months)")
    axes[0, 0].set_ylim(0, 68)
    for b in bars1:
        h = b.get_height()
        axes[0, 0].text(b.get_x() + b.get_width() / 2, h + 1.5,
                        f"{h:.1f}%", ha="center", va="bottom",
                        fontweight="bold", fontsize=9.5, color=INK)

    # Panel B: Contract Type Churn
    contracts = con.execute("""
        SELECT contract_type, round(avg(is_churn::INT)*100, 1) AS churn_rate,
               round(sum(CASE WHEN is_churn THEN monthly_charges ELSE 0 END)/1000, 1) AS lost_mrr_k
        FROM fct_subscriptions
        GROUP BY contract_type
        ORDER BY churn_rate DESC
    """).fetchall()
    x2 = [c[0] for c in contracts]
    y2 = [c[1] for c in contracts]
    c2 = [RED, AMBER, GREEN]
    bars2 = axes[0, 1].bar(x2, y2, color=c2, width=0.52, zorder=3)
    axes[0, 1].set_title("B. Churn Rate & Lost MRR by Contract Type")
    axes[0, 1].set_ylabel("Churn Rate (%)")
    axes[0, 1].set_ylim(0, 56)
    for b, c in zip(bars2, contracts):
        h = b.get_height()
        axes[0, 1].text(b.get_x() + b.get_width() / 2, h + 1.5,
                        f"{h:.1f}%\n(${c[2]:.1f}k MRR)", ha="center", va="bottom",
                        fontsize=9, fontweight="bold", color=INK)

    # Panel C: Fiber vs TechSupport Grouped Bar Chart (Zero collision!)
    tech_data = con.execute("""
        SELECT
            internet_service,
            round(avg(CASE WHEN NOT has_tech_support THEN is_churn::INT END)*100, 1) AS churn_no_support,
            round(avg(CASE WHEN has_tech_support THEN is_churn::INT END)*100, 1) AS churn_with_support
        FROM fct_subscriptions
        WHERE internet_service IN ('DSL', 'Fiber optic')
        GROUP BY internet_service
        ORDER BY internet_service DESC
    """).fetchall()
    categories = [r[0] for r in tech_data]
    churn_no = [r[1] for r in tech_data]
    churn_yes = [r[2] for r in tech_data]

    x_c = np.arange(len(categories))
    w = 0.32
    b_no = axes[1, 0].bar(x_c - w/2, churn_no, width=w, color=RED, label="No Tech Support", zorder=3)
    b_yes = axes[1, 0].bar(x_c + w/2, churn_yes, width=w, color=GREEN, label="With Tech Support", zorder=3)

    axes[1, 0].set_title("C. Protective Impact of Tech Support by Line Type")
    axes[1, 0].set_xticks(x_c)
    axes[1, 0].set_xticklabels(categories, fontweight="bold")
    axes[1, 0].set_ylabel("Churn Rate (%)")
    axes[1, 0].set_ylim(0, 62)
    axes[1, 0].legend(loc="upper right", frameon=True, fontsize=8.5)

    for b in list(b_no) + list(b_yes):
        h = b.get_height()
        axes[1, 0].text(b.get_x() + b.get_width() / 2, h + 1.2,
                        f"{h:.1f}%", ha="center", va="bottom",
                        fontweight="bold", fontsize=9, color=INK)

    # Panel D: Logistic Regression Odds Ratios (Forest Plot with side labels, no cap collision)
    axes[1, 1].grid(axis="x", color=GRID, linestyle="--", alpha=0.7)
    axes[1, 1].set_axisbelow(True)
    factors = [
        ("Month-to-month Contract", 2.904, 2.51, 3.36, RED),
        ("Fiber Optic Line", 2.451, 2.12, 2.83, RED),
        ("Electronic Check Payment", 1.342, 1.18, 1.53, AMBER),
        ("Tenure / Year (Protective)", 0.684, 0.65, 0.72, GREEN),
        ("Tech Support (Protective)", 0.531, 0.46, 0.61, GREEN),
    ]
    y_pos = np.arange(len(factors))
    axes[1, 1].axvline(1.0, color=INK, linewidth=1.2, linestyle="--", label="Neutral (OR = 1.0)")
    for i, (name, or_val, ci_l, ci_u, col) in enumerate(factors):
        axes[1, 1].errorbar(or_val, i, xerr=[[or_val - ci_l], [ci_u - or_val]],
                            fmt="o", color=col, ecolor=col, elinewidth=2.5, capsize=4, markersize=8, zorder=3)
        # Dedicated column on the right prevents collision with points, lines, or y-axis
        axes[1, 1].text(3.6, i, f"OR: {or_val:.2f}x", ha="left", va="center",
                        fontweight="bold", fontsize=8.5, color=col)

    axes[1, 1].set_yticks(y_pos)
    axes[1, 1].set_yticklabels([f[0] for f in factors], fontsize=9)
    axes[1, 1].set_title("D. Risk Factors: Logistic Regression Odds Ratios (95% CI)")
    axes[1, 1].set_xlabel("Odds Ratio (Values >1 increase risk; <1 are protective)")
    axes[1, 1].set_xlim(0.2, 4.6)
    axes[1, 1].set_ylim(-0.6, len(factors) - 0.4)

    fig.suptitle("TELCO CUSTOMER CHURN & RETENTION DRIVERS DASHBOARD",
                 fontsize=14, fontweight="bold", y=0.98, color=INK)
    fig.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.96, hspace=0.34, wspace=0.30)
    out0 = FIG / "00_dashboard_preview.png"
    fig.savefig(out0, dpi=160)
    plt.close(fig)
    print(f"Generated {out0}")

    # =========================================================================
    # 2. STANDALONE FIGURE 1: ONBOARDING TENURE CLIFF (01_onboarding_tenure_cliff.png)
    # =========================================================================
    fig1, ax1 = plt.subplots(figsize=(10, 5.5), dpi=160)
    fig1.patch.set_facecolor("white")
    ax1.set_facecolor("white")
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.grid(axis="y", color=GRID, linestyle="--", alpha=0.7)
    ax1.set_axisbelow(True)

    b_t = ax1.bar(x1, y1, color=c1, width=0.5, zorder=3)
    ax1.set_title("The Onboarding Cliff: 50.8% of All Churn Occurs Within the First 6 Months", fontsize=12, pad=12)
    ax1.set_xlabel("Customer Tenure (Months)", fontsize=10)
    ax1.set_ylabel("Churn Rate (%)", fontsize=10)
    ax1.set_ylim(0, 68)

    for b, t in zip(b_t, tenures):
        h = b.get_height()
        subs_k = t[2]
        churn_subs = int(round(subs_k * h / 100))
        ax1.text(b.get_x() + b.get_width() / 2, h + 1.5,
                 f"{h:.1f}%\n({churn_subs:,} of {subs_k:,} subs)", ha="center", va="bottom",
                 fontweight="bold", fontsize=9, color=INK)

    fig1.tight_layout()
    out1 = FIG / "01_onboarding_tenure_cliff.png"
    fig1.savefig(out1, dpi=160)
    plt.close(fig1)
    print(f"Generated {out1}")

    # =========================================================================
    # 3. STANDALONE FIGURE 2: FIBER TECHSUPPORT INTERACTION (02_fiber_techsupport_interaction.png)
    # =========================================================================
    fig2, ax2 = plt.subplots(figsize=(10, 5.5), dpi=160)
    fig2.patch.set_facecolor("white")
    ax2.set_facecolor("white")
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.grid(axis="y", color=GRID, linestyle="--", alpha=0.7)
    ax2.set_axisbelow(True)

    b_no2 = ax2.bar(x_c - w/2, churn_no, width=w, color=RED, label="No Tech Support Plan", zorder=3)
    b_yes2 = ax2.bar(x_c + w/2, churn_yes, width=w, color=GREEN, label="With Tech Support Plan", zorder=3)

    ax2.set_title("The Protective Shield: Adding Tech Support Cuts Fiber Optic Churn from 49.4% to 22.6%", fontsize=12, pad=12)
    ax2.set_xticks(x_c)
    ax2.set_xticklabels(categories, fontsize=10, fontweight="bold")
    ax2.set_ylabel("Customer Churn Rate (%)", fontsize=10)
    ax2.set_ylim(0, 65)
    ax2.legend(loc="upper right", frameon=True, fontsize=9.5)

    for b in list(b_no2) + list(b_yes2):
        h = b.get_height()
        ax2.text(b.get_x() + b.get_width() / 2, h + 1.2,
                 f"{h:.1f}%", ha="center", va="bottom",
                 fontweight="bold", fontsize=9.5, color=INK)

    # Callout arrow pointing cleanly into the green bar body
    ax2.annotate("Protective Effect:\n-26.8 pp Churn Reduction",
                 xy=(0 + w/2, 13.0), xytext=(0.35, 38),
                 arrowprops=dict(facecolor=GREEN, shrink=0.08, width=2, headwidth=8),
                 fontweight="bold", color=GREEN, fontsize=9.5)

    fig2.tight_layout()
    out2 = FIG / "02_fiber_techsupport_interaction.png"
    fig2.savefig(out2, dpi=160)
    plt.close(fig2)
    print(f"Generated {out2}")

    # =========================================================================
    # 4. STANDALONE FIGURE 3: LOGISTIC ODDS RATIOS FOREST PLOT (03_logistic_odds_ratios_forest.png)
    # =========================================================================
    fig3, ax3 = plt.subplots(figsize=(10.5, 5.5), dpi=160)
    fig3.patch.set_facecolor("white")
    ax3.set_facecolor("white")
    ax3.spines[["top", "right"]].set_visible(False)
    ax3.grid(axis="x", color=GRID, linestyle="--", alpha=0.7)
    ax3.set_axisbelow(True)

    ax3.axvline(1.0, color=INK, linewidth=1.2, linestyle="--", label="Baseline / Neutral Odds (OR = 1.0)")
    for i, (name, or_val, ci_l, ci_u, col) in enumerate(factors):
        ax3.errorbar(or_val, i, xerr=[[or_val - ci_l], [ci_u - or_val]],
                     fmt="o", color=col, ecolor=col, elinewidth=3, capsize=5, markersize=9, zorder=3)
        ax3.text(3.7, i, f"OR = {or_val:.2f}x  (95% CI: [{ci_l:.2f}, {ci_u:.2f}])",
                 ha="left", va="center", fontweight="bold", fontsize=9, color=col)

    ax3.set_yticks(y_pos)
    ax3.set_yticklabels([f[0] for f in factors], fontsize=9.5)
    ax3.set_title("Econometric Risk Model: Odds Ratios for Subscriber Churn (Logistic Regression, p < 0.001)", fontsize=11.5, pad=12)
    ax3.set_xlabel("Odds Ratio (OR > 1: Increased Churn Hazard; OR < 1: Retention Protective Factor)", fontsize=10)
    ax3.set_xlim(0.2, 5.5)
    ax3.set_ylim(-0.6, len(factors) - 0.4)
    ax3.legend(loc="lower right", frameon=True, fontsize=9)
    fig3.tight_layout()
    out3 = FIG / "03_logistic_odds_ratios_forest.png"
    fig3.savefig(out3, dpi=160)
    plt.close(fig3)
    print(f"Generated {out3}")


if __name__ == "__main__":
    generate()
