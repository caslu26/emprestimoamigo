# 📊 Exemplo de Planilha para Importação

## 📋 **Estrutura da Planilha**

Para importar dados no sistema, sua planilha deve seguir esta estrutura exata:

### **📁 Nomes das Abas:**

- janeiro
- fevereiro
- março
- abril
- maio
- junho
- julho
- agosto
- setembro
- outubro
- novembro
- dezembro

### **📊 Colunas Obrigatórias (em cada aba):**

1. **Cliente** - Nome completo do cliente
2. **Valor Emprestado** - Valor solicitado (formato numérico)
3. **Valor a Receber** - Valor total com juros (formato numérico)
4. **Data de Pagamento** - Data de vencimento (DD/MM/AAAA)
5. **Status** - pago, pendente ou atrasado (minúsculas)

## 📝 **Exemplo Completo**

### **Aba "janeiro":**

```
| Cliente          | Valor Emprestado | Valor a Receber | Data de Pagamento | Status   |
|------------------|------------------|-----------------|-------------------|----------|
| João Silva       | 1000.00         | 1200.00        | 15/01/2024       | pendente |
| Maria Santos     | 2500.00         | 3000.00        | 20/01/2024       | pago     |
| Pedro Costa      | 800.00          | 960.00         | 25/01/2024       | atrasado |
| Ana Lima         | 1500.00         | 1800.00        | 30/01/2024       | pendente |
```

### **Aba "fevereiro":**

```
| Cliente          | Valor Emprestado | Valor a Receber | Data de Pagamento | Status   |
|------------------|------------------|-----------------|-------------------|----------|
| Carlos Oliveira  | 2000.00         | 2400.00        | 10/02/2024       | pendente |
| Lucia Ferreira   | 3200.00         | 3840.00        | 15/02/2024       | pago     |
| Roberto Alves    | 900.00          | 1080.00        | 20/02/2024       | pendente |
| Fernanda Souza   | 1800.00         | 2160.00        | 25/02/2024       | atrasado |
```

### **Aba "março":**

```
| Cliente          | Valor Emprestado | Valor a Receber | Data de Pagamento | Status   |
|------------------|------------------|-----------------|-------------------|----------|
| Marcos Pereira   | 1100.00         | 1320.00        | 05/03/2024       | pendente |
| Juliana Costa    | 2800.00         | 3360.00        | 12/03/2024       | pago     |
| Rafael Santos    | 750.00          | 900.00         | 18/03/2024       | pendente |
| Beatriz Lima     | 2200.00         | 2640.00        | 25/03/2024       | pago     |
```

## ⚠️ **Regras Importantes**

### **✅ Formato Correto:**

- **Valores**: Use ponto como separador decimal (1000.50)
- **Datas**: Formato brasileiro DD/MM/AAAA (15/01/2024)
- **Status**: Apenas minúsculas (pago, pendente, atrasado)
- **Nomes**: Texto simples, sem caracteres especiais

### **❌ Evitar:**

- Valores com vírgula (1.000,50)
- Datas em formato americano (01/15/2024)
- Status em maiúsculas (PAGO, PENDENTE)
- Colunas com nomes diferentes
- Abas com nomes diferentes

## 🔧 **Como Criar a Planilha**

### **1. No Excel:**

1. Crie um novo arquivo
2. Renomeie as abas para os meses (janeiro, fevereiro, etc.)
3. Em cada aba, crie as 5 colunas obrigatórias
4. Preencha os dados seguindo o formato correto

### **2. No Google Sheets:**

1. Crie um novo documento
2. Renomeie as abas para os meses
3. Crie as colunas em cada aba
4. Preencha os dados
5. Exporte como Excel (.xlsx)

### **3. Validação:**

Antes de fazer upload, verifique:

- ✅ Nomes das abas estão corretos
- ✅ Colunas têm os nomes exatos
- ✅ Valores estão em formato numérico
- ✅ Datas estão no formato brasileiro
- ✅ Status estão em minúsculas

## 📊 **Resultado da Importação**

Após importar esta planilha exemplo, você terá:

- **12 empréstimos** importados
- **12 clientes** cadastrados
- **Dados distribuídos** por mês
- **Status variados** (pago, pendente, atrasado)

## 🎯 **Dicas Extras**

1. **Organize por mês**: Mantenha os dados organizados por mês nas abas
2. **Valide os dados**: Verifique se os valores estão corretos antes da importação
3. **Backup**: Sempre mantenha uma cópia da planilha original
4. **Teste**: Comece com uma planilha pequena para testar o processo

---

**✅ Com esta estrutura, você pode importar todos os seus dados existentes para o sistema!**
