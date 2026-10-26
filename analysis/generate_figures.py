"""Generate publication-quality figures for Telco Churn analytics README."""
from pathlib import Path
import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "reports" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

INK, MUTED, GRID = "#1F2937", "#6B7280", "#E5E7EB"
BLUE, RED, GREEN, AMBER = "#2563EB", "#DC2626", "#059669", "#D97706"

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

    fig, axes = plt.subplots(2, 2, figsize=(14, 9), dpi=150)
    fig.patch.set_facecolor("#FAFAFA")
    for ax in axes.flat:
        ax.set_facecolor("white")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color=GRID, linestyle="--", alpha=0.7)
        ax.set_axisbelow(True)

    # 1. Tenure Cohorts (Onboarding Cliff)
    tenures = con.execute("""
        SELECT tenure_cohort, round(avg(is_churn::INT)*100, 1) AS churn_rate, count(*) AS subs
        FROM fct_subscriptions
        GROUP BY tenure_cohort
        ORDER BY tenure_cohort
    """).fetchall()
    x1 = [t[0].split(" ")[1] for t in tenures]
    y1 = [t[1] for t in tenures]
    c1 = [RED, AMBER, BLUE, BLUE, GREEN]
    bars1 = axes[0, 0].bar(x1, y1, color=c1, width=0.55, zorder=3)
    axes[0, 0].set_title("A. The Onboarding Cliff: Churn Rate by Tenure")
    axes[0, 0].set_ylabel("Churn Rate (%)")
    axes[0, 0].set_ylim(0, max(y1) * 1.25)
    for b in bars1:
        axes[0, 0].text(b.get_x() + b.get_width() / 2, b.get_height() + 1.2,
                        f"{b.get_height():.1f}%", ha="center", va="bottom", fontweight="bold", color=INK)

    # 2. Contract Type Churn
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
    bars2 = axes[0, 1].bar(x2, y2, color=c2, width=0.55, zorder=3)
    axes[0, 1].set_title("B. Churn Rate by Contract Commitment")
    axes[0, 1].set_ylabel("Churn Rate (%)")
    axes[0, 1].set_ylim(0, max(y2) * 1.25)
    for b, c in zip(bars2, contracts):
        axes[0, 1].text(b.get_x() + b.get_width() / 2, b.get_height() + 1.2,
                        f"{b.get_height():.1f}%\n(${c[2]:.1f}k MRR)", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=INK)

    # 3. Fiber vs TechSupport Interaction
    fiber_tech = con.execute("""
        SELECT
            internet_service || '\n' || CASE WHEN has_tech_support THEN 'With TechSupport' ELSE 'NO TechSupport' END,
            round(avg(is_churn::INT)*100, 1) AS churn_rate
        FROM fct_subscriptions
        WHERE internet_service IN ('Fiber optic', 'DSL')
        GROUP BY internet_service, has_tech_support
        ORDER BY churn_rate DESC
    """).fetchall()
    x3 = [f[0] for f in fiber_tech]
    y3 = [f[1] for f in fiber_tech]
    c3 = [RED, BLUE, AMBER, GREEN]
    bars3 = axes[1, 0].bar(x3, y3, color=c3, width=0.55, zorder=3)
    axes[1, 0].set_title("C. The Fiber Optic Paradox: Adding Tech Support")
    axes[1, 0].set_ylabel("Churn Rate (%)")
    axes[1, 0].set_ylim(0, max(y3) * 1.25)
    for b in bars3:
        axes[1, 0].text(b.get_x() + b.get_width() / 2, b.get_height() + 1.2,
                        f"{b.get_height():.1f}%", ha="center", va="bottom", fontweight="bold", color=INK)

    # 4. Logistic Regression Odds Ratios (Forest Plot)
    axes[1, 1].grid(axis="x", color=GRID, linestyle="--", alpha=0.7)
    axes[1, 1].set_axisbelow(True)
    factors = [
        ("Month-to-month Contract", 2.904, 2.51, 3.36, RED),
        ("Fiber Optic Internet", 2.451, 2.12, 2.83, RED),
        ("Electronic Check Payment", 1.342, 1.18, 1.53, AMBER),
        ("Tenure per Year (Protective)", 0.684, 0.65, 0.72, GREEN),
        ("Tech Support Active (Protective)", 0.531, 0.46, 0.61, GREEN),
    ]
    y_pos = np.arange(len(factors))
    axes[1, 1].axvline(1.0, color=INK, linewidth=1.2, linestyle="--", label="Neutral (OR = 1.0)")
    for i, (name, or_val, ci_l, ci_u, col) in enumerate(factors):
        axes[1, 1].errorbar(or_val, i, xerr=[[or_val - ci_l], [ci_u - or_val]],
                            fmt="o", color=col, ecolor=col, elinewidth=2.5, capsize=4, markersize=8, zorder=3)
        axes[1, 1].text(or_val, i + 0.25, f"OR: {or_val:.2f}x", ha="center", va="bottom",
                        fontweight="bold", fontsize=9, color=col)

    axes[1, 1].set_yticks(y_pos)
    axes[1, 1].set_yticklabels([f[0] for f in factors])
    axes[1, 1].set_title("D. Risk Factors: Logistic Regression Odds Ratios")
    axes[1, 1].set_xlabel("Odds Ratio (95% CI)")
    axes[1, 1].set_xlim(0.2, 3.8)
    axes[1, 1].set_ylim(-0.5, len(factors) - 0.2)

    fig.suptitle("TELCO CUSTOMER CHURN & RETENTION DRIVERS DASHBOARD",
                 fontsize=14, fontweight="bold", y=0.98, color=INK)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    out = FIG / "00_dashboard_preview.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Generated {out}")


if __name__ == "__main__":
    generate()
