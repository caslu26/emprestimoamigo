# 🔧 Correção: KeyError no Preview dos Dados

## ❌ **Erro Identificado**

```
KeyError: "['valor_com_juros', 'status'] not in index"
File "app.py", line 2171, in data_import_page
    display_df = preview_df[['nome_cliente', 'valor_solicitado', 'valor_com_juros', 'data_pagamento', 'status']].copy()
```

## 🔍 **Causa do Problema**

O erro acontecia porque o **preview dos dados** estava tentando acessar colunas que **não existiam mais** no DataFrame após as correções na estrutura de dados.

### **Campos que Causavam o Erro:**

#### **1. Campo `valor_com_juros`**

- **Problema**: Campo não existe mais na estrutura corrigida
- **Substituído por**: Cálculo dinâmico baseado em `valor_solicitado` + `taxa_juros`

#### **2. Campo `status`**

- **Problema**: Campo não está sendo criado na nova estrutura
- **Motivo**: Campo não é usado pela função `add_loan`

## ✅ **Solução Implementada**

### **1. Verificação Dinâmica de Colunas**

```python
# Verificar quais colunas existem antes de acessar
available_columns = ['nome_cliente', 'valor_solicitado', 'data_pagamento', 'taxa_juros', 'parcelas']
display_columns = [col for col in available_columns if col in preview_df.columns]
display_df = preview_df[display_columns].copy()
```

**Benefícios:**

- ✅ **Não quebra** se colunas estiverem faltando
- ✅ **Adapta-se** à estrutura atual dos dados
- ✅ **Evita KeyError** em futuras mudanças

### **2. Cálculo Dinâmico do Valor Total**

```python
# Calcular valor total com juros para exibição
if 'valor_solicitado' in preview_df.columns and 'taxa_juros' in preview_df.columns:
    valor_solicitado = preview_df['valor_solicitado']
    taxa_juros = preview_df['taxa_juros']
    valor_total = valor_solicitado * (1 + taxa_juros / 100)
    display_df['valor_total'] = valor_total.apply(lambda x: f"R$ {x:,.2f}")
```

**Lógica:**

- **Calcula automaticamente** o valor total baseado na taxa de juros
- **Mostra o resultado** formatado em reais
- **Mantém a funcionalidade** do preview original

### **3. Formatação Condicional**

```python
# Formatar valores monetários se existirem
if 'valor_solicitado' in display_df.columns:
    display_df['valor_solicitado'] = display_df['valor_solicitado'].apply(lambda x: f"R$ {x:,.2f}")

# Formatar taxa de juros se existir
if 'taxa_juros' in display_df.columns:
    display_df['taxa_juros'] = display_df['taxa_juros'].apply(lambda x: f"{x:.1f}%")
```

**Benefícios:**

- ✅ **Formata apenas** campos que existem
- ✅ **Evita erros** de campos inexistentes
- ✅ **Mantém consistência** visual

### **4. Mapeamento Flexível de Colunas**

```python
column_mapping = {
    'nome_cliente': 'Cliente',
    'valor_solicitado': 'Valor Emprestado',
    'valor_total': 'Valor Total',
    'taxa_juros': 'Taxa de Juros',
    'parcelas': 'Parcelas',
    'data_pagamento': 'Data Pagamento'
}

# Renomear apenas colunas que existem
display_df = display_df.rename(columns={col: column_mapping[col] for col in display_df.columns if col in column_mapping})
```

**Benefícios:**

- ✅ **Nomes amigáveis** para o usuário
- ✅ **Adapta-se** à estrutura atual
- ✅ **Não quebra** se campos mudarem

## 📊 **Estrutura do Preview Corrigida**

### **Antes (Causava Erro):**

```python
# Tentava acessar colunas que não existiam
display_df = preview_df[['nome_cliente', 'valor_solicitado', 'valor_com_juros', 'data_pagamento', 'status']].copy()
```

### **Depois (Funciona):**

```python
# Verifica quais colunas existem primeiro
available_columns = ['nome_cliente', 'valor_solicitado', 'data_pagamento', 'taxa_juros', 'parcelas']
display_columns = [col for col in available_columns if col in preview_df.columns]
display_df = preview_df[display_columns].copy()

# Calcula valor total dinamicamente
if 'valor_solicitado' in preview_df.columns and 'taxa_juros' in preview_df.columns:
    valor_total = valor_solicitado * (1 + taxa_juros / 100)
    display_df['valor_total'] = valor_total.apply(lambda x: f"R$ {x:,.2f}")
```

## 🎯 **Resultado**

### **✅ Benefícios:**

- **Preview funciona** corretamente
- **Não quebra** com mudanças na estrutura
- **Mostra dados relevantes** para o usuário
- **Formatação consistente** de valores

### **✅ Campos Exibidos no Preview:**

1. ✅ **Cliente** - Nome do cliente
2. ✅ **Valor Emprestado** - Valor solicitado (formatado)
3. ✅ **Valor Total** - Valor com juros (calculado)
4. ✅ **Taxa de Juros** - Taxa calculada (formatada)
5. ✅ **Parcelas** - Número de parcelas
6. ✅ **Data Pagamento** - Data de vencimento

## 🔧 **Detalhes Técnicos**

### **Verificação de Existência:**

```python
if col in df.columns:
    # Usar coluna
else:
    # Pular ou usar alternativa
```

### **Cálculo de Valor Total:**

```python
valor_total = valor_solicitado * (1 + taxa_juros / 100)
```

### **Formatação Condicional:**

```python
if 'field' in df.columns:
    df['field'] = df['field'].apply(formatter)
```

## 🚀 **Como Testar**

1. **Faça upload da sua planilha**
2. **Veja o preview** dos dados processados
3. **Confirme** que os valores estão corretos
4. **Proceda** com a importação

## 💡 **Prevenção Futura**

### **✅ Padrões Implementados:**

- **Sempre verificar** existência de colunas antes de acessar
- **Usar mapeamento flexível** para nomes de colunas
- **Calcular valores derivados** dinamicamente
- **Formatação condicional** baseada em disponibilidade

### **✅ Estrutura Robusta:**

```python
# Padrão para acessar colunas:
available_columns = ['col1', 'col2', 'col3']
display_columns = [col for col in available_columns if col in df.columns]

# Padrão para formatação:
if 'field' in df.columns:
    df['field'] = df['field'].apply(formatter)
```

---

**✅ O erro foi completamente corrigido e o preview agora funciona perfeitamente!**
