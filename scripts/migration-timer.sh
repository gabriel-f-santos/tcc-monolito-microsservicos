#!/bin/bash
# migration-timer.sh — grava start/end timestamps por servico em paralelo
# Uso:
#   bash scripts/migration-timer.sh start <service-name>
#   bash scripts/migration-timer.sh end <service-name>
#
# Ao rodar "end", calcula o delta e append em metrics/migration-times/summary.csv
# com colunas: service,start_ts,end_ts,elapsed_seconds,elapsed_minutes

set -euo pipefail

ACTION="${1:-}"
SERVICE="${2:-}"

if [[ -z "$ACTION" || -z "$SERVICE" ]]; then
    echo "Uso: $0 start|end <service-name>" >&2
    exit 1
fi

# Sempre resolver a raiz do projeto a partir do diretorio do script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
TIMES_DIR="$ROOT_DIR/metrics/migration-times"
mkdir -p "$TIMES_DIR"

case "$ACTION" in
    start)
        TS=$(date +%s.%N)
        echo "$TS" > "$TIMES_DIR/${SERVICE}.start"
        echo "[timer] $SERVICE START @ $(date -Iseconds)"
        ;;
    end)
        END_TS=$(date +%s.%N)
        START_FILE="$TIMES_DIR/${SERVICE}.start"
        if [[ ! -f "$START_FILE" ]]; then
            echo "[timer] ERRO: sem start registrado para $SERVICE" >&2
            exit 2
        fi
        START_TS=$(cat "$START_FILE")
        ELAPSED=$(awk "BEGIN { printf \"%.3f\", $END_TS - $START_TS }")
        MINUTES=$(awk "BEGIN { printf \"%.2f\", ($END_TS - $START_TS) / 60 }")
        echo "$END_TS" > "$TIMES_DIR/${SERVICE}.end"

        SUMMARY="$TIMES_DIR/summary.csv"
        if [[ ! -f "$SUMMARY" ]]; then
            echo "service,start_ts,end_ts,elapsed_seconds,elapsed_minutes" > "$SUMMARY"
        fi
        echo "${SERVICE},${START_TS},${END_TS},${ELAPSED},${MINUTES}" >> "$SUMMARY"

        echo "[timer] $SERVICE END   @ $(date -Iseconds) — elapsed=${ELAPSED}s (${MINUTES}min)"
        ;;
    *)
        echo "Acao invalida: $ACTION (use start ou end)" >&2
        exit 1
        ;;
esac
