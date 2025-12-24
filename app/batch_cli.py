import argparse
import json
from pathlib import Path

from app.data.dataset import load_users_csv
from app.services.recommender import recommend


def main():
    parser = argparse.ArgumentParser(description="Batch recommend from CSV of user profiles")
    parser.add_argument("--csv", required=True, help="Path to users CSV")
    parser.add_argument("--outdir", required=True, help="Directory to write JSON outputs per row")
    args = parser.parse_args()

    profiles = load_users_csv(args.csv)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    for idx, profile in enumerate(profiles, start=1):
        result = recommend(profile)
        out_path = outdir / f"profile_{idx:03d}.json"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
