#!/usr/bin/env bash
set -euo pipefail

# Destrói todas as stacks SAM do TCC (microsserviços + variantes MVC).
# Uso:
#   ./destroy-sam-stacks.sh           # pede confirmação por stack
#   ./destroy-sam-stacks.sh --yes     # sem prompts (CUIDADO)

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MS_DIR="${REPO_ROOT}/microsservicos"

# sam só existe no pyenv 3.11.13 nessa máquina. O shim global do pyenv
# (~/.pyenv/shims/sam) resolve pra outra versão e falha — então pulamos
# qualquer caminho de shim e vamos direto no binário versionado.
SAM_BIN="${SAM_BIN:-}"
if [[ -n "$SAM_BIN" && "$SAM_BIN" == *"/shims/"* ]]; then
  echo "!! SAM_BIN aponta pra um shim do pyenv ($SAM_BIN); ignorando." >&2
  SAM_BIN=""
fi
if [[ -z "$SAM_BIN" ]]; then
  if [[ -x "$HOME/.pyenv/versions/3.11.13/bin/sam" ]]; then
    SAM_BIN="$HOME/.pyenv/versions/3.11.13/bin/sam"
  elif command -v pyenv >/dev/null 2>&1; then
    CAND="$(PYENV_VERSION=3.11.13 pyenv which sam 2>/dev/null || true)"
    [[ -n "$CAND" && "$CAND" != *"/shims/"* && -x "$CAND" ]] && SAM_BIN="$CAND"
  fi
  if [[ -z "$SAM_BIN" ]]; then
    CAND="$(command -v sam 2>/dev/null || true)"
    [[ -n "$CAND" && "$CAND" != *"/shims/"* && -x "$CAND" ]] && SAM_BIN="$CAND"
  fi
fi
if [[ -z "$SAM_BIN" || ! -x "$SAM_BIN" ]]; then
  echo "!! sam CLI não encontrado fora dos shims. Defina SAM_BIN=/caminho/para/sam." >&2
  exit 1
fi
SAM_VERSION="$("$SAM_BIN" --version 2>&1 || true)"
if [[ "$SAM_VERSION" != *"SAM CLI"* ]]; then
  echo "!! '$SAM_BIN --version' não retornou versão válida: $SAM_VERSION" >&2
  exit 1
fi
echo ">> Usando sam: $SAM_BIN ($SAM_VERSION)"

# Ordem importa: estoque importa exports de catalogo e auth; catalogo
# importa exports de auth. Tem que destruir das folhas pras raízes,
# senão CloudFormation cancela o delete por export em uso.
SERVICES=(
  "estoque-service"
  "estoque-service-mvc"
  "catalogo-service"
  "catalogo-service-mvc"
  "auth-service"
  "auth-service-mvc"
)

NO_PROMPTS=""
if [[ "${1:-}" == "--yes" || "${1:-}" == "-y" ]]; then
  NO_PROMPTS="--no-prompts"
  echo ">> Modo sem confirmação ativado."
fi

echo ">> Vai destruir as seguintes stacks na AWS (us-east-1):"
for s in "${SERVICES[@]}"; do
  echo "   - tcc-${s}"
done
echo

if [[ -z "$NO_PROMPTS" ]]; then
  read -rp "Confirma? (digite 'destroy' para prosseguir): " CONFIRM
  [[ "$CONFIRM" == "destroy" ]] || { echo "Abortado."; exit 1; }
fi

FAILED=()
for svc in "${SERVICES[@]}"; do
  DIR="${MS_DIR}/${svc}"
  echo
  echo "================================================"
  echo ">> Destruindo: ${svc} (${DIR})"
  echo "================================================"

  if [[ ! -f "${DIR}/samconfig.toml" ]]; then
    echo "!! samconfig.toml não encontrado em ${DIR}, pulando."
    FAILED+=("${svc} (sem samconfig)")
    continue
  fi

  STACK_NAME="$(grep -E '^stack_name' "${DIR}/samconfig.toml" | head -1 | sed -E 's/.*"([^"]+)".*/\1/')"
  STACK_REGION="$(grep -E '^region' "${DIR}/samconfig.toml" | head -1 | sed -E 's/.*"([^"]+)".*/\1/')"
  if command -v aws >/dev/null 2>&1 && [[ -n "$STACK_NAME" && -n "$STACK_REGION" ]]; then
    if ! aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$STACK_REGION" >/dev/null 2>&1; then
      echo ">> Stack ${STACK_NAME} não existe na AWS, pulando."
      continue
    fi
  fi

  if (cd "${DIR}" && "$SAM_BIN" delete ${NO_PROMPTS}); then
    echo ">> OK: ${svc} destruída."
  else
    echo "!! Falha ao destruir ${svc}."
    FAILED+=("${svc}")
  fi
done

echo
echo "================================================"
if [[ ${#FAILED[@]} -eq 0 ]]; then
  echo ">> Todas as stacks destruídas com sucesso."
else
  echo "!! Algumas stacks falharam:"
  for f in "${FAILED[@]}"; do echo "   - $f"; done
  exit 1
fi
