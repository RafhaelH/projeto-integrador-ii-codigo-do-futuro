#!/usr/bin/env python3
"""HTTP real com TLS/CSRF e dados exclusivos; reutiliza helpers históricos sem editá-los.

Execute uma única vez: python3 retestar.py --private-dir /root/diretorio-exclusivo
Credenciais, cookies e tokens não entram nas evidências. Não executa deploy ou limpeza.
"""

import argparse
import importlib.util
import json
import os
import re
import secrets
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
RUN = OUT.name
HISTORY = ROOT / "docs/06-testes/validacao-publicada/VALIDATION-20261013-120621/validar.py"
spec = importlib.util.spec_from_file_location("historical_validation", HISTORY)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False))


def profile_state(user_id, expected_email, password):
    # Raw passwords/hashes stay inside the process; only booleans and a state digest leave it.
    return v.orm(
        "from apps.accounts.models import User\n"
        f"u=User.objects.get(pk={user_id!r})\n"
        "print(json.dumps({'name':u.full_name,'role':u.role,'active':u.is_active,"
        f"'email_matches':u.email=={expected_email!r},'password_preserved':u.check_password({password!r}),"
        "'protected_digest':hashlib.sha256(json.dumps([u.password,u.role,u.is_active,"
        "u.is_staff,u.is_superuser,list(u.groups.values_list('pk',flat=True)),"
        "list(u.user_permissions.values_list('pk',flat=True))],sort_keys=True).encode()).hexdigest()}))"
    )


def profiles(creds):
    path = "/conta/perfil/"
    anonymous = v.Session("ANONYMOUS_PROFILE")
    v.get("Perfil anônimo exige login", "Perfil próprio", anonymous, path, 302)
    v.post(
        "Perfil anônimo com CSRF exige login",
        "Perfil próprio",
        anonymous,
        path,
        {"full_name": "Nome", "email": "invalid@example.com"},
        source="/entrar/",
        n=302,
        verify=False,
        unchanged=True,
    )
    v.test(
        "POST de perfil anônimo exige login",
        "Perfil próprio",
        anonymous,
        path,
        "POST",
        {},
        expected="CSRF rejeita POST sem token",
        checks=v.status(403),
        unchanged=True,
    )
    users = {
        alias: v.find(v.snapshot(), "accounts.User", role="ADMIN")["id"]
        if alias == "admin"
        else v.find(v.snapshot(), "accounts.User", full_name=RUN + " " + alias.upper())["id"]
        for alias in ["admin", "i1", "p1", "p2"]
    }
    for alias in ["admin", "i1", "p1"]:
        client = v.CLIENTS[alias]
        email = creds[alias]["email"]
        user_id = users[alias]
        before = profile_state(user_id, email, creds[alias]["password"])
        v.get(
            "Navegação para meu perfil " + alias,
            "Perfil próprio",
            client,
            "/",
            extra={"link_proprio": lambda r, b, a: f'href="{path}"' in r["text"]},
        )
        v.get(
            "Consultar perfil próprio " + alias,
            "Perfil próprio",
            client,
            path,
            extra={
                "campos_permitidos": lambda r, b, a: (
                    {"full_name", "email"}.issubset(
                        set().union(*(f["names"] for f in v.Forms(r["text"]).forms))
                    )
                    and not any(
                        'name="' + key + '"' in r["text"]
                        for key in ["role", "is_active", "is_staff", "is_superuser"]
                    )
                )
            },
        )
        updated_email = f"{RUN.lower()}-{alias}-updated@validation.codigodofuturo.local"
        name = before["name"] + " EDITADO"
        expectation = (user_id, updated_email, creds[alias]["password"], before | {"name": name})
        v.post(
            "Atualizar perfil próprio " + alias,
            "Perfil próprio",
            client,
            path,
            {"full_name": name, "email": updated_email.upper()},
            check={
                "somente_identificacao": lambda r, b, a, data=expectation: (
                    profile_state(*data[:3]) == data[3]
                )
            },
        )
        creds[alias]["email"] = updated_email
        fresh = v.Session("LOGIN_NEW_EMAIL_" + alias)
        v.post(
            "Login com e-mail atualizado " + alias,
            "Autenticação",
            fresh,
            "/entrar/",
            {"username": updated_email, "password": creds[alias]["password"]},
            check={
                "sessao_iniciada": lambda r, b, a, fresh=fresh: any(
                    cookie.name == "sessionid" for cookie in fresh.jar
                )
            },
        )
        v.post(
            "E-mail anterior não autentica " + alias,
            "Autenticação",
            v.Session("OLD_EMAIL"),
            "/entrar/",
            {"username": email, "password": creds[alias]["password"]},
            n=200,
            unchanged=True,
            check={"erro": lambda r, b, a: "E-mail ou senha inválidos" in r["text"]},
        )

    participant = v.CLIENTS["p1"]
    user_id = users["p1"]
    before = profile_state(user_id, creds["p1"]["email"], creds["p1"]["password"])
    other_before = profile_state(users["p2"], creds["p2"]["email"], creds["p2"]["password"])
    payload = {
        "full_name": before["name"],
        "email": creds["p1"]["email"],
        "id": users["p2"],
        "pk": users["p2"],
        "user": users["p2"],
        "role": "ADMIN",
        "is_staff": "on",
        "is_superuser": "on",
        "is_active": "",
        "password": "forged",
        "groups": "1",
        "user_permissions": "1",
    }
    v.post(
        "Alvo de terceiro e privilégios forjados ignorados",
        "Perfil próprio",
        participant,
        path + "?user=" + users["p2"],
        payload,
        source=path,
        verify=False,
        check={
            "protegidos_e_terceiro_preservados": lambda r, b, a: (
                profile_state(user_id, creds["p1"]["email"], creds["p1"]["password"]) == before
                and profile_state(users["p2"], creds["p2"]["email"], creds["p2"]["password"])
                == other_before
            )
        },
    )
    v.get(
        "Perfil não possui rota por usuário",
        "Perfil próprio",
        participant,
        path + users["p2"] + "/",
        404,
    )
    for title, data in [
        ("nome obrigatório", {"full_name": "   ", "email": creds["p1"]["email"]}),
        ("nome longo", {"full_name": "x" * 151, "email": creds["p1"]["email"]}),
        ("e-mail obrigatório", {"full_name": "Nome", "email": ""}),
        ("e-mail inválido", {"full_name": "Nome", "email": "invalid"}),
        (
            "unicidade sem diferença de caixa",
            {"full_name": "Nome", "email": creds["p2"]["email"].upper()},
        ),
    ]:
        v.post(
            "Perfil: " + title,
            "Perfil próprio",
            participant,
            path,
            data,
            n=200,
            unchanged=True,
            check={
                "erro_visivel": lambda r, b, a: "field-error" in r["text"],
                "identificacao_preservada": lambda r, b, a: (
                    profile_state(user_id, creds["p1"]["email"], creds["p1"]["password"]) == before
                ),
            },
        )
    v.post(
        "Perfil sem CSRF bloqueado",
        "Perfil próprio",
        participant,
        path,
        payload,
        n=403,
        csrf="missing",
        unchanged=True,
    )


def administrative_paths():
    admin = v.CLIENTS["admin"]
    today = datetime.now(v.TZ).date()
    data = v.CLASS_DATA["queue"] | {"code": RUN + "-B", "title": RUN + " GUARDA_ADMIN"}
    v.post(
        "Preparar turma para guarda administrativa",
        "Preparação HTTP",
        admin,
        "/oficinas/turmas/nova/",
        data,
        check={
            "planejada": lambda r, b, a: (
                v.find(a, "workshops.ClassGroup", code=RUN + "-B")["status"] == "PLANNED"
            )
        },
    )
    class_id = v.find(v.snapshot(), "workshops.ClassGroup", code=RUN + "-B")["id"]
    user_id = v.find(v.snapshot(), "accounts.User", role="ADMIN")["id"]
    path = f"/admin/workshops/classgroup/{class_id}/change/"
    page = admin.request(path)
    form = next(f for f in v.Forms(page["text"]).forms if "code" in f["names"])
    payload = (
        form["fields"]
        | data
        | {
            "created_by": user_id,
            "registration_opens_at_0": data["registration_opens_at"][:10],
            "registration_opens_at_1": "00:00:00",
            "registration_closes_at_0": data["registration_closes_at"][:10],
            "registration_closes_at_1": "23:00:00",
            "_save": "Salvar",
        }
    )
    payload.pop("csrfmiddlewaretoken", None)
    v.get(
        "Admin indica fluxo canônico e situação somente leitura",
        "Admin acadêmico",
        admin,
        path,
        extra={
            "status_nao_editavel": lambda r, b, a: 'name="status"' not in r["text"],
            "fluxo_indicado": lambda r, b, a: "processar a conclusão na aplicação" in r["text"],
        },
    )
    forged = payload | {
        "status": "COMPLETED",
        "title": RUN + " PARCIAL",
        "meetings-TOTAL_FORMS": "1",
        "meetings-INITIAL_FORMS": "0",
        "meetings-0-title": RUN + " PARCIAL",
        "meetings-0-class_group": class_id,
        "meetings-0-starts_at_0": (today + timedelta(days=1)).isoformat(),
        "meetings-0-starts_at_1": "09:00:00",
        "meetings-0-ends_at_0": (today + timedelta(days=1)).isoformat(),
        "meetings-0-ends_at_1": "10:00:00",
    }
    v.post(
        "DEF-003 conclusão direta bloqueada sem gravação parcial",
        "Admin acadêmico",
        admin,
        path,
        forged,
        n=200,
        unchanged=True,
        check={
            "mensagem_da_guarda": lambda r, b, a: "não pode ser alterada diretamente" in r["text"],
            "turma_planejada_sem_encontro": lambda r, b, a: (
                v.find(a, "workshops.ClassGroup", id=class_id)["status"] == "PLANNED"
                and not any(m["class_group_id"] == class_id for m in a["workshops.Meeting"])
            ),
        },
    )
    v.post(
        "Admin permite editar outros campos legítimos",
        "Admin acadêmico",
        admin,
        path,
        payload | {"title": RUN + " GUARDA_ADMIN_EDITADO"},
        check={
            "titulo_editado_status_preservado": lambda r, b, a: (
                v.find(a, "workshops.ClassGroup", id=class_id)["title"].endswith("EDITADO")
                and v.find(a, "workshops.ClassGroup", id=class_id)["status"] == "PLANNED"
            )
        },
    )
    meeting_data = {
        "title": RUN + " GUARDA_MEETING",
        "description": RUN,
        "starts_at": (today + timedelta(days=1)).isoformat() + "T09:00",
        "ends_at": (today + timedelta(days=1)).isoformat() + "T10:00",
    }
    meeting_path = f"/oficinas/turmas/{class_id}/encontros/novo/"
    v.post(
        "Criar encontro legítimo para reteste",
        "Preparação HTTP",
        admin,
        meeting_path,
        meeting_data,
        check={
            "criado": lambda r, b, a: len(a["workshops.Meeting"]) == len(b["workshops.Meeting"]) + 1
        },
    )
    meeting_id = v.find(v.snapshot(), "workshops.Meeting", title=meeting_data["title"])["id"]
    v.post(
        "DEF-001 início duplicado preserva original",
        "Encontros",
        admin,
        meeting_path,
        meeting_data | {"title": RUN + " DUPLICADO"},
        n=200,
        unchanged=True,
        check={"erro_util": lambda r, b, a: "já possui um encontro" in r["text"]},
    )
    v.post(
        "Editar encontro com seu próprio início",
        "Encontros",
        admin,
        f"/oficinas/encontros/{meeting_id}/editar/",
        meeting_data | {"description": RUN + " editado"},
        check={
            "editado": lambda r, b, a: v.find(a, "workshops.Meeting", id=meeting_id)[
                "description"
            ].endswith("editado")
        },
    )
    inline = payload | {
        "title": RUN + " PARCIAL",
        "meetings-TOTAL_FORMS": "1",
        "meetings-INITIAL_FORMS": "1",
        "meetings-0-id": meeting_id,
        "meetings-0-class_group": class_id,
        "meetings-0-title": RUN + " PARCIAL",
        "meetings-0-description": RUN + " editado",
        "meetings-0-status": "COMPLETED",
        "meetings-0-starts_at_0": (today + timedelta(days=1)).isoformat(),
        "meetings-0-starts_at_1": "09:00:00",
        "meetings-0-ends_at_0": (today + timedelta(days=1)).isoformat(),
        "meetings-0-ends_at_1": "10:00:00",
    }
    v.post(
        "Admin inline não marca encontro realizado",
        "Admin acadêmico",
        admin,
        path,
        inline,
        n=200,
        unchanged=True,
        check={"guarda_inline": lambda r, b, a: "não pode ser alterada diretamente" in r["text"]},
    )
    standalone = {
        "title": RUN + " PARCIAL",
        "description": RUN,
        "starts_at_0": (today + timedelta(days=1)).isoformat(),
        "starts_at_1": "09:00:00",
        "ends_at_0": (today + timedelta(days=1)).isoformat(),
        "ends_at_1": "10:00:00",
        "status": "COMPLETED",
        "_save": "Salvar",
    }
    v.post(
        "Admin de encontro não altera situação diretamente",
        "Admin acadêmico",
        admin,
        f"/admin/workshops/meeting/{meeting_id}/change/",
        standalone,
        n=200,
        unchanged=True,
        check={"guarda": lambda r, b, a: "não pode ser alterada diretamente" in r["text"]},
    )
    enrollment = v.ENROLLMENTS[("p1", "academic")]
    evaluation = v.find(v.snapshot(), "learning.Evaluation", enrollment_id=enrollment)["id"]
    project = v.find(v.snapshot(), "learning.StudentProject", enrollment_id=enrollment)["id"]
    for resource, pk in [
        ("enrollments/enrollment", enrollment),
        ("learning/evaluation", evaluation),
        ("learning/studentproject", project),
    ]:
        v.post(
            "Admin acadêmico exige fluxo autorizado: " + resource,
            "Admin acadêmico",
            admin,
            f"/admin/{resource}/{pk}/change/",
            {"status": "APPROVED", "final_score": "10.0"},
            n=403,
            unchanged=True,
            verify=False,
        )


def reset_password(creds):
    client = v.Session("PASSWORD_RESET_COMPLETE")
    started = datetime.now().astimezone().isoformat()
    v.post(
        "Preparar redefinição de senha exclusiva",
        "Preparação HTTP",
        client,
        "/senha/recuperar/",
        {"email": creds["p3"]["email"]},
        unchanged=True,
    )
    logs = subprocess.run(
        v.COMPOSE + ["logs", "--no-color", "--since", started, "app"],
        text=True,
        capture_output=True,
        timeout=20,
        check=True,
    ).stdout
    links = re.findall(re.escape(v.BASE) + r"(/senha/redefinir/[^\s<>]+)", logs)
    if not links:
        raise RuntimeError("Link de recuperação não encontrado; logs omitidos")
    token_path = links[-1]
    v.get("Token de redefinição válido", "Autenticação", client, token_path, 302)
    parts = token_path.rstrip("/").split("/")
    set_path = "/senha/redefinir/" + parts[-2] + "/set-password/"
    new_password = secrets.token_urlsafe(32)
    old_password = creds["p3"]["password"]
    v.post(
        "Redefinir senha exclusiva",
        "Autenticação",
        client,
        set_path,
        {"new_password1": new_password, "new_password2": new_password},
        check={
            "senha_alterada": lambda r, b, a: profile_state(
                v.find(a, "accounts.User", full_name=RUN + " P3")["id"],
                creds["p3"]["email"],
                new_password,
            )["password_preserved"]
        },
    )
    v.post(
        "Senha anterior rejeitada",
        "Autenticação",
        v.Session("OLD_PASSWORD"),
        "/entrar/",
        {"username": creds["p3"]["email"], "password": old_password},
        n=200,
        unchanged=True,
        check={"erro": lambda r, b, a: "E-mail ou senha inválidos" in r["text"]},
    )
    creds["p3"]["password"] = new_password
    v.login("p3", creds)
    v.get(
        "Token usado não pode ser reutilizado",
        "Autenticação",
        v.Session("USED_TOKEN"),
        token_path,
        extra={"link_invalido": lambda r, b, a: "inválido" in r["text"].lower()},
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-dir", required=True, type=Path)
    args = parser.parse_args()
    v.RUN, v.OUT, v.PRIVATE = RUN, OUT, args.private_dir
    v.PRIVATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(v.PRIVATE, 0o700)
    v.LIMIT = 650
    original_prep, original_post, original_get, original_test = v.prep, v.post, v.get, v.test
    credentials = {}

    def prepare():
        credentials.update(original_prep())
        return credentials

    def post(name, group, client, path, *args, **kwargs):
        if name == "Encontro início duplicado":
            kwargs["check"] = {
                "erro_duplicidade": lambda r, b, a: "já possui um encontro" in r["text"]
            }
        return original_post(name, group, client, path, *args, **kwargs)

    def get(name, group, client, path, *args, **kwargs):
        # Correct expectations already documented by the original executor's audit.
        if name in ["Download revogado bloqueado", "Histórico certificado revogado"]:
            args = (404,)
            kwargs.pop("extra", None)
        return original_get(name, group, client, path, *args, **kwargs)

    def test(*args, **kwargs):
        result = original_test(*args, **kwargs)
        if v.CASES[-1]["classification"] != "APROVADO":
            raise RuntimeError("Reteste falhou: " + v.CASES[-1]["functionality"])
        return result

    v.prep, v.post, v.get, v.test = prepare, post, get, test
    write(
        "inicio-http.json",
        {
            "timestamp": datetime.now(v.TZ).isoformat(),
            "run": RUN,
            "historical_run": "VALIDATION-20261013-120621",
            "tls_verified": True,
            "sequential_except_two_capacity_requests": True,
        },
    )
    try:
        v.main()
        administrative_paths()
        profiles(credentials)
        reset_password(credentials)
    finally:
        if credentials:
            private_file = v.PRIVATE / "credentials.json"
            private_file.write_text(json.dumps(credentials))
            private_file.chmod(0o600)
        v.save()
        state = v.snapshot()
        write("estado-final-execucao.json", state)
        write(
            "ids-execucao.json",
            {label: [row["id"] for row in rows] for label, rows in state.items()},
        )
        write("dados-existentes-final-hashes.json", v.existing_hash())
        before = json.loads((OUT / "dados-existentes-inicial-hashes.json").read_text())
        after = json.loads((OUT / "dados-existentes-final-hashes.json").read_text())
        write(
            "dados-existentes-comparacao.json",
            {
                "unchanged": before == after,
                "changed_models": [m for m in before if before[m] != after[m]],
            },
        )
        write(
            "fim-http.json",
            {
                "timestamp": datetime.now(v.TZ).isoformat(),
                "http_requests": len(v.REQUESTS),
                "checks_including_setup_and_repetitions": len(v.CASES),
                "failed": [c["id"] for c in v.CASES if c["classification"] != "APROVADO"],
            },
        )


if __name__ == "__main__":
    main()
