# Segurança e privacidade

## Relato de vulnerabilidades

Não publique credenciais, dados pessoais ou detalhes exploráveis em uma issue pública. Encaminhe o relato diretamente ao responsável pelo repositório, informando versão, passos mínimos e impacto observado.

## Dados permitidos no repositório

- personas e dados totalmente fictícios;
- imagens anonimizadas;
- arquivos `.env.example` sem segredos;
- evidências de teste sem tokens, cookies ou informações pessoais reais.

## Dados proibidos

- senhas e chaves de API;
- arquivos `.env` reais;
- backups ou cópias do banco;
- CPF, telefone, endereço ou e-mail pessoal de participantes;
- cookies, tokens de sessão ou links privados de redefinição de senha.

## Controles mínimos antes da publicação

1. executar `python src/manage.py check --deploy` com as configurações de produção;
2. confirmar HTTPS e cookies seguros;
3. validar permissões por perfil e vínculo;
4. usar dados fictícios no vídeo e nas capturas;
5. testar backup e restauração;
6. revisar logs para impedir exposição de informações sensíveis.
