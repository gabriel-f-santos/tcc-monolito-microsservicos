#!/bin/bash
# Compara codigo do monolito vs microsservicos para medir reuso na migracao
# Uso: bash scripts/compare-migration.sh

set -euo pipefail

MONO="monolito/src"
MICRO="microsservicos"

echo "============================================================"
echo "  COMPARACAO DE MIGRACAO: MONOLITO vs MICROSSERVICOS"
echo "============================================================"
echo ""

TOTAL_FILES=0
IDENTICAL_FILES=0
IMPORT_ONLY_FILES=0
NEW_FILES=0
MODIFIED_FILES=0

declare -A SERVICE_MAP
SERVICE_MAP["auth"]="auth-service"
SERVICE_MAP["catalogo"]="catalogo-service"
SERVICE_MAP["estoque"]="estoque-service"

for BC in auth catalogo estoque; do
    SVC="${SERVICE_MAP[$BC]}"
    MONO_BC="$MONO/$BC"
    MICRO_BC="$MICRO/$SVC/src"

    echo "------------------------------------------------------------"
    echo "  BC: $BC → $SVC"
    echo "------------------------------------------------------------"

    BC_TOTAL=0
    BC_IDENTICAL=0
    BC_IMPORT=0
    BC_NEW=0
    BC_MODIFIED=0

    for LAYER in domain application; do
        if [ ! -d "$MICRO_BC/$LAYER" ]; then continue; fi

        for MICRO_FILE in $(find "$MICRO_BC/$LAYER" -name "*.py" ! -name "__init__.py" 2>/dev/null | sort); do
            REL_PATH=$(echo "$MICRO_FILE" | sed "s|$MICRO_BC/||")
            MONO_FILE="$MONO_BC/$REL_PATH"
            FILENAME=$(basename "$MICRO_FILE")
            BC_TOTAL=$((BC_TOTAL + 1))

            if [ ! -f "$MONO_FILE" ]; then
                echo "  [NEW]         $LAYER/$FILENAME"
                BC_NEW=$((BC_NEW + 1))
            else
                # Compare ignoring import paths
                DIFF_FULL=$(diff "$MICRO_FILE" "$MONO_FILE" 2>/dev/null || true)
                DIFF_NO_IMPORTS=$(diff <(grep -v "^from src\." "$MICRO_FILE" | grep -v "^import ") \
                                      <(grep -v "^from src\." "$MONO_FILE" | grep -v "^import ") 2>/dev/null || true)

                if [ -z "$DIFF_FULL" ]; then
                    echo "  [IDENTICAL]   $LAYER/$FILENAME"
                    BC_IDENTICAL=$((BC_IDENTICAL + 1))
                elif [ -z "$DIFF_NO_IMPORTS" ]; then
                    IMPORT_CHANGES=$(echo "$DIFF_FULL" | grep "^[<>]" | wc -l)
                    echo "  [IMPORT-ONLY] $LAYER/$FILENAME ($((IMPORT_CHANGES / 2)) import(s) changed)"
                    BC_IMPORT=$((BC_IMPORT + 1))
                else
                    CHANGES=$(echo "$DIFF_FULL" | grep "^[<>]" | wc -l)
                    echo "  [MODIFIED]    $LAYER/$FILENAME ($CHANGES lines differ)"
                    BC_MODIFIED=$((BC_MODIFIED + 1))
                fi
            fi
        done
    done

    # Count infra+presentation (all new)
    for LAYER in infrastructure presentation; do
        NEW_COUNT=$(find "$MICRO_BC/$LAYER" -name "*.py" ! -name "__init__.py" 2>/dev/null | wc -l)
        BC_NEW=$((BC_NEW + NEW_COUNT))
        BC_TOTAL=$((BC_TOTAL + NEW_COUNT))
    done
    [ -f "$MICRO_BC/container.py" ] && BC_NEW=$((BC_NEW + 1)) && BC_TOTAL=$((BC_TOTAL + 1))

    REUSED=$((BC_IDENTICAL + BC_IMPORT))
    if [ $BC_TOTAL -gt 0 ]; then
        PCT=$((REUSED * 100 / BC_TOTAL))
    else
        PCT=0
    fi

    echo ""
    echo "  Resumo $BC:"
    echo "    Identicos:    $BC_IDENTICAL"
    echo "    Import-only:  $BC_IMPORT"
    echo "    Modificados:  $BC_MODIFIED"
    echo "    Novos:        $BC_NEW"
    echo "    Total:        $BC_TOTAL"
    echo "    Reutilizado:  $REUSED/$BC_TOTAL ($PCT%)"
    echo ""

    TOTAL_FILES=$((TOTAL_FILES + BC_TOTAL))
    IDENTICAL_FILES=$((IDENTICAL_FILES + BC_IDENTICAL))
    IMPORT_ONLY_FILES=$((IMPORT_ONLY_FILES + BC_IMPORT))
    NEW_FILES=$((NEW_FILES + BC_NEW))
    MODIFIED_FILES=$((MODIFIED_FILES + BC_MODIFIED))
done

echo "============================================================"
echo "  TOTAIS"
echo "============================================================"
REUSED_TOTAL=$((IDENTICAL_FILES + IMPORT_ONLY_FILES))
if [ $TOTAL_FILES -gt 0 ]; then
    PCT_TOTAL=$((REUSED_TOTAL * 100 / TOTAL_FILES))
else
    PCT_TOTAL=0
fi

echo ""
echo "  Arquivos identicos (zero diff):   $IDENTICAL_FILES"
echo "  Arquivos import-only (so path):   $IMPORT_ONLY_FILES"
echo "  Arquivos modificados (logica):    $MODIFIED_FILES"
echo "  Arquivos novos (infra+present):   $NEW_FILES"
echo "  Total de arquivos:                $TOTAL_FILES"
echo ""
echo "  CODIGO REUTILIZADO: $REUSED_TOTAL/$TOTAL_FILES ($PCT_TOTAL%)"
echo "  CODIGO NOVO:        $NEW_FILES/$TOTAL_FILES ($((NEW_FILES * 100 / TOTAL_FILES))%)"
echo ""
echo "  Conclusao: Domain e Application foram migrados com"
echo "  $((IDENTICAL_FILES + IMPORT_ONLY_FILES)) de $((IDENTICAL_FILES + IMPORT_ONLY_FILES + MODIFIED_FILES)) arquivos"
echo "  sem alteracao de logica (apenas import paths)."
echo "  Isso comprova que DDD/Clean Architecture isolou"
echo "  a logica de negocio da infraestrutura."
echo ""
