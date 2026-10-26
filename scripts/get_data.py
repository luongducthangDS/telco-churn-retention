"""Download IBM Telco Customer Churn dataset into data/raw/."""
import subprocess
from pathlib import Path

URL = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"

raw_dir = Path(__file__).resolve().parents[1] / "data" / "raw"
raw_dir.mkdir(parents=True, exist_ok=True)
dest = raw_dir / "telco_churn_raw.csv"

if not dest.exists() or dest.stat().st_size < 1000:
    print(f"Downloading Telco Churn dataset from {URL}...")
    subprocess.run(["curl.exe", "-L", URL, "-o", str(dest)], check=True)
    print(f"Saved to {dest} ({dest.stat().st_size:,} bytes)")
else:
    print(f"Telco Churn data already exists at {dest}")
