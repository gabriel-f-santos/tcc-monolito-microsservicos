"""Reference test_integration_contract.py — copiar para tests/ de cada servico.

Teste-guardiao que valida o INTEGRATION-CONTRACT.md:
- Regra 1: toda env var do template.yaml e lida pelo codigo src/
- Regra 2: nao ha fallback condicional InMemory em producao
- Regra 3 (soft): arquivos em src/infrastructure/ que importam boto3 nao
  fazem chamadas em import-time

Deve passar ANTES de qualquer teste de comportamento.
"""
from __future__ import annotations

import pathlib
import re


SERVICE_ROOT = pathlib.Path(__file__).parent.parent


def _read_template() -> str:
    return (SERVICE_ROOT / "template.yaml").read_text()


def _all_src_code() -> str:
    return "\n".join(
        p.read_text()
        for p in SERVICE_ROOT.joinpath("src").rglob("*.py")
        if "__pycache__" not in str(p)
    )


def _env_vars_declared_in_template() -> set[str]:
    """Extrai os nomes das env vars em Environment.Variables via scanner simples."""
    text = _read_template()
    lines = text.splitlines()
    env_vars: set[str] = set()

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip() == "Variables:":
            base_indent = len(line) - len(line.lstrip())
            i += 1
            while i < len(lines):
                child = lines[i]
                if not child.strip() or child.lstrip().startswith("#"):
                    i += 1
                    continue
                child_indent = len(child) - len(child.lstrip())
                if child_indent <= base_indent:
                    break
                m = re.match(r"\s*([A-Z_][A-Z0-9_]*)\s*:", child)
                if m:
                    env_vars.add(m.group(1))
                i += 1
            continue
        i += 1

    return env_vars


# --- Testes -------------------------------------------------------------------


def test_env_vars_from_template_are_read_by_src_code():
    """Regra 1: toda env var declarada no template.yaml aparece em src/*.py.

    Motivacao: na rodada anterior, auth-service lia `DYNAMODB_TABLE` mas o
    template enviava `USUARIOS_TABLE` → cada Lambda cold-start caiu em
    InMemory, login sempre retornou 401 em producao.
    """
    declared = _env_vars_declared_in_template()
    code = _all_src_code()
    missing = sorted(v for v in declared if v not in code)
    assert not missing, (
        f"Env vars declaradas em template.yaml mas NAO lidas por src/: {missing}.\n"
        f"Regra 1 do INTEGRATION-CONTRACT: o codigo deve usar EXATAMENTE os nomes do template. "
        f"Nao invente variantes como DYNAMODB_TABLE, TABLE_NAME etc."
    )


def test_no_inmemory_fallback_in_production_code():
    """Regra 2: sem branch if env_var → DynamoDB else → InMemory em src/.

    Motivacao: na rodada anterior, estoque-service tinha apenas repos InMemory.
    Em producao, cada Lambda invocation era isolada e perdia o estado. O
    container nem tinha implementacao DynamoDB.
    """
    code = _all_src_code()
    violating_patterns = [
        r"if\s+.*os\.environ[^:]*:[\s\S]{0,400}?InMemory",
        r"if\s+.*os\.getenv[^:]*:[\s\S]{0,400}?InMemory",
        r"_USE_DYNAMO\s*=\s*.*os\.(environ|getenv)",
        r"is_aws\s*=\s*.*os\.(environ|getenv)",
        r"except\s+KeyError[\s\S]{0,200}?InMemory",
        r"except\s+Exception[\s\S]{0,200}?InMemory",
        r"AWS_LAMBDA_FUNCTION_NAME[\s\S]{0,200}?InMemory",
    ]
    hits = [p for p in violating_patterns if re.search(p, code)]
    assert not hits, (
        "Detectado fallback condicional InMemory em src/ (padroes: "
        f"{hits}).\nRegra 2 do contrato: producao SEMPRE usa DynamoDB. "
        "Testes usam moto via conftest.py. Remova o branch InMemory de src/."
    )


def test_no_aws_calls_at_module_import_time():
    """Regra 5: nenhuma operacao AWS em nivel de modulo (coluna 0).

    Motivacao: quando handlers cacheiam `Table(...)` ou chamam `get_item()`
    em import-time, o pytest importa o modulo DURANTE a coleta, ANTES do
    conftest conseguir ativar mock_aws(). Resultado: os testes quebram com
    erro de credenciais em vez de erro de comportamento claro, e confundem
    a IA que vai tentar "consertar" de formas erradas. Alem disso, em
    producao com cold starts agressivos a chamada de import-time aumenta
    init_duration.
    """
    for py in SERVICE_ROOT.joinpath("src").rglob("*.py"):
        if "__pycache__" in str(py):
            continue
        text = py.read_text()
        lines = text.splitlines()
        # Heuristica: linha comecando na coluna 0 (sem indentacao) que
        # contem uma chamada boto3/DynamoDB/SNS/SQS. Excluir import e def.
        bad_tokens = (
            "boto3.resource(",
            "boto3.client(",
            ".put_item(",
            ".get_item(",
            ".update_item(",
            ".delete_item(",
            ".scan(",
            ".query(",
            ".publish(",
            ".send_message(",
        )
        for lineno, line in enumerate(lines, start=1):
            if not line or line[0] in " \t":
                continue  # indentado — dentro de funcao/classe
            if line.startswith(("import ", "from ", "def ", "class ", "async def ", "#")):
                continue
            for tok in bad_tokens:
                if tok in line:
                    raise AssertionError(
                        f"{py.relative_to(SERVICE_ROOT)}:{lineno} tem chamada AWS em "
                        f"nivel de modulo: {line.strip()!r}. Regra 5: mova para dentro "
                        f"de uma funcao. Lambdas caches de `Table(...)` podem ser feitos "
                        f"com um singleton LAZY (funcao get_table() que cacheia em dict)."
                    )


def test_event_consumers_do_not_only_log():
    """Regra 4 (heuristica): event_consumer.py deve conter chamada de escrita.

    Motivacao: na rodada anterior, estoque-service-mvc tinha event_consumer
    que so logava — nunca persistia o ItemEstoque criado pelo evento
    ProdutoCriado. O handler retornava 200 e os testes passavam porque
    consultavam um dict in-memory que virou lixo em producao.
    """
    consumer = SERVICE_ROOT / "src" / "handlers" / "event_consumer.py"
    if not consumer.exists():
        return  # servico sem event consumer — skip
    code = consumer.read_text()
    has_write = any(
        marker in code
        for marker in ("put_item", "update_item", ".save(", "repository.save", "Table(")
    )
    assert has_write, (
        "event_consumer.py nao tem nenhuma chamada de escrita (put_item/update_item/save/Table(). "
        "Regra 4: event consumers DEVEM persistir no DynamoDB."
    )
