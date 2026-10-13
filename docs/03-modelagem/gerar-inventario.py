"""Gera documentação do schema sem conexão com o banco publicado.

Executar na raiz: .venv/bin/python docs/03-modelagem/gerar-inventario.py
Usa o estado final das migrations e tipos do backend PostgreSQL, sem executar SQL.
"""

import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.test"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
sys.path.insert(0, str(ROOT / "src"))

import django  # noqa: E402

django.setup()

from django.db import connections  # noqa: E402
from django.db.backends.base.schema import BaseDatabaseSchemaEditor  # noqa: E402
from django.db.backends.postgresql.base import DatabaseWrapper  # noqa: E402
from django.db.backends.postgresql.schema import DatabaseSchemaEditor  # noqa: E402
from django.db.migrations.loader import MigrationLoader  # noqa: E402

OUT = Path(__file__).parent
DOMAIN = {"accounts", "people", "workshops", "enrollments", "learning"}
connection = DatabaseWrapper({"NAME": "documentacao_offline"}, alias="documentacao_offline")


def deny_connection(*args, **kwargs):
    raise RuntimeError("Este gerador não permite conexão com banco de dados.")


connection.ensure_connection = deny_connection
connection.cursor = deny_connection
# Integer validators use the default backend's ranges, even without SQL.
connections["default"] = connection


class OfflineSchemaEditor(DatabaseSchemaEditor):
    def execute(self, sql, params=()):
        return BaseDatabaseSchemaEditor.execute(self, sql, params)


loader = MigrationLoader(None)
state = loader.project_state()
models = sorted(state.apps.get_models(), key=lambda model: model._meta.db_table)
inventory = []
for model in models:
    meta = model._meta
    fields = []
    for field in meta.local_fields:
        item = {
            "field": field.name,
            "column": field.column,
            "django_type": field.get_internal_type(),
            "postgresql_type": field.db_type(connection),
            "null": field.null,
            "blank": field.blank,
            "primary_key": field.primary_key,
            "unique": field.unique,
            "db_index": field.db_index,
            "choices": list(field.flatchoices),
            "validators": [
                f"{v.__class__.__name__}({getattr(v, 'limit_value', '')})"
                if not hasattr(v, "__name__")
                else v.__name__
                for v in field.validators
            ],
        }
        if field.has_default():
            default = field.default
            item["python_default"] = (
                f"{default.__module__}.{default.__name__}" if callable(default) else str(default)
            )
        if getattr(field, "auto_now", False):
            item["automatic"] = "auto_now"
        if getattr(field, "auto_now_add", False):
            item["automatic"] = "auto_now_add"
        if field.is_relation:
            item["references"] = field.remote_field.model._meta.db_table + ".id"
            item["on_delete_orm"] = field.remote_field.on_delete.__name__
        fields.append(item)
    inventory.append(
        {
            "model": meta.label,
            "table": meta.db_table,
            "domain": meta.app_label in DOMAIN,
            "fields": fields,
            "constraints": [repr(c) for c in meta.constraints],
            "indexes": [repr(i) for i in meta.indexes],
            "unique_together": list(meta.unique_together),
            "many_to_many": [
                {"field": f.name, "table": f.remote_field.through._meta.db_table}
                for f in meta.local_many_to_many
            ],
        }
    )
migrations = []
for key, migration in sorted(loader.disk_migrations.items()):
    if key[0] not in DOMAIN:
        continue
    path = ROOT / "src/apps" / key[0] / "migrations" / (key[1] + ".py")
    migrations.append(
        {
            "app": key[0],
            "name": key[1],
            "path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "dependencies": migration.dependencies,
            "operations": [operation.__class__.__name__ for operation in migration.operations],
        }
    )
result = {
    "source": "estado final das migrations conferido com models; sem consulta ao banco",
    "django": django.get_version(),
    "models": inventory,
    "project_migrations": migrations,
}
(OUT / "inventario-schema.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2, default=str) + "\n"
)

lines = [
    "# Dicionário de dados implementado",
    "",
    "Gerado por [gerar-inventario.py](gerar-inventario.py), com o Django fixado em `uv.lock`. "
    "A fonte é o código, sem consulta ou escrita no banco publicado. "
    "Veja [inventário completo](inventario-schema.json) e [banco físico](banco-fisico.md).",
    "",
    "## Convenções",
    "",
    "`NULL` é nulabilidade SQL; `blank` permite ausência na validação de formulário. "
    "Texto com blank=sim e NULL=não usa string vazia. PK e UNIQUE são restrições SQL; "
    "choices e validadores são regras Python, salvo CHECK explícito. "
    "Defaults, UUIDs e datas automáticas são preenchidos pelo Python, não "
    "defaults SQL permanentes. "
    "PROTECT/CASCADE indicam a política do coletor Django, não cláusulas ON "
    "DELETE equivalentes no PostgreSQL.",
    "",
    "Há 16 modelos próprios persistentes; core possui base abstrata e "
    "reporting não possui tabelas. "
    "As tabelas do framework e as associações de autorização também estão listadas. "
    "`django_migrations` é mantida pelo executor de migrations (id bigint, app varchar(255), "
    "name varchar(255), applied timestamptz, todos NOT NULL; id PK), não por um modelo instalado.",
]
for item in inventory:
    lines += [
        "",
        f"## {item['table']}",
        "",
        f"Modelo: `{item['model']}`. "
        + ("Domínio do projeto." if item["domain"] else "Infraestrutura Django."),
        "",
        "| Coluna (campo) | Tipo PostgreSQL | NULL | blank | Chaves/índice | "
        "Regras e preenchimento |",
        "|---|---|---|---|---|---|",
    ]
    for field in item["fields"]:
        keys = []
        if field["primary_key"]:
            keys.append("PK")
        elif field["unique"]:
            keys.append("UNIQUE")
        elif field["db_index"]:
            keys.append("INDEX")
        if "references" in field:
            keys.append("FK → " + field["references"] + "; ORM " + field["on_delete_orm"])
        rules = [v for v in field["validators"] if v]
        if field["choices"]:
            rules.append("choices: " + ", ".join(str(k) for k, _ in field["choices"]))
        if "python_default" in field:
            rules.append("default Python: " + field["python_default"])
        if "automatic" in field:
            rules.append(field["automatic"])
        if field["django_type"] in {"AutoField", "BigAutoField"}:
            rules.append("identity SQL")
        cells = [
            f"`{field['column']}` ({field['field']})",
            field["postgresql_type"],
            "sim" if field["null"] else "não",
            "sim" if field["blank"] else "não",
            "; ".join(keys) or "—",
            "; ".join(rules).replace("|", "&#124;") or "—",
        ]
        lines.append("| " + " | ".join(cells) + " |")
    if item["constraints"]:
        lines += ["", "Restrições explícitas do modelo:", ""] + [
            "- `" + s.replace("`", "") + "`" for s in item["constraints"]
        ]
    if item["indexes"]:
        lines += ["", "Índices explícitos:", ""] + ["- `" + s + "`" for s in item["indexes"]]
    if item["unique_together"]:
        lines += ["", "Unicidade composta SQL: `" + repr(item["unique_together"]) + "`."]
    for assoc in item["many_to_many"]:
        through = (
            state.apps.get_model(item["model"])._meta.get_field(assoc["field"]).remote_field.through
        )
        columns = []
        for field in through._meta.local_fields:
            description = f"{field.column}: {field.db_type(connection)}, NOT NULL"
            if field.primary_key:
                description += ", PK identity"
            if field.is_relation:
                target = field.remote_field.model._meta.db_table
                description += f", FK → {target}.id, INDEX, ORM CASCADE"
            columns.append(description)
        columns = "; ".join(columns)
        lines += [
            "",
            f"Associação `{assoc['field']}`: tabela `{assoc['table']}`; {columns}. "
            f"PK id; FKs com índice; UNIQUE {through._meta.unique_together}.",
        ]
lines += [
    "",
    "## Regras entre entidades e valores derivados",
    "",
    "- Idade 14–21 no início e responsável ativo para menor na inscrição: "
    "people/enrollments services; não são CHECK SQL.",
    "- Uma turma pode ter zero instrutores enquanto planejada; abrir/iniciar "
    "exige instrutor ativo e iniciar exige encontro planejado.",
    "- Frequência liga inscrição e encontro da mesma turma: Attendance.clean "
    "e seleção do serviço. A FK isolada não verifica essa igualdade.",
    "- Vagas operacionais contam CONFIRMED; painel histórico conta "
    "CONFIRMED/APPROVED/NOT_COMPLETED. Fila usa waitlisted_at, created_at e "
    "PK como desempate.",
    "- Frequência usa PRESENT / encontros COMPLETED já terminados; JUSTIFIED "
    "não conta presença. Percentual é calculado, não coluna.",
    "- Aprovação exige frequência ≥75%, nota ≥6 e projeto entregue; "
    "conclusão exige todos os encontros não cancelados processados e "
    "avaliações registradas.",
    "- Certificate.enrollment_id é UNIQUE para todo o histórico: há no "
    "máximo um certificado por inscrição, mesmo revogado; o MVP não reemite "
    "revogado. workload_hours é snapshot na emissão; PDF usa nomes/dados "
    "relacionados na consulta, sem snapshot integral do cadastro.",
    "- Histórico da inscrição é imutável pelos fluxos/admin; "
    "frequência/avaliação conservam última autoria/data, sem log de todas as "
    "versões.",
    "- CPF/CNPJ opcionais são normalizados para NULL quando vazios e "
    "validados em Python; hashes de senha e sessões nunca são evidência "
    "pública.",
    "",
]
(OUT / "dicionario-de-dados.md").write_text("\n".join(lines))

with OfflineSchemaEditor(connection, collect_sql=True, atomic=False) as editor:
    for model in sorted(state.apps.get_models(), key=lambda model: model._meta.db_table):
        editor.create_model(model)
sql = (
    "-- Referência do estado final das migrations, gerada offline. NÃO é um "
    "dump da VPS.\n-- Não substituir migrate por este arquivo. Nenhum SQL foi "
    "executado.\n" + "\n".join(editor.collected_sql) + "\n"
)
(OUT / "schema-postgresql.sql").write_text(sql)
logical = [
    "# Modelo lógico relacional",
    "",
    "Derivado dos modelos e migrations atuais. Cardinalidades e dependências "
    "funcionais estão em [modelo-de-dados.md](modelo-de-dados.md). Tipos e "
    "nulabilidade: [dicionário](dicionario-de-dados.md).",
    "",
    "Cada relação abaixo lista todas as colunas; PK/FK/UK são chaves "
    "físicas, não nomes conceituais fictícios.",
    "",
]
for item in inventory:
    if not item["domain"]:
        continue
    fields = ", ".join(
        f["column"]
        + (" [PK]" if f["primary_key"] else " [UK]" if f["unique"] else "")
        + (" [FK]" if "references" in f else "")
        for f in item["fields"]
    )
    logical += [f"## {item['table']}", "", f"`{item['table']}({fields})`", ""]
    logical += [
        f"- `{f['column']}` → `{f['references']}`; {'opcional' if f['null'] else 'obrigatória'}."
        for f in item["fields"]
        if "references" in f
    ]
    logical += [f"- Restrição: `{c}`." for c in item["constraints"]]
    logical.append("")
(OUT / "modelo-logico.md").write_text("\n".join(logical))
print(
    json.dumps(
        {
            "domain_models": sum(i["domain"] for i in inventory),
            "project_migrations": len(migrations),
            "sql_statements": len(editor.collected_sql),
            "database_connections": 0,
        }
    )
)
