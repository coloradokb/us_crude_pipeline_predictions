from __future__ import annotations

import argparse
import json

from pipeline_pred.config import load_settings
from pipeline_pred.service import (
    backfill_recent_predictions,
    generate_prediction,
    ingest_eia,
    initialize_database,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="WCESTUS1 prediction platform")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-db", help="Create or migrate the local database")

    ingest_parser = subparsers.add_parser("ingest", help="Fetch source data from EIA")
    ingest_parser.add_argument("--start", default="2015-01-01")

    predict_parser = subparsers.add_parser("predict", help="Generate next-week forecast")
    predict_parser.add_argument("--series", default="WCESTUS1")

    backfill_parser = subparsers.add_parser(
        "backfill-history",
        help="Generate historical one-week forecasts with known actuals",
    )
    backfill_parser.add_argument("--series", default="WCESTUS1")
    backfill_parser.add_argument("--weeks", type=int, default=9)

    pipeline_parser = subparsers.add_parser(
        "run-pipeline", help="Run ingest and prediction"
    )
    pipeline_parser.add_argument("--start", default="2015-01-01")
    pipeline_parser.add_argument("--series", default="WCESTUS1")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    settings = load_settings()

    if args.command == "init-db":
        initialize_database(settings)
        print(json.dumps({"status": "ok"}))
    elif args.command == "ingest":
        result = ingest_eia(settings, start=args.start)
        print(json.dumps(result.__dict__, sort_keys=True))
    elif args.command == "predict":
        result = generate_prediction(settings, series=args.series)
        print(json.dumps(result, sort_keys=True))
    elif args.command == "backfill-history":
        result = backfill_recent_predictions(
            settings,
            series=args.series,
            weeks=args.weeks,
        )
        print(json.dumps(result, sort_keys=True))
    elif args.command == "run-pipeline":
        ingest_result = ingest_eia(settings, start=args.start)
        prediction_result = generate_prediction(settings, series=args.series)
        print(
            json.dumps(
                {
                    "ingest": ingest_result.__dict__,
                    "prediction": prediction_result,
                },
                sort_keys=True,
            )
        )
    else:
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
