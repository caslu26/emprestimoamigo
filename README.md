# 💰 Sistema de Monitoramento de Empréstimos

Um sistema completo de gerenciamento de empréstimos desenvolvido em Streamlit, com autenticação de usuários, dashboard interativo e controle detalhado de empréstimos.

## 🚀 Deploy no Streamlit Cloud

### Pré-requisitos
- Conta no Streamlit Cloud
- Repositório no GitHub com o código

### Como fazer o deploy:

1. **Fazer push do código para o GitHub**
2. **Acessar Streamlit Cloud** (https://share.streamlit.io)
3. **Conectar repositório** GitHub
4. **Configurar o deploy:**
   - **Main file path**: `app.py`
   - **Python version**: 3.9 ou superior

### 📁 Estrutura do Projeto
```
emprestimoamigo/
├── app.py                 # Arquivo principal
├── database.py            # Gerenciamento de dados
├── requirements.txt       # Dependências Python
├── .streamlit/
│   └── config.toml       # Configurações do Streamlit
├── packages.txt          # Dependências do sistema (se necessário)
└── README.md            # Este arquivo
```

## 🔐 Credenciais Padrão

**Usuário Administrador:**
- Usuário: `admin`
- Senha: `admin123`

## ✨ Funcionalidades

### 🔐 Sistema de Autenticação
- Login seguro com criptografia de senhas
- Controle de permissões por tipo de usuário
- Cadastro de novos usuários

### 📊 Dashboard Principal
- Métricas financeiras consolidadas
- Gráficos interativos com Plotly
- Análise temporal avançada

### 📋 Gestão de Empréstimos
- Cadastro de empréstimos por categoria
- Filtros avançados por data, status, cliente
- Atualização de status em lote

### 👥 Gestão de Clientes
- Lista organizada de clientes
- Filtros por tipo, atividade, período
- Estatísticas detalhadas

### 📊 Importação de Dados
- Importação de planilhas Excel
- Validação robusta de dados
- Correção automática de inconsistências

## 🛠️ Tecnologias Utilizadas

- **Streamlit**: Framework web
- **Pandas**: Manipulação de dados
- **Plotly**: Gráficos interativos
- **bcrypt**: Criptografia de senhas
- **openpyxl/xlrd**: Leitura de arquivos Excel

## 📱 Responsividade

O sistema é totalmente responsivo e funciona em:
- 💻 Desktop
- 📱 Tablet
- 📱 Smartphone

## 🔧 Configurações

### Variáveis de Ambiente (se necessário)
```
# Para produção, configure:
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Banco de Dados
O sistema usa arquivos CSV locais para armazenamento:
- `loans.csv`: Empréstimos gerais
- `motoristas.csv`: Empréstimos de motoristas
- `comerciantes.csv`: Empréstimos de comerciantes
- `clients.csv`: Dados dos clientes
- `users.json`: Usuários do sistema

## 🚀 Execução Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run app.py
```

## 📞 Suporte

Para suporte técnico ou dúvidas sobre o sistema, entre em contato através da seção "Suporte" dentro da aplicação.

---

**Desenvolvido com ❤️ para gestão eficiente de empréstimos**