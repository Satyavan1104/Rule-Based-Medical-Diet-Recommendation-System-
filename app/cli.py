import argparse
import json
from pathlib import Path

from app.data.schema import load_profile_json
from app.services.recommender import recommend


def main():
    parser = argparse.ArgumentParser(description="Rule-Based Medical Diet Recommender CLI")
    parser.add_argument("--input", required=True, help="Path to input JSON profile")
    parser.add_argument("--save", required=False, default=None, help="Path to save output JSON")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON to stdout")
    args = parser.parse_args()

    profile = load_profile_json(args.input)
    result = recommend(profile)

    if args.pretty:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))

    if args.save:
        out_path = Path(args.save)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Saved output to: {out_path}")


if __name__ == "__main__":
    main()
