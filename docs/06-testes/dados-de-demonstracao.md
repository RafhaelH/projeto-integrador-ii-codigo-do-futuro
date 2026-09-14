# Dados de demonstração

## Objetivo

A carga determinística prepara uma base exclusivamente fictícia para apresentação, testes
manuais e avaliação com usuários. Ela não apaga registros e pode ser executada novamente:
os mesmos registros reservados são atualizados sem duplicação.

## Execução local

Após aplicar as migrações:

```bash
uv run python src/manage.py seed_demo
```

Todos os e-mails usam o domínio reservado `demo.codigodofuturo.local`, os nomes visíveis
começam com `[DEMO]` e os códigos das turmas começam com `DEMO-`.

## Credenciais

| Perfil | E-mail | Senha local |
|---|---|---|
| Administrador | `admin@demo.codigodofuturo.local` | `Demo@Codigo2026` |
| Instrutora | `larissa.instrutora@demo.codigodofuturo.local` | `Demo@Codigo2026` |
| Instrutor | `rafael.instrutor@demo.codigodofuturo.local` | `Demo@Codigo2026` |
| Participante | `ana.oliveira@demo.codigodofuturo.local` | `Demo@Codigo2026` |

Os outros participantes usam o mesmo domínio e a mesma senha local. Nunca reutilize essa
senha fora de um ambiente descartável de desenvolvimento ou homologação.

## Conteúdo criado

| Entidade | Quantidade |
|---|---:|
| Usuários | 9 |
| Participantes | 6 |
| Instrutores | 2 |
| Responsáveis e vínculos | 3 |
| Instituições | 1 |
| Oficinas | 3 |
| Turmas | 4 |
| Encontros | 10 |
| Inscrições | 9 |
| Registros de frequência | 12 |
| Projetos | 4 |
| Avaliações | 3 |
| Certificados | 1 |

## Cenários disponíveis

- turma de Python concluída, com uma aprovação certificada e uma não conclusão por frequência;
- turma de desenvolvimento web em andamento, com presença, falta, projeto entregue e rascunho;
- turma de robótica aberta e lotada, com duas confirmações, espera e solicitação pendente;
- próxima turma planejada, ainda sem inscrições;
- participantes adultos e menores com responsáveis ativos;
- inscrições pendente, confirmada, em espera, cancelada, aprovada e não concluída.

## Segurança

Com `DEBUG=False`, o comando é bloqueado por padrão. Em uma homologação isolada, a liberação
exige simultaneamente uma senha definida no ambiente e a opção explícita:

```bash
DEMO_PASSWORD='troque-esta-senha' uv run python src/manage.py seed_demo --allow-production
```

Não execute a carga no banco que contenha dados pessoais reais. O comando não faz limpeza
global e não altera superusuários existentes; ele atua somente nas identidades reservadas.
