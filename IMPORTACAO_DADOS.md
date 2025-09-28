# 📊 Importação de Dados - Sistema de Empréstimos

## 🎯 **Funcionalidade Implementada**

O sistema agora possui uma funcionalidade completa de **importação de dados** a partir de planilhas Excel com múltiplas abas (janeiro a dezembro).

## 📋 **Como Usar**

### **1. Acessar a Funcionalidade**

- Faça login como **administrador**
- No menu lateral, clique em **"📊 Importar Dados"**

### **2. Preparar sua Planilha**

#### **📁 Estrutura da Planilha:**

- **Uma aba para cada mês**: janeiro, fevereiro, março, abril, maio, junho, julho, agosto, setembro, outubro, novembro, dezembro
- **Nomes das abas**: Devem ser exatamente como listado acima (em português, minúsculas)

#### **📊 Colunas Obrigatórias:**

Cada aba deve conter estas colunas (nomes exatos):

| Coluna              | Descrição                     | Formato                |
| ------------------- | ----------------------------- | ---------------------- |
| `Cliente`           | Nome completo do cliente      | Texto                  |
| `Valor Emprestado`  | Valor solicitado pelo cliente | Numérico               |
| `Valor a Receber`   | Valor total com juros         | Numérico               |
| `Data de Pagamento` | Data de vencimento            | DD/MM/AAAA             |
| `Status`            | Status do empréstimo          | pago/pendente/atrasado |

### **3. Upload e Processamento**

1. **Clique em "Escolher arquivo"** e selecione sua planilha Excel (.xlsx ou .xls)
2. **Aguarde o processamento** - o sistema irá:

   - Validar a estrutura das abas
   - Verificar as colunas obrigatórias
   - Processar todos os dados
   - Gerar estatísticas

3. **Visualize o preview** dos dados antes da importação
4. **Confirme a importação** clicando em "✅ Confirmar Importação"

## 📊 **Exemplo de Planilha**

### **Aba "Janeiro":**

| Cliente      | Valor Emprestado | Valor a Receber | Data de Pagamento | Status   |
| ------------ | ---------------- | --------------- | ----------------- | -------- |
| João Silva   | 1000.00          | 1200.00         | 15/01/2024        | pendente |
| Maria Santos | 2500.00          | 3000.00         | 20/01/2024        | pago     |
| Pedro Costa  | 800.00           | 960.00          | 25/01/2024        | atrasado |

### **Aba "Fevereiro":**

| Cliente         | Valor Emprestado | Valor a Receber | Data de Pagamento | Status   |
| --------------- | ---------------- | --------------- | ----------------- | -------- |
| Ana Lima        | 1500.00          | 1800.00         | 10/02/2024        | pendente |
| Carlos Oliveira | 3000.00          | 3600.00         | 15/02/2024        | pago     |

## ✅ **Validações Implementadas**

### **Estrutura:**

- ✅ Verifica se as abas têm os nomes corretos
- ✅ Valida se as colunas obrigatórias existem
- ✅ Processa apenas abas de meses válidos

### **Dados:**

- ✅ Valida se cliente não está vazio
- ✅ Converte valores para formato numérico
- ✅ Processa datas em formato brasileiro
- ✅ Padroniza status (pago/pendente/atrasado)

### **Tratamento de Erros:**

- ✅ Relatório detalhado de erros encontrados
- ✅ Continua processamento mesmo com erros parciais
- ✅ Preview dos dados antes da importação

## 📈 **Estatísticas da Importação**

O sistema mostra:

- **Total de Empréstimos** processados
- **Valor Total** dos empréstimos
- **Meses Processados** com sucesso
- **Erros Encontrados** (se houver)

## 🚀 **Resultado da Importação**

Após confirmar:

- ✅ **Empréstimos importados** para o sistema
- ✅ **Clientes adicionados** automaticamente
- ✅ **Dados disponíveis** em todas as funcionalidades
- ✅ **Relatório de sucesso** com estatísticas

## 💡 **Dicas Importantes**

### **✅ O que funciona:**

- Abas com nomes em português (janeiro, fevereiro, etc.)
- Valores em formato numérico (1000.50)
- Datas em formato brasileiro (15/01/2024)
- Status: pago, pendente, atrasado (minúsculas)

### **⚠️ Cuidados:**

- Nomes das abas devem ser exatos
- Colunas devem ter os nomes corretos
- Valores não podem estar vazios
- Status deve estar em minúsculas

### **🔄 Processo Seguro:**

- **Preview obrigatório** antes da importação
- **Validação completa** dos dados
- **Relatório de erros** detalhado
- **Cancelamento** a qualquer momento

## 🛠️ **Dependências Adicionadas**

Para suporte a Excel, foram adicionadas:

- `openpyxl==3.1.2` - Para arquivos .xlsx
- `xlrd==2.0.1` - Para arquivos .xls

## 📱 **Interface Responsiva**

A página de importação é totalmente responsiva:

- **Desktop**: Layout em colunas
- **Tablet**: Adaptação automática
- **Mobile**: Layout em coluna única

## 🎯 **Benefícios**

1. **Migração Rápida**: Importe centenas de empréstimos em minutos
2. **Validação Automática**: Sistema verifica dados antes da importação
3. **Preview Seguro**: Veja os dados antes de confirmar
4. **Relatório Completo**: Estatísticas detalhadas da importação
5. **Tratamento de Erros**: Processamento continua mesmo com erros parciais

## 🔧 **Suporte Técnico**

Se encontrar problemas:

1. Verifique o formato da planilha
2. Confirme os nomes das abas e colunas
3. Revise os dados de exemplo
4. Consulte os erros detalhados no sistema

---

**✅ Agora você pode migrar todos os seus dados existentes para o sistema de forma rápida e segura!**
