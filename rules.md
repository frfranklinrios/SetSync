# Diretrizes Obrigatórias do Projeto

## 1. Idioma e Comunicação
- **Sempre responda em português do Brasil (pt-BR)** em todas as interações, explicações de código, commits sugeridos e comentários.
- Toda a comunicação no chat ou edits deve ser estritamente em português.

## 2. Stack Tecnológica Fixa
- **Linguagem:** Python.
- **Gerenciador de Pacotes:** Use **sempre o `uv`** (da Astral) para gerenciar o ambiente virtual, dependências e execução de scripts. Não utilize pip padrão ou poetry.
- **Ambiente de Desenvolvimento:** Use **sempre `docker-compose`** (Docker Compose) para orquestrar os serviços do projeto (aplicação, bancos de dados, etc.).
- **Framework Web:** O backend deve ser desenvolvido **sempre utilizando Flask**.

## 3. Documentação Contínua
- O projeto deve **sempre manter um arquivo de documentação detalhado** (ex: `README.md` ou `DOCUMENTATION.md`).
- A cada alteração de escopo, novas rotas, novas dependências ou mudanças no Docker, atualize imediatamente este arquivo de documentação.
- A documentação deve incluir instruções claras de como rodar o projeto usando `uv` e `docker compose`.

## 4. Controle de Versão e Sincronização
- **Sincronização com GitHub:** Todo o código, configurações e documentação devem ser **sempre sincronizados com o repositório no GitHub**.
- **Commits:** Realize commits frequentes, organizados e com mensagens claras e descritivas (sempre em português) a cada nova funcionalidade, correção ou atualização de estrutura/documentação.
- **Push Constante:** Certifique-se de realizar o push das alterações regularmente para garantir que o repositório remoto esteja sempre atualizado com a versão mais recente da máquina local.

