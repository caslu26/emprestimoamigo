# 🔧 Solução de Problemas - Importação de Dados

## ❌ **Erro: "Value must be either numerical or a string containing a wildcard"**

### **Causa:**

Este erro ocorre quando o pandas tenta processar dados que não estão no formato esperado. Pode ser causado por:

1. **Valores não numéricos** em campos que deveriam ser números
2. **Formatação inconsistente** dos dados
3. **Células vazias** ou com valores especiais
4. **Caracteres especiais** nos dados
5. **Dependência xlrd faltando** para arquivos .xls

### **Solução Implementada:**

A funcionalidade foi **melhorada** para ser mais robusta:

#### **✅ Correções Específicas:**

- **Instalação automática** da dependência xlrd
- **Múltiplos engines**: Tenta openpyxl e xlrd automaticamente
- **Múltiplas configurações**: Testa diferentes parâmetros de leitura
- **Conversão forçada**: Converte todas as colunas para string primeiro
- **Acesso seguro**: Usa .get() para evitar erros de chave

#### **✅ Melhorias no Processamento:**

- **Leitura como string**: Todos os dados são lidos como string primeiro
- **Limpeza automática**: Remove R$, espaços e caracteres especiais
- **Conversão robusta**: Tenta múltiplos formatos para valores e datas
- **Mapeamento flexível**: Aceita variações nos nomes das colunas
- **Tratamento de erros**: Continua processamento mesmo com erros parciais

#### **✅ Validações Adicionadas:**

- **Verificação de dados vazios**: Ignora linhas com dados inválidos
- **Formato de valores**: Limpa e converte automaticamente
- **Formato de datas**: Tenta múltiplos formatos de data
- **Status padronizado**: Mapeia variações de status

## 🔍 **Outros Problemas Comuns e Soluções**

### **1. Erro: "Colunas faltando"**

**Causa:** Nomes das colunas não coincidem exatamente

**Solução:** O sistema agora aceita estas variações:

| Coluna Original   | Variações Aceitas                                                             |
| ----------------- | ----------------------------------------------------------------------------- |
| Cliente           | cliente, nome, nome do cliente, nome_cliente                                  |
| Valor Emprestado  | valor emprestado, valor_emprestado, valor solicitado, valor_solicitado, valor |
| Valor a Receber   | valor a receber, valor_a_receber, valor total, valor_total, total             |
| Data de Pagamento | data de pagamento, data_pagamento, data pagamento, vencimento, data           |
| Status            | status, situação, situacao, estado                                            |

### **2. Erro: "Valor emprestado inválido"**

**Causa:** Valores em formato incorreto

**Solução:** O sistema agora aceita:

- ✅ `1000.50` (formato correto)
- ✅ `R$ 1.000,50` (com símbolo e formatação)
- ✅ `1000,50` (vírgula como decimal)
- ✅ `1.000,50` (formato brasileiro)

### **3. Erro: "Data inválida"**

**Causa:** Datas em formato incorreto

**Solução:** O sistema aceita:

- ✅ `15/01/2024` (formato brasileiro)
- ✅ `2024-01-15` (formato ISO)
- ✅ `15-01-2024` (formato alternativo)

### **4. Erro: "Status inválido"**

**Causa:** Status em formato incorreto

**Solução:** O sistema mapeia automaticamente:

- ✅ `pago` ou `paga` → pago
- ✅ `pendente` → pendente
- ✅ `atrasado`, `atrasada`, `em atraso` → atrasado

## 🛠️ **Diagnóstico Automático**

O sistema agora inclui **diagnóstico automático** que:

### **✅ Analisa o Arquivo:**

- Lista todas as abas encontradas
- Identifica quais são meses válidos
- Mostra quais abas têm problemas

### **✅ Fornece Feedback Detalhado:**

- Erros específicos por linha
- Sugestões de correção
- Checklist de validação

### **✅ Tenta Múltiplos Engines e Configurações:**

- `openpyxl` com `dtype=str` (para .xlsx)
- `openpyxl` com `dtype=None` (para .xlsx)
- `xlrd` com `dtype=str` (para .xls)
- `xlrd` com `dtype=None` (para .xls)
- **Fallback automático** entre todas as opções
- **Instalação automática** de dependências faltantes

## 📋 **Checklist de Validação**

Antes de fazer upload, verifique:

### **📁 Estrutura do Arquivo:**

- [ ] Arquivo é Excel (.xlsx ou .xls)
- [ ] Não está corrompido
- [ ] Tem abas com nomes dos meses

### **📊 Nomes das Abas:**

- [ ] janeiro, fevereiro, março, abril, maio, junho
- [ ] julho, agosto, setembro, outubro, novembro, dezembro
- [ ] Nomes em português, minúsculas

### **📋 Colunas em Cada Aba:**

- [ ] Cliente (nome do cliente)
- [ ] Valor Emprestado (valor solicitado)
- [ ] Valor a Receber (valor total)
- [ ] Data de Pagamento (data de vencimento)
- [ ] Status (pago/pendente/atrasado)

### **📝 Dados:**

- [ ] Cliente não está vazio
- [ ] Valores são numéricos
- [ ] Datas estão no formato correto
- [ ] Status são válidos

## 🚀 **Como Usar a Nova Versão**

### **1. Upload Normal:**

- Faça upload da planilha
- O sistema processa automaticamente
- Veja estatísticas e erros

### **2. Se Houver Erros:**

- Consulte a seção "Ver erros detalhados"
- Siga as dicas de correção
- Corrija a planilha e tente novamente

### **3. Diagnóstico Automático:**

- Se o processamento falhar completamente
- O sistema mostra análise do arquivo
- Identifica problemas específicos

### **4. Download de Exemplo:**

- Use o botão "📥 Baixar Planilha de Exemplo"
- Baixe um arquivo Excel com estrutura correta
- Use como modelo para sua planilha

## 💡 **Dicas Extras**

### **✅ Para Melhor Compatibilidade:**

1. **Salve no Excel** antes de fazer upload
2. **Use nomes simples** para colunas
3. **Evite fórmulas** complexas
4. **Formate valores** como números
5. **Use datas simples** (DD/MM/AAAA)

### **✅ Para Grandes Volumes:**

1. **Teste com uma aba** primeiro
2. **Verifique os erros** antes de continuar
3. **Faça backup** da planilha original
4. **Importe por partes** se necessário

## 📞 **Suporte Técnico**

Se ainda tiver problemas:

1. **Verifique o diagnóstico** automático
2. **Consulte os erros detalhados**
3. **Siga o checklist** de validação
4. **Teste com dados simples** primeiro

---

**✅ Com essas melhorias, a importação deve funcionar muito melhor!**
