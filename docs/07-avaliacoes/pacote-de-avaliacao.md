# Pacote para as cinco avaliações

Este pacote deve ser usado somente depois que a release candidata estiver publicada. Cada sessão
precisa registrar a versão testada, as tarefas realizadas, os problemas observados e a opinião do
avaliador sem esconder resultados negativos.

## Distribuição recomendada

| Avaliação | Perspectiva | Conta sugerida | Foco |
|---|---|---|---|
| 01 | Participante | `ana.oliveira@demo.codigodofuturo.local` | inscrição, jornada e certificado |
| 02 | Participante | `carla.mendes@demo.codigodofuturo.local` | inscrição, frequência e projeto |
| 03 | Instrutor | `larissa.instrutora@demo.codigodofuturo.local` | turma, chamada, revisão e resultado |
| 04 | Instrutor | `rafael.instrutor@demo.codigodofuturo.local` | isolamento, cronograma e avaliação |
| 05 | Administrador | `admin@demo.codigodofuturo.local` | cadastros, vagas, indicadores e CSV |

A senha da homologação deve ser enviada separadamente e não pode aparecer no Git, nas capturas ou
no PDF final.

## Antes da primeira sessão

- [ ] Registrar URL, SHA/tag e data da release candidata.
- [ ] Executar o smoke test público.
- [ ] Criar um backup da base demonstrativa.
- [ ] Confirmar as cinco pessoas e obter ciência para uso acadêmico das respostas.
- [ ] Testar as cinco contas sugeridas.
- [ ] Abrir os formulários de `resultados/` e substituir todos os campos pendentes.
- [ ] Preparar captura de tela sem cookies, senhas ou dados pessoais reais.

## Condução de cada sessão

1. informar objetivo, duração aproximada de 20 a 30 minutos e perfil simulado;
2. pedir que a pessoa verbalize dúvidas, sem ensinar o caminho inicialmente;
3. anotar sucesso, ajuda necessária, tempo aproximado e erro por tarefa;
4. registrar screenshot somente quando útil e com autorização;
5. aplicar as perguntas obrigatórias da universidade;
6. obter notas de 1 a 5 e comentário final;
7. salvar o resultado no arquivo numerado correspondente.

## Roteiro do participante

1. entrar e localizar uma turma disponível;
2. consultar a oficina e solicitar inscrição quando o cenário permitir;
3. abrir **Minhas inscrições**;
4. abrir **Minha jornada** e interpretar frequência, projeto e resultado;
5. cadastrar ou atualizar um projeto no cenário permitido;
6. localizar um certificado disponível e baixar o PDF;
7. sair da aplicação.

## Roteiro do instrutor

1. entrar e identificar as turmas vinculadas;
2. confirmar que outra turma não vinculada não aparece;
3. abrir cronograma e participantes de uma turma;
4. registrar ou corrigir uma chamada;
5. revisar um projeto;
6. cadastrar ou editar uma avaliação;
7. consultar o painel restrito e sair.

## Roteiro do administrador

1. cadastrar ou editar participante e responsável fictícios;
2. consultar oficinas, criar turma e cadastrar encontro;
3. vincular instrutor;
4. analisar inscrição e verificar capacidade/lista de espera;
5. acompanhar frequência, projeto e avaliação;
6. consultar indicadores com filtro;
7. exportar um CSV e confirmar ausência de CPF, telefone e e-mail;
8. consultar certificados e sair.

## Perguntas mínimas obrigatórias

- Nome de quem testou.
- Data do teste.
- O que foi testado e funcionou.
- O que foi testado e não funcionou, incluindo resultado esperado.
- O que não foi testado e por quê.
- Bugs encontrados.
- Sugestões de melhoria.

## Nomes das evidências

Use nomes previsíveis e sem dados sensíveis:

```text
docs/07-avaliacoes/evidencias/
├── av01-participante-problema-01.png
├── av02-participante-fluxo-ok-01.png
├── av03-instrutor-problema-01.png
├── av04-instrutor-fluxo-ok-01.png
└── av05-admin-problema-01.png
```

## Depois das cinco sessões

1. transferir cada achado para `registro-de-melhorias.md`;
2. classificar tipo e severidade;
3. decidir entre implementar agora, implementar depois, não aceitar ou marcar duplicidade;
4. justificar tudo o que não for implementado;
5. corrigir em branch própria e relacionar PR/commit;
6. executar regressão dos fluxos afetados e toda a suíte;
7. obter confirmação do reteste quando necessária;
8. gerar o PDF consolidado com as cinco opiniões e as decisões.
