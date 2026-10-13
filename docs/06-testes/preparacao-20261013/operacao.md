# Operação da preparação reproduzível

O comando gerencia os IDs comprovados desta implantação e UUIDs novos derivados de um namespace estável. Ele reutiliza oficinas/pessoas/inscrições originais; não cria uma segunda carga completa. O manifest não é uma autorização para outra base. Em banco vazio ou com relações divergentes, a preparação recusa executar. Restaurar a base e os arquivos restritos permite repetir a mesma preparação.

Na VPS, o executor local restrito lê somente `deploy/production.env`, confirma o container PostgreSQL deste projeto, resolve seu IP interno e passa configuração pelo ambiente do processo. Não grava mudanças no arquivo de ambiente nem imprime segredos. A assinatura `accounts.User`, o nome confirmado e `POSTGRES_DB` precisam corresponder. Os testes usaram outro PostgreSQL, sem porta publicada, com dados em tmpfs; ele já foi removido.

Simulação no ambiente publicado:

```bash
cd /home/ubuntu/projetos/projeto-integrador-ii-codigo-do-futuro
.venv/bin/python /root/codigo-do-futuro-presentation/20261013/run_project.py prepare_presentation \
  --manifest /root/codigo-do-futuro-presentation/20261013/demo-manifest.json \
  --confirm-database codigo_futuro \
  --credentials-file /root/codigo-do-futuro-presentation/20261013/credentials.json \
  --state-file /root/codigo-do-futuro-presentation/20261013/state.json \
  --reference-date 2026-10-13 --dry-run
```

Para aplicar em uma restauração ainda não preparada, retire somente `--dry-run`, depois de backup, conferência do manifest e revisão da simulação. Na base já preparada, o estado existente faz o comando retornar sem redefinir senhas, datas, notas ou tarefas realizadas. Não apagar `state.json` ou `credentials.json` para forçar novo seed. O estado guarda os IDs criados e a data; as credenciais guardam senhas aleatórias geradas uma única vez. Diretório 700, arquivos 600, fora do Git. Os mesmos argumentos funcionam em `python src/manage.py prepare_presentation` dentro do runtime Django deste projeto, quando os arquivos restritos estiverem disponíveis fora de `/app`.

O dry-run inicial apresenta IDs gerenciados, campos/nomes a organizar, contatos, códigos, períodos e espaços novos. Ele não chama os serviços nem grava arquivos de credenciais. A aplicação inicial é transacional, valida relações e recusa dependências externas ou colisões de IDs/e-mails. A carga histórica usa um relógio de fixture apenas no processo do comando para registrar inscrições e eventos acadêmicos fictícios em ordem; o relógio da VPS e da aplicação publicada não é alterado. As datas de importação dos registros antigos são preservadas. Nenhuma turma foi marcada diretamente como concluída nesta preparação: o estado histórico foi mantido e a nova conclusão A05-F passou pelo serviço acadêmico.

`archive_validation` recebe manifests explícitos, nunca seleciona por nome. A simulação é padrão, a aplicação exige `--apply`, nome exato do banco e arquivo de exportação novo em diretório restrito. A revisão considera todas as FKs, preserva alvos com fontes externas e confere o Collector antes de cada exclusão na transação. Exportação inclui IDs/relações e sessões identificadas pelo usuário técnico; hashes de senha e chaves de sessão ficam somente no arquivo restrito. Arquivos SHA-256 permitem conferir a exportação. A exclusão dos certificados fictícios comprovados é uma operação de manutenção explicitamente autorizada neste pedido, não uma operação da interface: a política cotidiana de revogação continua intacta.

Não repetir a limpeza antiga para outros registros, não executar flush e não remover volumes. Preservar os 85 arquivos históricos de evidência. `seed_demo` antigo está bloqueado quando reconhece a apresentação, para não recriar nomes/e-mails antigos. Os espaços dos administradores são separados por roteiro; a permissão administrativa funcional global continua sendo parte do produto. A03/A04 têm isolamento de turma no servidor, A05 tem dados próprios.

Datas e limitações: referência 13/10/2026. A oferta A05-I fecha em 16/10/2026 às 18h; Robótica fecha em 03/11/2026 às 18h. Se as sessões forem posteriores, revisar a tarefa e preparar nova oferta exclusiva após backup, sem reset dos dados existentes. E-mail é de console, sem entrega SMTP; não abrir logs de recuperação durante gravações. A gravação do vídeo e as cinco opiniões humanas continuam pendentes.
