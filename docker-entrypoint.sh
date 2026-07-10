#!/bin/sh
set -eu

case "${1:-api}" in
    api)
        exec uvicorn pipeline_pred.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
        ;;
    scheduler)
        cron
        exec tail -f /var/log/cron.log
        ;;
    run-pipeline)
        shift
        exec python -m pipeline_pred.cli run-pipeline "$@"
        ;;
    backfill-history)
        shift
        exec python -m pipeline_pred.cli backfill-history "$@"
        ;;
    init-db)
        shift
        exec python -m pipeline_pred.cli init-db "$@"
        ;;
    *)
        exec "$@"
        ;;
esac
