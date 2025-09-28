# 💰 Sistema de Monitoramento de Empréstimos

Um sistema completo de gerenciamento de empréstimos desenvolvido em Streamlit, com autenticação de usuários, dashboard interativo e controle detalhado de empréstimos.

## 🚀 Funcionalidades

### 🔐 Sistema de Autenticação

- **Login seguro** com criptografia de senhas
- **Usuário administrador** com acesso total ao sistema
- **Cadastro de novos usuários** (apenas admins)
- **Controle de permissões** por tipo de usuário

### 📊 Dashboard Principal

- **Cards de métricas** com informações financeiras:
  - Total emprestado
  - Total com juros
  - Total pago
  - Valor a receber
  - Valor líquido
- **Gráficos interativos**:
  - Distribuição por status (pago, pendente, atrasado)
  - Evolução mensal dos empréstimos
- **Análise temporal avançada**:
  - Filtros por período (semanal, quinzenal, mensal)
  - Gráficos de evolução temporal
  - Métricas detalhadas por período
  - Análise por categoria

### 📋 Detalhamento de Empréstimos

- **Tabela completa** com todos os empréstimos
- **Filtros avançados**:
  - Por status (pendente, pago, atrasado)
  - Por período (última semana, quinzena, mês, personalizado)
  - Por nome do cliente
  - Por categoria (geral, motoristas, comerciantes)
- **Status coloridos**:
  - 🟢 Pago (verde)
  - 🟡 Pendente (amarelo)
  - 🔴 Atrasado (vermelho)
- **Resumo estatístico** dos filtros aplicados
- **Ações em lote** para atualização de status

### ➕ Cadastro de Empréstimos

- **Formulário completo** com validações
- **Cálculo automático** de juros e parcelas
- **Campos obrigatórios**:
  - Nome completo do cliente
  - Telefone
  - Valor solicitado
  - Taxa de juros
  - Data do empréstimo
  - Data de pagamento
  - Número de parcelas

## 🛠️ Instalação e Uso

### Pré-requisitos

- Python 3.7+
- pip

### Instalação

1. Clone ou baixe os arquivos do projeto
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

### Execução

```bash
streamlit run app.py
```

O sistema estará disponível em `http://localhost:8501`

## 👤 Credenciais Padrão

**Usuário Administrador:**

- Usuário: `admin`
- Senha: `admin123`

## 📁 Estrutura do Projeto

```
monitoramento/
├── app.py              # Aplicação principal Streamlit
├── database.py         # Sistema de banco de dados
├── requirements.txt    # Dependências Python
├── README.md          # Documentação
├── users.json         # Arquivo de usuários (criado automaticamente)
└── loans.csv          # Arquivo de empréstimos (criado automaticamente)
```

## 🔧 Tecnologias Utilizadas

- **Streamlit** - Framework web para Python
- **Pandas** - Manipulação de dados
- **Plotly** - Gráficos interativos
- **bcrypt** - Criptografia de senhas
- **CSV/JSON** - Armazenamento de dados

## 📊 Recursos do Sistema

### Dashboard

- Visualização em tempo real das métricas financeiras
- Gráficos de pizza para distribuição por status
- Gráficos de barras para evolução temporal

### Gestão de Empréstimos

- Cadastro completo de novos empréstimos
- Cálculo automático de juros e parcelas
- Controle de status (pendente, pago, atrasado)
- Filtros e buscas avançadas

### Segurança

- Senhas criptografadas com bcrypt
- Controle de sessão
- Diferentes níveis de acesso

## 🆕 Novas Funcionalidades Implementadas

### 📅 Análise Temporal de Empréstimos

- **Filtros por período**: Semanal, quinzenal e mensal
- **Seletor de período personalizado**: Data de início e fim customizáveis
- **Gráficos de evolução temporal**: Visualização da evolução dos empréstimos ao longo do tempo
- **Métricas detalhadas por período**: Quantidade, valores e taxas de pagamento
- **Análise por categoria**: Separação por tipo de empréstimo (geral, motoristas, comerciantes)
- **Resumo estatístico**: Métricas consolidadas do período selecionado

### 🔍 Filtros Avançados

- **Períodos pré-definidos**: Última semana, 15 dias, mês, 3 meses
- **Período personalizado**: Seletor livre de datas
- **Combinação de filtros**: Status, período e busca por nome
- **Informações visuais**: Indicadores do período selecionado

### 📊 Importação de Dados

- **Upload de planilhas Excel**: Suporte a arquivos .xlsx e .xls
- **Múltiplas abas**: Processa abas de janeiro a dezembro automaticamente
- **Validação automática**: Verifica estrutura e dados antes da importação
- **Preview dos dados**: Visualização antes de confirmar importação
- **Relatório detalhado**: Estatísticas completas da importação
- **Tratamento de erros**: Processamento continua mesmo com erros parciais

## 🎯 Próximas Funcionalidades

- [x] ✅ Análise temporal com filtros de data
- [x] ✅ Importação de dados de planilhas Excel
- [ ] Relatórios em PDF
- [ ] Notificações de vencimento
- [ ] Histórico de pagamentos
- [ ] Backup automático dos dados
- [ ] Dashboard mobile responsivo

## 📞 Suporte

Para dúvidas ou sugestões, entre em contato através do sistema ou consulte a documentação do Streamlit.

---

**Desenvolvido com ❤️ usando Streamlit**
