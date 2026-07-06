# PCP – Sistema de Controle de Pedidos de Produção

Sistema web local para acompanhar pedidos de produção: cadastro de pedidos, status por setor, datas de entrega, previsão de retorno, histórico de alterações e backup automático dos dados.

## Stack técnica

- **Backend:** Python (Flask)
- **Banco de dados:** SQLite
- **Frontend:** HTML/JS (`pcp_prototype.html`, `pcp_prototype_sqlite.html`)
- **Controle de versão:** Git + GitHub
- **Desenvolvimento assistido por IA:** Claude (protótipo inicial), ChatGPT (iterações e melhorias), Claude Code (edição direta do código e automação das rotinas de Git)

## Funcionalidades

- Cadastro e edição de pedidos (cliente, quantidade faltante, datas de entrega, previsão de retorno, status/setor)
- Controle de acesso por papel: leitura (Vendas/Expedição) e edição (PCP)
- Importação e exportação de dados via Excel (`/api/import.xlsx`)
- Backup automático diário do banco de dados e da planilha
- Log de auditoria de todas as alterações

## Como rodar

1. Instalar as dependências:
   ```
   pip install -r requirements_pcp.txt
   ```
2. Rodar o servidor:
   ```
   iniciar_pcp.bat
   ```
   (ou `python servidor_pcp.py` diretamente)
3. Acessar no navegador: `http://localhost:8080`

## Sobre este projeto

Este sistema nasceu de uma necessidade real de controle de pedidos na produção, criado com apoio de ferramentas de IA (Claude e ChatGPT), sem experiência prévia em programação. O versionamento com Git/GitHub e o uso do Claude Code foram incorporados posteriormente para dar mais segurança (backup e histórico de mudanças) e agilidade nas atualizações do sistema.
