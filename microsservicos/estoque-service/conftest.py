"""Reference conftest.py — copiar para cada servico sem modificacoes.

Lê o `template.yaml` do servico, cria tabelas DynamoDB, topicos SNS e filas
SQS em moto, resolve refs (!Ref) para nomes/ARNs reais e popula os.environ
com as mesmas env vars que o Lambda teria em producao.

Resultado: qualquer teste do servico roda contra um AWS totalmente mockado
mas exerce o MESMO caminho de codigo que o deploy real, eliminando a classe
de bugs "codigo passa local, falha em producao" (ver INTEGRATION-CONTRACT.md).

Requer: moto[all], pyyaml. Ambos em requirements-dev.txt.
"""
from __future__ import annotations

import os
import pathlib
import sys

import boto3
import pytest
import yaml
from moto import mock_aws


# --- SAM YAML parsing ---------------------------------------------------------


class _SAMLoader(yaml.SafeLoader):
    """Loader que preserva intrinsics do CloudFormation/SAM como dicts."""


def _sam_tag_constructor(loader: yaml.SafeLoader, tag_suffix: str, node):
    if isinstance(node, yaml.ScalarNode):
        value = loader.construct_scalar(node)
    elif isinstance(node, yaml.SequenceNode):
        value = loader.construct_sequence(node)
    else:
        value = loader.construct_mapping(node)
    return {f"!{tag_suffix}": value}


_SAMLoader.add_multi_constructor("!", _sam_tag_constructor)


SERVICE_ROOT = pathlib.Path(__file__).parent


def _load_template() -> dict:
    with (SERVICE_ROOT / "template.yaml").open() as f:
        return yaml.load(f, Loader=_SAMLoader)


def _resolve(value, resource_map: dict[str, str]):
    """Resolve !Ref / !GetAtt / !ImportValue / !Sub em valor de env var."""
    if isinstance(value, dict):
        if "!Ref" in value:
            ref = value["!Ref"]
            return resource_map.get(ref, f"ref-{ref}")
        if "!GetAtt" in value:
            att = value["!GetAtt"]
            if isinstance(att, list):
                att = ".".join(str(a) for a in att)
            target = str(att).split(".", 1)[0]
            return resource_map.get(target, f"getatt-{att}")
        if "!ImportValue" in value:
            return f"import-{value['!ImportValue']}"
        if "!Sub" in value:
            return str(value["!Sub"])
    return value


def _create_aws_resources(tpl: dict) -> dict[str, str]:
    """Cria tabelas/topicos/filas em moto. Retorna {logical_id: phys_name_or_arn}."""
    resources = tpl.get("Resources", {})
    resource_map: dict[str, str] = {}

    # Parameters com defaults viram valores resolvidos
    for name, param in (tpl.get("Parameters") or {}).items():
        resource_map[name] = str(param.get("Default", f"param-{name}"))

    # DynamoDB
    ddb = boto3.resource("dynamodb", region_name="us-east-1")
    for logical_id, res in resources.items():
        if res.get("Type") != "AWS::DynamoDB::Table":
            continue
        props = res["Properties"]
        table_name = props.get("TableName", logical_id)
        if isinstance(table_name, dict):  # se for !Sub ou outro intrinsic
            table_name = logical_id
        ddb.create_table(
            TableName=str(table_name),
            KeySchema=props["KeySchema"],
            AttributeDefinitions=props["AttributeDefinitions"],
            BillingMode=props.get("BillingMode", "PAY_PER_REQUEST"),
        )
        resource_map[logical_id] = str(table_name)

    # SNS topics
    sns = boto3.client("sns", region_name="us-east-1")
    for logical_id, res in resources.items():
        if res.get("Type") != "AWS::SNS::Topic":
            continue
        name = res["Properties"].get("TopicName", logical_id)
        if isinstance(name, dict):
            name = logical_id
        arn = sns.create_topic(Name=str(name))["TopicArn"]
        resource_map[logical_id] = arn

    # SQS queues
    sqs = boto3.client("sqs", region_name="us-east-1")
    for logical_id, res in resources.items():
        if res.get("Type") != "AWS::SQS::Queue":
            continue
        name = res["Properties"].get("QueueName", logical_id)
        if isinstance(name, dict):
            name = logical_id
        url = sqs.create_queue(QueueName=str(name))["QueueUrl"]
        resource_map[logical_id] = url

    return resource_map


def _set_env_vars(tpl: dict, resource_map: dict[str, str]) -> None:
    for res in tpl.get("Resources", {}).values():
        if res.get("Type") != "AWS::Serverless::Function":
            continue
        env_vars = (
            res.get("Properties", {}).get("Environment", {}).get("Variables", {}) or {}
        )
        for key, raw in env_vars.items():
            os.environ[key] = str(_resolve(raw, resource_map))


def _purge_src_modules() -> None:
    """Evita que caches em modulos ja importados mascarem as env vars."""
    for name in list(sys.modules.keys()):
        if name == "src" or name.startswith("src."):
            del sys.modules[name]


# --- Fixtures -----------------------------------------------------------------


@pytest.fixture(scope="function", autouse=True)
def aws_mocked():
    """Fixture autouse que sobe mock_aws + recursos do template a cada teste."""
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"

    with mock_aws():
        tpl = _load_template()
        resource_map = _create_aws_resources(tpl)
        _set_env_vars(tpl, resource_map)
        _purge_src_modules()
        yield resource_map


@pytest.fixture
def dynamodb():
    """boto3 DynamoDB resource apontando pro moto."""
    return boto3.resource("dynamodb", region_name="us-east-1")


@pytest.fixture
def sns():
    return boto3.client("sns", region_name="us-east-1")


@pytest.fixture
def sqs():
    return boto3.client("sqs", region_name="us-east-1")
