import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from database import Database
import numpy as np
try:
    from email_config import EmailService
except ImportError:
    # Se email_config não existir, criar uma classe mock
    class EmailService:
        def send_reset_email(self, to_email, username, message):
            print(f"Email simulado para {to_email}: {message}")
            return True

# Configuração da página
st.set_page_config(
    page_title="Empréstimos Amigo",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para melhor responsividade
st.markdown("""
<style>
    /* Responsividade geral */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    
    /* Sidebar responsiva */
    .css-1d391kg {
        padding-top: 1rem;
    }
    
    /* Colunas responsivas */
    @media (max-width: 768px) {
        .stColumns > div {
            flex-direction: column;
            margin-bottom: 1rem;
        }
        
        .stColumns > div > div {
            width: 100% !important;
        }
    }
    
    /* Métricas responsivas */
    @media (max-width: 768px) {
        .metric-container {
            margin-bottom: 1rem;
        }
    }
    
    /* Tabelas responsivas */
    .stDataFrame {
        overflow-x: auto;
    }
    
    /* Cards responsivos */
    @media (max-width: 768px) {
        .client-card {
            margin-bottom: 1rem;
        }
    }
    
    /* Botões responsivos */
    @media (max-width: 768px) {
        .stButton > button {
            width: 100%;
            margin-bottom: 0.5rem;
        }
    }
    
    /* Formulários responsivos */
    @media (max-width: 768px) {
        .stForm > div {
            padding: 1rem;
        }
    }
    
    /* Gráficos responsivos */
    .js-plotly-plot {
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar banco de dados
db = Database()
email_service = EmailService()

# Limpar tokens expirados na inicialização
db.cleanup_expired_tokens()

# Funções auxiliares para análise temporal
def get_period_filter(df, period_type, start_date=None, end_date=None):
    """
    Filtra DataFrame por período específico
    
    Args:
        df: DataFrame com coluna 'data_emprestimo'
        period_type: 'semanal', 'quinzenal', 'mensal'
        start_date: Data de início (opcional)
        end_date: Data de fim (opcional)
    """
    if df.empty:
        return df
    
    df_copy = df.copy()
    df_copy['data_emprestimo'] = pd.to_datetime(df_copy['data_emprestimo'])
    
    if period_type == 'semanal':
        df_copy['periodo'] = df_copy['data_emprestimo'].dt.to_period('W')
    elif period_type == 'quinzenal':
        # Criar períodos quinzenais (primeira e segunda quinzena do mês)
        df_copy['mes'] = df_copy['data_emprestimo'].dt.to_period('M')
        df_copy['dia'] = df_copy['data_emprestimo'].dt.day
        df_copy['quinzena'] = (df_copy['dia'] <= 15).astype(int) + 1
        df_copy['periodo'] = df_copy['mes'].astype(str) + '-Q' + df_copy['quinzena'].astype(str)
    elif period_type == 'mensal':
        df_copy['periodo'] = df_copy['data_emprestimo'].dt.to_period('M')
    
    # Aplicar filtros de data se fornecidos
    if start_date:
        df_copy = df_copy[df_copy['data_emprestimo'].dt.date >= start_date]
    if end_date:
        df_copy = df_copy[df_copy['data_emprestimo'].dt.date <= end_date]
    
    return df_copy

def calculate_period_metrics(df, period_type):
    """
    Calcula métricas por período
    
    Args:
        df: DataFrame filtrado por período
        period_type: 'semanal', 'quinzenal', 'mensal'
    """
    if df.empty:
        return pd.DataFrame()
    
    metrics = df.groupby('periodo').agg({
        'id': 'count',
        'valor_solicitado': 'sum',
        'valor_total': 'sum',
        'valor_pago': 'sum',
        'status': lambda x: (x == 'pago').sum()
    }).reset_index()
    
    metrics.columns = ['periodo', 'total_emprestimos', 'valor_emprestado', 'valor_total', 'valor_pago', 'emprestimos_pagos']
    metrics['valor_pendente'] = metrics['valor_total'] - metrics['valor_pago']
    metrics['taxa_pagamento'] = (metrics['emprestimos_pagos'] / metrics['total_emprestimos'] * 100).round(2)
    
    return metrics

def get_date_range_selector():
    """
    Cria seletor de período para filtros de data
    """
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Data Início",
            value=date.today() - timedelta(days=90),
            help="Selecione a data de início do período"
        )
    
    with col2:
        end_date = st.date_input(
            "Data Fim", 
            value=date.today(),
            help="Selecione a data de fim do período"
        )
    
    return start_date, end_date

def create_responsive_columns(num_cols, gap="small"):
    """
    Cria colunas responsivas que se adaptam ao tamanho da tela
    
    Args:
        num_cols: Número de colunas
        gap: Espaçamento entre colunas ("small", "medium", "large")
    """
    # Em telas pequenas, sempre usar 1 coluna
    if num_cols > 2:
        # Para desktop, usar o número especificado
        return st.columns(num_cols, gap=gap)
    else:
        return st.columns(num_cols, gap=gap)

def create_responsive_metrics(metrics_data, num_cols=4):
    """
    Cria métricas responsivas que se adaptam ao tamanho da tela
    
    Args:
        metrics_data: Lista de dicionários com {'label': str, 'value': str, 'delta': str}
        num_cols: Número de colunas (padrão 4)
    """
    # Em mobile, usar 2 colunas; em desktop, usar o número especificado
    cols = create_responsive_columns(min(num_cols, len(metrics_data)))
    
    for i, metric in enumerate(metrics_data):
        with cols[i % len(cols)]:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric(
                label=metric['label'],
                value=metric['value'],
                delta=metric.get('delta')
            )
            st.markdown('</div>', unsafe_allow_html=True)

# Funções para importação de dados
def process_excel_data(uploaded_file):
    """
    Processa arquivo Excel com múltiplas abas (janeiro a dezembro)
    
    Args:
        uploaded_file: Arquivo Excel carregado pelo Streamlit
    
    Returns:
        dict: Dados processados e estatísticas da importação
    """
    try:
        # Mapear nomes dos meses
        month_map = {
            # Nomes padrão (minúsculas)
            'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
            'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
            'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12,
            # Nomes com números (como "Janeiro 01")
            'janeiro 01': 1, 'janeiro 1': 1, 'janeiro_01': 1, 'janeiro_1': 1,
            'fevereiro 02': 2, 'fevereiro 2': 2, 'fevereiro_02': 2, 'fevereiro_2': 2,
            'março 03': 3, 'março 3': 3, 'março_03': 3, 'março_3': 3,
            'abril 04': 4, 'abril 4': 4, 'abril_04': 4, 'abril_4': 4,
            'maio 05': 5, 'maio 5': 5, 'maio_05': 5, 'maio_5': 5,
            'junho 06': 6, 'junho 6': 6, 'junho_06': 6, 'junho_6': 6,
            'julho 07': 7, 'julho 7': 7, 'julho_07': 7, 'julho_7': 7,
            'agosto 08': 8, 'agosto 8': 8, 'agosto_08': 8, 'agosto_8': 8,
            'setembro 09': 9, 'setembro 9': 9, 'setembro_09': 9, 'setembro_9': 9,
            'outubro 10': 10, 'outubro_10': 10,
            'novembro 11': 11, 'novembro_11': 11,
            'dezembro 12': 12, 'dezembro_12': 12,
            # Nomes em maiúsculas
            'JANEIRO': 1, 'FEVEREIRO': 2, 'MARÇO': 3, 'ABRIL': 4,
            'MAIO': 5, 'JUNHO': 6, 'JULHO': 7, 'AGOSTO': 8,
            'SETEMBRO': 9, 'OUTUBRO': 10, 'NOVEMBRO': 11, 'DEZEMBRO': 12,
            'JANEIRO 01': 1, 'FEVEREIRO 02': 2, 'MARÇO 03': 3, 'ABRIL 04': 4,
            'MAIO 05': 5, 'JUNHO 06': 6, 'JULHO 07': 7, 'AGOSTO 08': 8,
            'SETEMBRO 09': 9, 'OUTUBRO 10': 10, 'NOVEMBRO 11': 11, 'DEZEMBRO 12': 12
        }
        
        # Ler todas as abas do Excel com configurações mais robustas
        excel_data = None
        
        # Tentar diferentes engines e configurações
        engines_to_try = [
            ('openpyxl', {'dtype': str, 'na_values': ['', 'N/A', 'n/a', 'NULL', 'null']}),
            ('openpyxl', {'dtype': None, 'na_values': ['', 'N/A', 'n/a', 'NULL', 'null']}),
            ('openpyxl', {'dtype': str}),
            ('openpyxl', {'dtype': None})
        ]
        
        # Tentar xlrd apenas se disponível
        try:
            import xlrd
            engines_to_try.extend([
                ('xlrd', {'dtype': str, 'na_values': ['', 'N/A', 'n/a', 'NULL', 'null']}),
                ('xlrd', {'dtype': None, 'na_values': ['', 'N/A', 'n/a', 'NULL', 'null']})
            ])
        except ImportError:
            pass  # xlrd não disponível, usar apenas openpyxl
        
        for engine, config in engines_to_try:
            try:
                uploaded_file.seek(0)  # Resetar posição do arquivo
                excel_data = pd.read_excel(
                    uploaded_file, 
                    sheet_name=None, 
                    engine=engine,
                    header=0,
                    **config
                )
                break  # Se funcionou, sair do loop
            except Exception as e:
                continue  # Tentar próxima configuração
        
        # Se nenhuma configuração funcionou
        if excel_data is None:
            return {
                'success': False,
                'error': "Não foi possível ler o arquivo Excel. Verifique se o arquivo não está corrompido e se tem o formato correto.",
                'data': [],
                'stats': {'total_loans': 0, 'total_value': 0, 'months_processed': 0, 'errors': []}
            }
        
        processed_data = []
        import_stats = {
            'total_loans': 0,
            'total_value': 0,
            'months_processed': 0,
            'errors': [],
            'loans_per_month': {}  # Contador por mês
        }
        
        # Processar cada aba (mês)
        # Debug: mostrar todas as abas encontradas
        import_stats['errors'].append(f"DEBUG - Abas encontradas no arquivo: {list(excel_data.keys())}")
        
        for sheet_name, df in excel_data.items():
            sheet_name_lower = sheet_name.lower().strip()
            import_stats['errors'].append(f"DEBUG - Processando aba: '{sheet_name}' (normalizada: '{sheet_name_lower}')")
            
            # Verificar se é um mês válido
            if sheet_name_lower in month_map:
                month_num = month_map[sheet_name_lower]
                
                # Limpar dados vazios e resetar índice
                df = df.dropna(how='all').reset_index(drop=True)
                
                if df.empty:
                    import_stats['errors'].append(f"Aba '{sheet_name}': Planilha vazia")
                    continue
                
                # Log para debug - mostrar primeiras linhas da planilha
                import_stats['errors'].append(f"DEBUG - Aba '{sheet_name}': {len(df)} linhas encontradas")
                if len(df) > 0:
                    import_stats['errors'].append(f"DEBUG - Primeira linha: {dict(df.iloc[0])}")
                    import_stats['errors'].append(f"DEBUG - Colunas: {list(df.columns)}")
                
                # Padronizar nomes das colunas - mais flexível
                df.columns = df.columns.str.lower().str.strip()
                
                # Mapear possíveis variações de nomes de colunas
                column_mapping = {
                    'cliente': ['cliente', 'nome', 'nome do cliente', 'nome_cliente'],
                    'valor emprestado': ['valor emprestado', 'valor_emprestado', 'valor solicitado', 'valor_solicitado', 'valor'],
                    'valor a receber': ['valor a receber', 'valor_a_receber', 'valor total', 'valor_total', 'total'],
                    'data de pagamento': ['data de pagamento', 'data_pagamento', 'data pagamento', 'vencimento', 'data'],
                    'status': ['status', 'situação', 'situacao', 'estado']
                }
                
                # Mapear colunas existentes para nomes padrão
                actual_columns = {}
                for standard_name, possible_names in column_mapping.items():
                    for possible_name in possible_names:
                        if possible_name in df.columns:
                            actual_columns[standard_name] = possible_name
                            break
                
                # Verificar se as colunas necessárias existem
                missing_columns = [col for col in column_mapping.keys() if col not in actual_columns]
                
                if missing_columns:
                    import_stats['errors'].append(f"Aba '{sheet_name}': Colunas faltando: {', '.join(missing_columns)}")
                    import_stats['errors'].append(f"Colunas encontradas: {list(df.columns)}")
                    import_stats['errors'].append(f"Colunas mapeadas: {actual_columns}")
                    continue
                
                # Log das colunas que foram encontradas
                import_stats['errors'].append(f"DEBUG - Aba '{sheet_name}': Colunas mapeadas com sucesso: {actual_columns}")
                
                # Converter todas as colunas para string para evitar problemas de tipo
                for col in df.columns:
                    df[col] = df[col].astype(str)
                
                # Processar cada linha da aba
                linhas_processadas = 0
                linhas_puladas = 0
                
                for idx, row in df.iterrows():
                    try:
                        # Validar dados básicos - mais robusto
                        cliente_raw = row.get(actual_columns['cliente'], '')
                        cliente = str(cliente_raw).strip() if cliente_raw and str(cliente_raw).lower() not in ['nan', 'none', ''] else ""
                        
                        valor_emprestado_raw = row.get(actual_columns['valor emprestado'], '')
                        valor_emprestado_str = str(valor_emprestado_raw).strip() if valor_emprestado_raw and str(valor_emprestado_raw).lower() not in ['nan', 'none', ''] else ""
                        
                        if not cliente or not valor_emprestado_str:
                            linhas_puladas += 1
                            if linhas_puladas <= 3:  # Mostrar apenas as primeiras 3 linhas puladas
                                import_stats['errors'].append(f"DEBUG - Linha {idx+2} pulada: cliente='{cliente}', valor='{valor_emprestado_str}'")
                            continue
                        
                        linhas_processadas += 1
                        
                        # Converter valores numéricos de forma mais robusta
                        try:
                            # Limpar string do valor (remover R$, espaços, etc.)
                            valor_emprestado_clean = valor_emprestado_str.replace('R$', '').replace(',', '.').replace(' ', '')
                            valor_emprestado = float(valor_emprestado_clean)
                            
                            # Validar se o valor é válido e maior que zero
                            if valor_emprestado <= 0:
                                import_stats['errors'].append(f"Aba '{sheet_name}', linha {idx+2}: Valor emprestado deve ser maior que zero: {valor_emprestado}")
                                continue
                                
                        except:
                            import_stats['errors'].append(f"Aba '{sheet_name}', linha {idx+2}: Valor emprestado inválido: {valor_emprestado_str}")
                            continue
                        
                        try:
                            valor_receber_raw = row.get(actual_columns['valor a receber'], '')
                            valor_receber_str = str(valor_receber_raw).strip() if valor_receber_raw and str(valor_receber_raw).lower() not in ['nan', 'none', ''] else ""
                            if valor_receber_str:
                                valor_receber_clean = valor_receber_str.replace('R$', '').replace(',', '.').replace(' ', '')
                                valor_receber = float(valor_receber_clean)
                            else:
                                valor_receber = valor_emprestado * 1.2  # 20% de juros padrão
                        except:
                            valor_receber = valor_emprestado * 1.2  # Usar juros padrão se erro
                        
                        # Converter data de pagamento de forma mais robusta
                        try:
                            data_pagamento_raw = row.get(actual_columns['data de pagamento'], '')
                            data_pagamento_str = str(data_pagamento_raw).strip() if data_pagamento_raw and str(data_pagamento_raw).lower() not in ['nan', 'none', ''] else ""
                            if data_pagamento_str:
                                # Tentar diferentes formatos de data
                                try:
                                    payment_date = pd.to_datetime(data_pagamento_str, format='%d/%m/%Y').date()
                                except:
                                    try:
                                        payment_date = pd.to_datetime(data_pagamento_str).date()
                                    except:
                                        payment_date = date.today() + timedelta(days=30)
                            else:
                                payment_date = date.today() + timedelta(days=30)
                        except:
                            payment_date = date.today() + timedelta(days=30)
                        
                        # Processar status
                        status_raw = row.get(actual_columns['status'], '')
                        status_str = str(status_raw).strip() if status_raw and str(status_raw).lower() not in ['nan', 'none', ''] else "pendente"
                        
                        # Mapear status possíveis - aceita maiúsculas e minúsculas
                        status_map = {
                            # Minúsculas
                            'pago': 'pago',
                            'paga': 'pago',
                            'pendente': 'pendente',
                            'atrasado': 'atrasado',
                            'atrasada': 'atrasado',
                            'em atraso': 'atrasado',
                            # Maiúsculas
                            'PAGO': 'pago',
                            'PAGA': 'pago',
                            'PENDENTE': 'pendente',
                            'ATRASADO': 'atrasado',
                            'ATRASADA': 'atrasado',
                            'EM ATRASO': 'atrasado',
                            # Primeira letra maiúscula
                            'Pago': 'pago',
                            'Paga': 'pago',
                            'Pendente': 'pendente',
                            'Atrasado': 'atrasado',
                            'Atrasada': 'atrasado',
                            'Em atraso': 'atrasado'
                        }
                        
                        status = status_map.get(status_str, 'pendente')
                        
                        # Calcular taxa de juros baseada nos valores da planilha
                        if valor_emprestado > 0:
                            taxa_juros = ((valor_receber - valor_emprestado) / valor_emprestado) * 100
                        else:
                            taxa_juros = 20.0  # Taxa padrão de 20%
                        
                        # Criar registro do empréstimo
                        loan_data = {
                            'nome_cliente': cliente,
                            'telefone': '',  # Não disponível na planilha
                            'valor_solicitado': valor_emprestado,
                            'taxa_juros': taxa_juros,  # Campo obrigatório
                            'valor_total_planilha': valor_receber,  # Valor exato da planilha
                            'data_pagamento': payment_date,
                            'data_emprestimo': date(2024, month_num, 1),  # Primeiro dia do mês
                            'parcelas': 1,  # Campo obrigatório - padrão 1 parcela
                            'status': status,  # Status da planilha
                            'tipo': 'emprestimos'  # Padrão
                        }
                        
                        processed_data.append(loan_data)
                        import_stats['total_loans'] += 1
                        import_stats['total_value'] += loan_data['valor_solicitado']
                        
                    except Exception as e:
                        import_stats['errors'].append(f"Aba '{sheet_name}', linha {idx+2}: {str(e)}")
                
                # Resumo do processamento da aba
                import_stats['errors'].append(f"DEBUG - Aba '{sheet_name}': {linhas_processadas} linhas processadas, {linhas_puladas} linhas puladas")
                
                # Calcular valor total da aba para debug
                if linhas_processadas > 0:
                    aba_valor_total = sum(loan['valor_solicitado'] for loan in processed_data[-linhas_processadas:])
                    import_stats['loans_per_month'][sheet_name] = linhas_processadas
                    import_stats['errors'].append(f"DEBUG - Aba '{sheet_name}': Valor total processado R$ {aba_valor_total:,.2f}")
                    import_stats['months_processed'] += 1
        
        # Resumo final detalhado
        total_valor_planilha = sum(loan.get('valor_total_planilha', loan.get('valor_solicitado', 0)) for loan in processed_data)
        import_stats['errors'].append(f"DEBUG - RESUMO FINAL:")
        import_stats['errors'].append(f"DEBUG - Total de empréstimos processados: {len(processed_data)}")
        import_stats['errors'].append(f"DEBUG - Valor total emprestado: R$ {import_stats['total_value']:,.2f}")
        import_stats['errors'].append(f"DEBUG - Valor total a receber: R$ {total_valor_planilha:,.2f}")
        import_stats['errors'].append(f"DEBUG - Meses processados: {import_stats['months_processed']}")
        
        # Resumo por mês
        if import_stats['loans_per_month']:
            import_stats['errors'].append(f"DEBUG - Empréstimos por mês:")
            for month, count in import_stats['loans_per_month'].items():
                import_stats['errors'].append(f"DEBUG -   {month}: {count} empréstimos")
        
        return {
            'success': True,
            'data': processed_data,
            'stats': import_stats
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Erro ao processar arquivo: {str(e)}",
            'data': [],
            'stats': {'total_loans': 0, 'total_value': 0, 'months_processed': 0, 'errors': []}
        }

def import_loans_data(loans_data):
    """
    Importa dados processados para o sistema
    
    Args:
        loans_data: Lista de dados de empréstimos processados
    
    Returns:
        dict: Resultado da importação
    """
    import_results = {
        'imported': 0,
        'errors': [],
        'clients_added': 0,
        'debug_info': []
    }
    
    # Debug: mostrar quantos dados foram recebidos
    import_results['debug_info'].append(f"DEBUG - Recebidos {len(loans_data)} empréstimos para importar")
    
    if not loans_data:
        import_results['errors'].append("DEBUG - Lista de empréstimos está vazia")
        return import_results
    
    # Agrupar por cliente para otimizar
    clients_added = set()
    
    for idx, loan_data in enumerate(loans_data):
        try:
            # Debug: mostrar dados do empréstimo
            import_results['debug_info'].append(f"DEBUG - Processando empréstimo {idx+1}: {loan_data.get('nome_cliente', 'N/A')}")
            
            # Validar e corrigir dados obrigatórios
            required_fields = ['nome_cliente', 'valor_solicitado', 'data_pagamento', 'tipo']
            
            # Corrigir valor_solicitado se estiver vazio ou inválido
            if not loan_data.get('valor_solicitado') or loan_data.get('valor_solicitado') == 0:
                # Tentar usar valor_total_planilha como fallback
                if loan_data.get('valor_total_planilha') and loan_data.get('valor_total_planilha') > 0:
                    # Se temos valor total, usar 80% como valor solicitado (estimativa)
                    loan_data['valor_solicitado'] = loan_data['valor_total_planilha'] * 0.8
                    import_results['debug_info'].append(f"DEBUG - Empréstimo {idx+1}: valor_solicitado corrigido usando valor_total_planilha * 0.8 = {loan_data['valor_solicitado']}")
                else:
                    # Se não temos nenhum valor, usar valor padrão
                    loan_data['valor_solicitado'] = 100.0
                    import_results['debug_info'].append(f"DEBUG - Empréstimo {idx+1}: valor_solicitado definido como padrão R$ 100,00")
            
            missing_fields = [field for field in required_fields if not loan_data.get(field)]
            
            if missing_fields:
                import_results['errors'].append(f"Empréstimo {idx+1} ({loan_data.get('nome_cliente', 'N/A')}): Campos obrigatórios faltando: {missing_fields}")
                continue
            
            # Adicionar cliente se não existir
            if loan_data['nome_cliente'] not in clients_added:
                client_result = db.add_client(loan_data['nome_cliente'], loan_data['telefone'], loan_data['tipo'])
                import_results['debug_info'].append(f"DEBUG - Cliente {loan_data['nome_cliente']}: add_client retornou {client_result}")
                clients_added.add(loan_data['nome_cliente'])
                import_results['clients_added'] += 1
            
            # Adicionar empréstimo
            loan_result = db.add_loan(loan_data, loan_data['tipo'])
            import_results['debug_info'].append(f"DEBUG - Empréstimo {loan_data['nome_cliente']}: add_loan retornou {loan_result}")
            
            if loan_result:
                import_results['imported'] += 1
            else:
                import_results['errors'].append(f"Erro ao adicionar empréstimo para {loan_data['nome_cliente']} - add_loan retornou False")
                
        except Exception as e:
            import_results['errors'].append(f"Erro ao importar {loan_data.get('nome_cliente', 'N/A')}: {str(e)}")
            import_results['debug_info'].append(f"DEBUG - Exceção no empréstimo {idx+1}: {str(e)}")
    
    # Debug: resumo final
    import_results['debug_info'].append(f"DEBUG - Resumo: {import_results['imported']} importados, {import_results['clients_added']} clientes adicionados, {len(import_results['errors'])} erros")
    
    return import_results

def login_page():
    st.title("🔐 Login - Sistema de Empréstimos")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Faça login para acessar o sistema")
        
        with st.form("login_form"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submit_button = st.form_submit_button("Entrar")
            
            if submit_button:
                if db.authenticate_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user_role = db.get_user_role(username)
                    st.success("Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos!")
        
        st.markdown("---")
        st.markdown("**Usuário Admin:** admin | **Senha:** admin123")
        st.markdown("**💡 Dica:** Para solicitar acesso administrativo, use um nome de usuário que termine com `.admin` (ex: `joao.admin`)")
        
        # Link para esqueci a senha
        if st.button("🔑 Esqueci minha senha"):
            st.session_state.show_forgot_password = True
            st.rerun()

def register_page():
    st.title("📝 Cadastro de Usuário")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("register_form"):
            st.markdown("### Criar nova conta")
            new_username = st.text_input("Novo usuário")
            new_password = st.text_input("Nova senha", type="password")
            confirm_password = st.text_input("Confirmar senha", type="password")
            submit_button = st.form_submit_button("Cadastrar")
            
            if submit_button:
                if new_password != confirm_password:
                    st.error("As senhas não coincidem!")
                elif len(new_password) < 6:
                    st.error("A senha deve ter pelo menos 6 caracteres!")
                elif new_username.endswith('.admin'):
                    # Usuário com .admin - criar solicitação
                    success, message = db.create_admin_request(new_username, new_password)
                    if success:
                        st.success(message)
                        st.info("🔔 Uma notificação foi enviada para os administradores sobre sua solicitação.")
                    else:
                        st.error(message)
                elif db.create_user(new_username, new_password):
                    st.success("Usuário criado com sucesso!")
                else:
                    st.error("Usuário já existe!")

def admin_dashboard_page():
    st.title("📊 Dashboard Admin - Visão Geral Completa")
    
    # Verificar solicitações pendentes
    admin_requests = db.get_admin_requests()
    if admin_requests:
        st.warning(f"🔔 Você tem {len(admin_requests)} solicitação(ões) de admin pendente(s)! Acesse 'Gerenciar Permissões' para revisar.")
    
    # Obter métricas consolidadas
    consolidated_metrics = db.get_consolidated_metrics()
    
    # Métricas totais
    total_metrics = consolidated_metrics['total']
    
    # Cards de métricas totais
    st.subheader("📈 Resumo Geral")
    
    # Métricas principais - responsivas
    metrics_data = [
        {
            'label': "💰 Total Emprestado",
            'value': f"R$ {total_metrics['total_emprestado']:,.2f}",
            'delta': None
        },
        {
            'label': "📈 Total com Juros", 
            'value': f"R$ {total_metrics['total_com_juros']:,.2f}",
            'delta': f"R$ {total_metrics['total_com_juros'] - total_metrics['total_emprestado']:,.2f}"
        },
        {
            'label': "✅ Total Pago",
            'value': f"R$ {total_metrics['total_pago']:,.2f}",
            'delta': None
        },
        {
            'label': "⏳ A Receber",
            'value': f"R$ {total_metrics['total_pendente']:,.2f}",
            'delta': None
        },
        {
            'label': "💵 Valor Líquido",
            'value': f"R$ {total_metrics['valor_liquido']:,.2f}",
            'delta': None
        },
        {
            'label': "📊 Total Empréstimos",
            'value': total_metrics['total_emprestimos'],
            'delta': None
        }
    ]
    
    create_responsive_metrics(metrics_data, num_cols=3)
    
    st.markdown("---")
    
    # Métricas por tipo
    st.subheader("📋 Resumo por Categoria")
    
    # Métricas por categoria - responsivas
    cols = create_responsive_columns(3)
    
    with cols[0]:
        st.markdown("#### 🏦 Empréstimos Clientes")
        emp_metrics = consolidated_metrics['emprestimos']
        st.metric("Valor Total", f"R$ {emp_metrics['total_com_juros']:,.2f}")
        st.metric("Quantidade", emp_metrics['total_emprestimos'])
        st.metric("A Receber", f"R$ {emp_metrics['total_pendente']:,.2f}")
    
    with cols[1]:
        st.markdown("#### 🚛 Motoristas")
        mot_metrics = consolidated_metrics['motoristas']
        st.metric("Valor Total", f"R$ {mot_metrics['total_com_juros']:,.2f}")
        st.metric("Quantidade", mot_metrics['total_emprestimos'])
        st.metric("A Receber", f"R$ {mot_metrics['total_pendente']:,.2f}")
    
    with cols[2]:
        st.markdown("#### 🏪 Comerciantes")
        com_metrics = consolidated_metrics['comerciantes']
        st.metric("Valor Total", f"R$ {com_metrics['total_com_juros']:,.2f}")
        st.metric("Quantidade", com_metrics['total_emprestimos'])
        st.metric("A Receber", f"R$ {com_metrics['total_pendente']:,.2f}")
    
    st.markdown("---")
    
    # Gráficos responsivos
    cols = create_responsive_columns(2)
    
    with cols[0]:
        st.subheader("📊 Status por Categoria")
        all_df = db.get_all_loans()
        if not all_df.empty:
            # Gráfico de pizza por status
            status_counts = all_df['status'].value_counts()
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Distribuição por Status",
                color_discrete_map={
                    'pago': '#28a745',
                    'pendente': '#ffc107',
                    'atrasado': '#dc3545'
                }
            )
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum empréstimo cadastrado ainda.")
    
    with cols[1]:
        st.subheader("📈 Empréstimos por Categoria")
        if not all_df.empty:
            # Gráfico de barras por tipo
            tipo_counts = all_df['tipo'].value_counts()
            fig = px.bar(
                x=tipo_counts.index,
                y=tipo_counts.values,
                title="Quantidade por Categoria",
                labels={'x': 'Categoria', 'y': 'Quantidade'},
                color=tipo_counts.values,
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum empréstimo cadastrado ainda.")
    
    # Gráfico de evolução mensal
    st.subheader("📅 Evolução Mensal por Categoria")
    if not all_df.empty:
        all_df['mes'] = all_df['data_emprestimo'].dt.to_period('M')
        monthly_data = all_df.groupby(['mes', 'tipo'])['valor_solicitado'].sum().reset_index()
        monthly_data['mes'] = monthly_data['mes'].astype(str)
        
        fig = px.bar(
            monthly_data,
            x='mes',
            y='valor_solicitado',
            color='tipo',
            title="Empréstimos por Mês e Categoria",
            labels={'valor_solicitado': 'Valor (R$)', 'mes': 'Mês', 'tipo': 'Categoria'},
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum empréstimo cadastrado ainda.")
    
    st.markdown("---")

def user_dashboard_page():
    st.title("📋 Meus Empréstimos - Visão do Funcionário")
    
    # Obter todos os empréstimos
    df = db.get_all_loans()
    
    if df.empty:
        st.info("Nenhum empréstimo cadastrado ainda.")
        return
    
    # Estatísticas básicas para funcionários - responsivas
    user_metrics = [
        {
            'label': "📊 Total de Empréstimos",
            'value': len(df),
            'delta': None
        },
        {
            'label': "⏳ Empréstimos Pendentes",
            'value': len(df[df['status'] == 'pendente']),
            'delta': None
        },
        {
            'label': "🚨 Empréstimos Atrasados",
            'value': len(df[df['status'] == 'atrasado']),
            'delta': None
        }
    ]
    
    create_responsive_metrics(user_metrics, num_cols=3)
    
    st.markdown("---")
    
    # Filtros para funcionários
    st.markdown("#### 🔍 Filtros")
    
    # Primeira linha de filtros - responsivos
    cols = create_responsive_columns(3)
    
    with cols[0]:
        status_filter = st.selectbox(
            "Filtrar por Status",
            ["Todos", "Pendente", "Atrasado", "Pago"]
        )
    
    with cols[1]:
        tipo_filter = st.selectbox(
            "Filtrar por Tipo",
            ["Todos", "Empréstimos", "Motoristas", "Comerciantes"]
        )
    
    with cols[2]:
        search_name = st.text_input("🔍 Buscar Cliente")
    
    # Segunda linha - filtros de período - responsivos
    cols2 = create_responsive_columns(2)
    
    with cols2[0]:
        period_filter = st.selectbox(
            "Filtrar por Período",
            ["Todos", "Última semana", "Últimos 15 dias", "Último mês", "Últimos 3 meses", "Personalizado"]
        )
    
    with cols2[1]:
        if period_filter == "Personalizado":
            st.markdown("**Período Personalizado**")
            start_date, end_date = get_date_range_selector()
        else:
            start_date, end_date = None, None
            
            # Aplicar filtros automáticos de período
            if period_filter == "Última semana":
                start_date = date.today() - timedelta(days=7)
                end_date = date.today()
            elif period_filter == "Últimos 15 dias":
                start_date = date.today() - timedelta(days=15)
                end_date = date.today()
            elif period_filter == "Último mês":
                start_date = date.today() - timedelta(days=30)
                end_date = date.today()
            elif period_filter == "Últimos 3 meses":
                start_date = date.today() - timedelta(days=90)
                end_date = date.today()
    
    # Aplicar filtros
    filtered_df = df.copy()
    
    if status_filter != "Todos":
        status_map = {
            "Pendente": "pendente",
            "Atrasado": "atrasado", 
            "Pago": "pago"
        }
        filtered_df = filtered_df[filtered_df['status'] == status_map[status_filter]]
    
    if tipo_filter != "Todos":
        tipo_map = {
            "Empréstimos": "emprestimos Clientes",
            "Motoristas": "motoristas",
            "Comerciantes": "comerciantes"
        }
        filtered_df = filtered_df[filtered_df['tipo'] == tipo_map[tipo_filter]]
    
    if search_name:
        filtered_df = filtered_df[
            filtered_df['nome_cliente'].str.contains(search_name, case=False, na=False)
        ]
    
    # Aplicar filtro de período
    if period_filter != "Todos" and start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df['data_emprestimo'].dt.date >= start_date) & 
            (filtered_df['data_emprestimo'].dt.date <= end_date)
        ]
    
    # Mostrar informações do filtro aplicado
    if period_filter != "Todos" and start_date and end_date:
        st.info(f"📅 Mostrando empréstimos de {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}")
    
    # Exibir empréstimos filtrados
    if not filtered_df.empty:
        st.subheader("📋 Lista de Empréstimos")
        
        # Formatar dados para exibição
        display_df = filtered_df[['nome_cliente', 'telefone', 'valor_solicitado', 'data_emprestimo', 'data_pagamento', 'status', 'tipo']].copy()
        display_df['valor_solicitado'] = display_df['valor_solicitado'].apply(lambda x: f"R$ {x:,.2f}")
        
        # Converter datas para string se necessário
        if pd.api.types.is_datetime64_any_dtype(display_df['data_emprestimo']):
            display_df['data_emprestimo'] = display_df['data_emprestimo'].dt.strftime('%d/%m/%Y')
        else:
            display_df['data_emprestimo'] = display_df['data_emprestimo'].astype(str)
            
        if pd.api.types.is_datetime64_any_dtype(display_df['data_pagamento']):
            display_df['data_pagamento'] = display_df['data_pagamento'].dt.strftime('%d/%m/%Y')
        else:
            display_df['data_pagamento'] = display_df['data_pagamento'].astype(str)
        
        # Mapear tipos para nomes mais amigáveis
        tipo_map = {
            'emprestimos': '🏦 Geral',
            'motoristas': '🚛 Motorista',
            'comerciantes': '🏪 Comerciante'
        }
        display_df['tipo'] = display_df['tipo'].map(tipo_map)
        
        # Renomear colunas
        display_df = display_df.rename(columns={
            'nome_cliente': 'Cliente',
            'telefone': 'Telefone',
            'valor_solicitado': 'Valor',
            'data_emprestimo': 'Data Empréstimo',
            'data_pagamento': 'Data Pagamento',
            'status': 'Status',
            'tipo': 'Tipo'
        })
        
        # Função para colorir status
        def color_status(val):
            if val == 'pago':
                return 'background-color: #d4edda; color: #155724'
            elif val == 'pendente':
                return 'background-color: #fff3cd; color: #856404'
            elif val == 'atrasado':
                return 'background-color: #f8d7da; color: #721c24'
            return ''
        
        # Aplicar estilo
        styled_df = display_df.style.map(color_status, subset=['Status'])
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Ações rápidas para funcionários - responsivas
        st.subheader("⚡ Ações Rápidas")
        cols = create_responsive_columns(3)
        
        with cols[0]:
            if st.button("📞 Contatar Clientes Atrasados", key="contact_overdue_users"):
                atrasados = filtered_df[filtered_df['status'] == 'atrasado']
                if not atrasados.empty:
                    st.success(f"Lista de {len(atrasados)} clientes atrasados para contato!")
                    for _, row in atrasados.iterrows():
                        st.write(f"📞 {row['nome_cliente']} - {row['telefone']}")
                else:
                    st.info("Nenhum cliente atrasado encontrado.")
        
        with cols[1]:
            if st.button("📅 Ver Vencimentos Hoje", key="check_today_due"):
                hoje = date.today()
                vencimentos_hoje = filtered_df[filtered_df['data_pagamento'].dt.date == hoje]
                if not vencimentos_hoje.empty:
                    st.warning(f"⚠️ {len(vencimentos_hoje)} empréstimo(s) vence(m) hoje!")
                    for _, row in vencimentos_hoje.iterrows():
                        st.write(f"📅 {row['nome_cliente']} - R$ {row['valor_solicitado']:,.2f}")
                else:
                    st.success("✅ Nenhum vencimento para hoje!")
        
        with cols[2]:
            if st.button("🗑️ Deletar Selecionados", key="delete_user_selected", type="secondary"):
                st.session_state.show_user_delete_confirmation = True
                st.session_state.user_delete_loans = filtered_df[['id', 'nome_cliente', 'valor_solicitado', 'tipo']].to_dict('records')
                st.rerun()
        
        # Confirmação de exclusão para funcionários
        if st.session_state.get('show_user_delete_confirmation', False):
            st.markdown("---")
            st.subheader("⚠️ Confirmação de Exclusão")
            
            st.warning("**ATENÇÃO:** Esta ação não pode ser desfeita!")
            st.write("**Empréstimos que serão deletados:**")
            
            for loan in st.session_state.get('user_delete_loans', []):
                tipo_map = {
                    'emprestimos': '🏦 Clientes',
                    'motoristas': '🚛 Motorista',
                    'comerciantes': '🏪 Comerciante'
                }
                tipo_nome = tipo_map.get(loan['tipo'], loan['tipo'])
                st.write(f"- ID {loan['id']}: {loan['nome_cliente']} - R$ {loan['valor_solicitado']:,.2f} ({tipo_nome})")
            
            col_confirm, col_cancel = st.columns(2)
            
            with col_confirm:
                if st.button("✅ Confirmar Exclusão", key="confirm_user_delete", type="primary"):
                    deleted_count = 0
                    for loan in st.session_state.get('user_delete_loans', []):
                        success, message = db.delete_loan(loan['id'], loan['tipo'])
                        if success:
                            deleted_count += 1
                    
                    if deleted_count > 0:
                        st.success(f"✅ {deleted_count} empréstimo(s) deletado(s) com sucesso!")
                    else:
                        st.error("❌ Nenhum empréstimo foi deletado.")
                    
                    # Limpar estado
                    if 'show_user_delete_confirmation' in st.session_state:
                        del st.session_state.show_user_delete_confirmation
                    if 'user_delete_loans' in st.session_state:
                        del st.session_state.user_delete_loans
                    
                    st.rerun()
            
            with col_cancel:
                if st.button("❌ Cancelar", key="cancel_user_delete"):
                    # Limpar estado
                    if 'show_user_delete_confirmation' in st.session_state:
                        del st.session_state.show_user_delete_confirmation
                    if 'user_delete_loans' in st.session_state:
                        del st.session_state.user_delete_loans
                    st.rerun()
    else:
        st.warning("Nenhum empréstimo encontrado com os filtros aplicados.")
    
    # Dicas para funcionários
    st.markdown("---")
    st.subheader("💡 Dicas para Funcionários")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **📞 Contato com Clientes:**
        - Sempre seja cordial e profissional
        - Confirme os dados antes de falar sobre valores
        - Ofereça opções de pagamento quando possível
        """)
    
    with col2:
        st.info("""
        **📋 Atualização de Status:**
        - Use a aba "Empréstimos" para atualizar status
        - Marque como "Pago" apenas após confirmação
        - Alerte sobre atrasos imediatamente
        """)

def forgot_password_page():
    st.title("🔑 Recuperar Senha")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Digite seu usuário para receber um link de recuperação")
        
        with st.form("forgot_password_form"):
            username = st.text_input("Usuário")
            submit_button = st.form_submit_button("Enviar Link de Recuperação")
            
            if submit_button:
                if username:
                    token = db.generate_reset_token(username)
                    if token:
                        # Em um sistema real, aqui você enviaria por email
                        # Por enquanto, vamos mostrar o token na tela para demonstração
                        st.success("Token de recuperação gerado com sucesso!")
                        st.info(f"""
                        **Token de Recuperação (válido por 1 hora):**
                        ```
                        {token}
                        ```
                        
                        **⚠️ IMPORTANTE:** 
                        - Este token expira em 1 hora
                        - Use-o na próxima página para redefinir sua senha
                        - Em um sistema real, este token seria enviado por email
                        """)
                        
                        # Salvar token na sessão para facilitar o teste
                        st.session_state.reset_token = token
                        st.session_state.show_reset_password = True
                    else:
                        st.error("Usuário não encontrado!")
                else:
                    st.error("Por favor, digite seu usuário!")
        
        st.markdown("---")
        if st.button("⬅️ Voltar ao Login"):
            st.session_state.show_forgot_password = False
            st.rerun()

def reset_password_page():
    st.title("🔐 Redefinir Senha")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Digite o token de recuperação e sua nova senha")
        
        with st.form("reset_password_form"):
            token = st.text_input("Token de Recuperação", value=st.session_state.get('reset_token', ''))
            new_password = st.text_input("Nova Senha", type="password")
            confirm_password = st.text_input("Confirmar Nova Senha", type="password")
            submit_button = st.form_submit_button("Redefinir Senha")
            
            if submit_button:
                if not all([token, new_password, confirm_password]):
                    st.error("Por favor, preencha todos os campos!")
                elif new_password != confirm_password:
                    st.error("As senhas não coincidem!")
                elif len(new_password) < 6:
                    st.error("A senha deve ter pelo menos 6 caracteres!")
                else:
                    if db.reset_password(token, new_password):
                        st.success("Senha redefinida com sucesso!")
                        st.info("Você pode fazer login com sua nova senha.")
                        
                        # Limpar sessão
                        if 'reset_token' in st.session_state:
                            del st.session_state.reset_token
                        if 'show_reset_password' in st.session_state:
                            del st.session_state.show_reset_password
                        if 'show_forgot_password' in st.session_state:
                            del st.session_state.show_forgot_password
                        
                        st.rerun()
                    else:
                        st.error("Token inválido ou expirado!")
        
        st.markdown("---")
        if st.button("⬅️ Voltar"):
            if 'show_reset_password' in st.session_state:
                del st.session_state.show_reset_password
            st.rerun()

def loans_detail_page(loan_type='emprestimos'):
    """Página de detalhamento de empréstimos por tipo"""
    type_names = {
        'emprestimos': 'Empréstimos Clientes',
        'motoristas': 'Motoristas',
        'comerciantes': 'Comerciantes'
    }
    
    type_icons = {
        'emprestimos': '🏦',
        'motoristas': '🚛',
        'comerciantes': '🏪'
    }
    
    st.title(f"{type_icons[loan_type]} {type_names[loan_type]}")
    
    # Seção de clientes - versão melhorada e organizada
    st.subheader("👥 Clientes Cadastrados")
    clients_df = db.get_clients(loan_type)
    
    if not clients_df.empty:
        # Estatísticas rápidas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Clientes", len(clients_df))
        with col2:
            # Contar empréstimos por cliente
            df_loans = db.get_loans(loan_type)
            if not df_loans.empty:
                loans_per_client = df_loans['nome_cliente'].value_counts()
                avg_loans = loans_per_client.mean()
                st.metric("Média Empréstimos/Cliente", f"{avg_loans:.1f}")
            else:
                st.metric("Média Empréstimos/Cliente", "0")
        with col3:
            # Cliente com mais empréstimos
            if not df_loans.empty:
                top_client = loans_per_client.index[0]
                top_loans = loans_per_client.iloc[0]
                st.metric("Top Cliente", f"{top_client[:15]}...")
            else:
                st.metric("Top Cliente", "-")
        
        st.markdown("---")
    else:
        st.info(f"📝 Nenhum cliente cadastrado para {type_names[loan_type].lower()} ainda.")
        st.markdown("💡 **Dica:** Clientes são adicionados automaticamente quando você cadastra empréstimos.")
    
    st.markdown("---")
    
    df = db.get_loans(loan_type)
    
    if df.empty:
        st.info(f"Nenhum empréstimo de {type_names[loan_type].lower()} cadastrado ainda.")
        return
    
    # Filtros
    st.markdown("#### 🔍 Filtros")
    
    # Primeira linha de filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Filtrar por Status",
            ["Todos"] + list(df['status'].unique())
        )
    
    with col2:
        search_name = st.text_input("Buscar por Nome")
    
    with col3:
        period_filter = st.selectbox(
            "Filtrar por Período",
            ["Todos", "Última semana", "Últimos 15 dias", "Último mês", "Últimos 3 meses", "Personalizado"]
        )
    
    # Segunda linha - filtros de data (aparece se "Personalizado" for selecionado)
    if period_filter == "Personalizado":
        st.markdown("#### 📅 Período Personalizado")
        start_date, end_date = get_date_range_selector()
    else:
        start_date, end_date = None, None
        
        # Aplicar filtros automáticos de período
        if period_filter == "Última semana":
            start_date = date.today() - timedelta(days=7)
            end_date = date.today()
        elif period_filter == "Últimos 15 dias":
            start_date = date.today() - timedelta(days=15)
            end_date = date.today()
        elif period_filter == "Último mês":
            start_date = date.today() - timedelta(days=30)
            end_date = date.today()
        elif period_filter == "Últimos 3 meses":
            start_date = date.today() - timedelta(days=90)
            end_date = date.today()
    
    # Aplicar filtros
    filtered_df = df.copy()
    
    if status_filter != "Todos":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    if search_name:
        filtered_df = filtered_df[
            filtered_df['nome_cliente'].str.contains(search_name, case=False, na=False)
        ]
    
    # Aplicar filtro de período
    if period_filter != "Todos" and start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df['data_emprestimo'].dt.date >= start_date) & 
            (filtered_df['data_emprestimo'].dt.date <= end_date)
        ]
    
    # Mostrar informações do filtro aplicado
    if period_filter != "Todos" and start_date and end_date:
        st.info(f"📅 Mostrando empréstimos de {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}")
    
    # Função para colorir status
    def color_status(val):
        if val == 'pago':
            return 'background-color: #d4edda; color: #155724'
        elif val == 'pendente':
            return 'background-color: #fff3cd; color: #856404'
        elif val == 'atrasado':
            return 'background-color: #f8d7da; color: #721c24'
        return ''
    
    # Mostrar resumo quando há filtros aplicados
    if not filtered_df.empty and (status_filter != "Todos" or search_name or period_filter != "Todos"):
        st.markdown("#### 📊 Resumo dos Filtros Aplicados")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Empréstimos Encontrados", len(filtered_df))
        
        with col2:
            valor_total = filtered_df['valor_solicitado'].sum()
            st.metric("Valor Total", f"R$ {valor_total:,.2f}")
        
        with col3:
            valor_pago = filtered_df['valor_pago'].sum()
            st.metric("Valor Pago", f"R$ {valor_pago:,.2f}")
        
        with col4:
            valor_pendente = filtered_df['valor_total'].sum() - valor_pago
            st.metric("Valor Pendente", f"R$ {valor_pendente:,.2f}")
        
        st.markdown("---")
    
    # Exibir tabela
    if not filtered_df.empty:
        # Formatar colunas para exibição
        display_df = filtered_df.copy()
        display_df['valor_solicitado'] = display_df['valor_solicitado'].apply(lambda x: f"R$ {x:,.2f}")
        display_df['valor_total'] = display_df['valor_total'].apply(lambda x: f"R$ {x:,.2f}")
        display_df['valor_pago'] = display_df['valor_pago'].apply(lambda x: f"R$ {x:,.2f}")
        display_df['taxa_juros'] = display_df['taxa_juros'].apply(lambda x: f"{x:.1f}%")
        # Converter datas para string se necessário
        if pd.api.types.is_datetime64_any_dtype(display_df['data_emprestimo']):
            display_df['data_emprestimo'] = display_df['data_emprestimo'].dt.strftime('%d/%m/%Y')
        else:
            display_df['data_emprestimo'] = display_df['data_emprestimo'].astype(str)
            
        if pd.api.types.is_datetime64_any_dtype(display_df['data_pagamento']):
            display_df['data_pagamento'] = display_df['data_pagamento'].dt.strftime('%d/%m/%Y')
        else:
            display_df['data_pagamento'] = display_df['data_pagamento'].astype(str)
        
        # Renomear colunas
        display_df = display_df.rename(columns={
            'nome_cliente': 'Cliente',
            'telefone': 'Telefone',
            'valor_solicitado': 'Valor Emprestado',
            'taxa_juros': 'Taxa Juros (%)',
            'data_emprestimo': 'Data Empréstimo',
            'data_pagamento': 'Data Pagamento',
            'parcelas': 'Parcelas',
            'valor_total': 'Valor Total',
            'valor_pago': 'Valor Pago',
            'status': 'Status'
        })
        
        # Aplicar estilo
        styled_df = display_df.style.map(color_status, subset=['Status'])
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True
        )
        # Ações em lote
        st.subheader("🔧 Ações em Lote")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Atualizar Status para Pago", key=f"update_paid_{loan_type}"):
                for idx, row in filtered_df.iterrows():
                    db.update_loan_status(row['id'], 'pago', row['valor_total'], loan_type)
                st.success("Status atualizado para todos os empréstimos selecionados!")
                st.rerun()
        
        with col2:
            if st.button("Marcar como Atrasado", key=f"update_overdue_{loan_type}"):
                for idx, row in filtered_df.iterrows():
                    if row['status'] != 'pago':
                        db.update_loan_status(row['id'], 'atrasado', loan_type=loan_type)
                st.success("Status atualizado para atrasado!")
                st.rerun()
        
        with col3:
            if st.button("🗑️ Deletar Selecionados", key=f"delete_batch_{loan_type}", type="secondary"):
                st.session_state.show_delete_confirmation = True
                st.session_state.delete_loan_type = loan_type
                st.session_state.delete_loans = filtered_df[['id', 'nome_cliente', 'valor_solicitado']].to_dict('records')
                st.rerun()
        
        # Confirmação de exclusão
        if st.session_state.get('show_delete_confirmation', False) and st.session_state.get('delete_loan_type') == loan_type:
            st.markdown("---")
            st.subheader("⚠️ Confirmação de Exclusão")
            
            st.warning("**ATENÇÃO:** Esta ação não pode ser desfeita!")
            st.write("**Empréstimos que serão deletados:**")
            
            for loan in st.session_state.get('delete_loans', []):
                st.write(f"- ID {loan['id']}: {loan['nome_cliente']} - R$ {loan['valor_solicitado']:,.2f}")
            
            col_confirm, col_cancel = st.columns(2)
            
            with col_confirm:
                confirm_batch_key = f"confirm_batch_delete_{loan_type}"
                if st.button("✅ Confirmar Exclusão", key=confirm_batch_key, type="primary"):
                    deleted_count = 0
                    for loan in st.session_state.get('delete_loans', []):
                        success, message = db.delete_loan(loan['id'], loan_type)
                        if success:
                            deleted_count += 1
                    
                    if deleted_count > 0:
                        st.success(f"✅ {deleted_count} empréstimo(s) deletado(s) com sucesso!")
                    else:
                        st.error("❌ Nenhum empréstimo foi deletado.")
                    
                    # Limpar estado
                    if 'show_delete_confirmation' in st.session_state:
                        del st.session_state.show_delete_confirmation
                    if 'delete_loan_type' in st.session_state:
                        del st.session_state.delete_loan_type
                    if 'delete_loans' in st.session_state:
                        del st.session_state.delete_loans
                    
                    st.rerun()
            
            with col_cancel:
                cancel_batch_key = f"cancel_batch_delete_{loan_type}"
                if st.button("❌ Cancelar", key=cancel_batch_key):
                    # Limpar estado
                    if 'show_delete_confirmation' in st.session_state:
                        del st.session_state.show_delete_confirmation
                    if 'delete_loan_type' in st.session_state:
                        del st.session_state.delete_loan_type
                    if 'delete_loans' in st.session_state:
                        del st.session_state.delete_loans
                    st.rerun()
    else:
        st.warning("Nenhum empréstimo encontrado com os filtros aplicados.")

def add_loan_page(loan_type='emprestimos'):
    """Página de cadastro de empréstimos por tipo"""
    type_names = {
        'emprestimos': 'Empréstimo Clientes',
        'motoristas': 'Empréstimo para Motorista',
        'comerciantes': 'Empréstimo para Comerciante'
    }
    
    type_icons = {
        'emprestimos': '🏦',
        'motoristas': '🚛',
        'comerciantes': '🏪'
    }
    
    st.title(f"➕ {type_icons[loan_type]} Cadastro de {type_names[loan_type]}")
    
    with st.form("add_loan_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome_cliente = st.text_input("Nome Completo do Cliente *", placeholder="Ex: João Silva")
            telefone = st.text_input("Telefone *", placeholder="Ex: (11) 99999-9999")
            valor_solicitado = st.number_input("Valor Solicitado (R$) *", min_value=0.01, step=0.01, format="%.2f")
        
        with col2:
            data_pagamento = st.date_input("Data de Pagamento *", value=date.today() + timedelta(days=30))
            valor_total = st.number_input("Total a Pagar (R$) *", min_value=0.01, step=0.01, format="%.2f", help="Valor total que o cliente deve pagar")
        
        # Campos específicos por tipo
        if loan_type == 'motoristas':
            st.markdown("#### 🚛 Informações do Motorista")
            col3, col4 = st.columns(2)
            with col3:
                cnh = st.text_input("Número da CNH", placeholder="Ex: 12345678901")
            with col4:
                veiculo = st.text_input("Tipo de Veículo", placeholder="Ex: Carro, Moto, Caminhão")
        
        elif loan_type == 'comerciantes':
            st.markdown("#### 🏪 Informações do Comerciante")
            col3, col4 = st.columns(2)
            with col3:
                cnpj = st.text_input("CNPJ", placeholder="Ex: 12.345.678/0001-90")
            with col4:
                tipo_negocio = st.text_input("Tipo de Negócio", placeholder="Ex: Restaurante, Loja, Serviços")
        
        # Mostrar informações do empréstimo
        if valor_solicitado > 0 and valor_total > 0:
            st.info(f"""
            **Informações do Empréstimo:**
            - Valor Solicitado: R$ {valor_solicitado:,.2f}
            - Total a Pagar: R$ {valor_total:,.2f}
            """)
        
        submitted = st.form_submit_button(f"Cadastrar {type_names[loan_type]}", type="primary")
        
        if submitted:
            if not all([nome_cliente, telefone, valor_solicitado, data_pagamento, valor_total]):
                st.error("Por favor, preencha todos os campos obrigatórios!")
            else:
                # Verificar se já foi processado para evitar duplicação
                form_key = f"loan_form_{loan_type}_{nome_cliente}_{telefone}_{valor_solicitado}_{valor_total}"
                if st.session_state.get(f"processed_{form_key}", False):
                    st.warning("⏳ Processando empréstimo...")
                    return
                
                # Marcar como processado
                st.session_state[f"processed_{form_key}"] = True
                
                # Calcular taxa de juros
                if valor_solicitado > 0:
                    taxa_juros = ((valor_total - valor_solicitado) / valor_solicitado) * 100
                else:
                    taxa_juros = 0.0
                
                loan_data = {
                    'nome_cliente': nome_cliente,
                    'telefone': telefone,
                    'valor_solicitado': valor_solicitado,
                    'data_emprestimo': datetime.now().date(),
                    'data_pagamento': data_pagamento,
                    'valor_com_juros': valor_total,
                    'status': 'pendente',
                    'valor_pago': 0.0,
                    'taxa_juros': taxa_juros,
                    'parcelas': 1,
                    'valor_total_planilha': valor_total
                }
                
                # Adicionar cliente primeiro
                client_id = db.add_client(nome_cliente, telefone, loan_type)
                
                result = db.add_loan(loan_data, loan_type)
                if result is True:
                    st.success("🎉 **Empréstimo cadastrado com sucesso!**")
                    st.info(f"""
                    **📋 Detalhes do Empréstimo:**
                    - 👤 **Cliente:** {nome_cliente}
                    - 📱 **Telefone:** {telefone}
                    - 💰 **Valor Solicitado:** R$ {valor_solicitado:,.2f}
                    - 💵 **Total a Pagar:** R$ {valor_total:,.2f}
                    - 📅 **Data de Pagamento:** {data_pagamento.strftime('%d/%m/%Y')}
                    - 📊 **Taxa de Juros:** {taxa_juros:.1f}%
                    - 🏷️ **Tipo:** {type_names[loan_type]}
                    """)
                    
                    # Limpar flag de processamento
                    if f"processed_{form_key}" in st.session_state:
                        del st.session_state[f"processed_{form_key}"]
                    
                    st.rerun()
                elif result is False:
                    st.warning("⚠️ **Empréstimo já existe!** Um empréstimo idêntico já foi cadastrado anteriormente.")
                    # Limpar flag em caso de duplicação
                    if f"processed_{form_key}" in st.session_state:
                        del st.session_state[f"processed_{form_key}"]
                else:
                    st.error("❌ **Erro ao cadastrar empréstimo!** Tente novamente.")
                    # Limpar flag em caso de erro
                    if f"processed_{form_key}" in st.session_state:
                        del st.session_state[f"processed_{form_key}"]

def clients_management_page():
    st.title("👥 Gestão de Clientes")
    
    # Seção de Novo Empréstimo
    st.markdown("### ➕ Novo Empréstimo")
    
    # Submenu para escolher tipo de empréstimo
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("**Escolha o tipo de empréstimo:**")
        loan_type = st.radio(
            "Tipo de Empréstimo:",
            ["🏦 Clientes Gerais", "🚛 Motorista", "🏪 Comerciante"],
            horizontal=True,
            help="Selecione a categoria do empréstimo"
        )
        
        type_map = {
            "🏦 Clientes Gerais": "emprestimos", 
            "🚛 Motorista": "motoristas", 
            "🏪 Comerciante": "comerciantes"
        }
        
        # Botão para abrir formulário
        if st.button("📝 Cadastrar Novo Empréstimo", type="primary"):
            st.session_state.show_new_loan_form = True
            st.session_state.selected_loan_type = type_map[loan_type]
            st.rerun()
    
    # Mostrar formulário se solicitado
    if st.session_state.get('show_new_loan_form', False):
        st.markdown("---")
        st.markdown("### 📝 Formulário de Novo Empréstimo")
        
        # Botão para voltar
        if st.button("⬅️ Voltar"):
            st.session_state.show_new_loan_form = False
            st.rerun()
        
        # Chamar a função de cadastro de empréstimo
        add_loan_page(st.session_state.get('selected_loan_type', 'emprestimos'))
        return  # Sair da função para mostrar apenas o formulário
    
    st.markdown("---")
    
    # Obter todos os clientes
    clients_df = db.get_all_clients()
    
    if clients_df.empty:
        st.info("📝 Nenhum cliente cadastrado ainda.")
        st.markdown("💡 **Dica:** Clientes são adicionados automaticamente quando você cadastra empréstimos.")
        return
    
    # Seção de filtros melhorada
    st.markdown("### 🔍 Filtros e Busca")
    
    # Primeira linha de filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tipo_filter = st.selectbox(
            "📂 Filtrar por Tipo",
            ["Todos", "Empréstimos", "Motoristas", "Comerciantes"],
            help="Filtra clientes por categoria de empréstimo"
        )
    
    with col2:
        search_name = st.text_input(
            "🔍 Buscar por Nome", 
            placeholder="Digite o nome do cliente...",
            help="Busca por nome do cliente (busca parcial)"
        )
    
    with col3:
        # Filtro por status de atividade
        activity_filter = st.selectbox(
            "⚡ Filtrar por Atividade",
            ["Todos", "Clientes Ativos", "Clientes Inativos"],
            help="Clientes ativos têm empréstimos, inativos não têm"
        )
    
    # Segunda linha de filtros
    col4, col5 = st.columns(2)
    
    with col4:
        # Filtro por período de cadastro
        cadastro_filter = st.selectbox(
            "📅 Período de Cadastro",
            ["Todos", "Última semana", "Último mês", "Últimos 3 meses", "Último ano"],
            help="Filtra por quando o cliente foi cadastrado"
        )
    
    with col5:
        # Ordenação
        sort_by = st.selectbox(
            "📊 Ordenar por",
            ["Nome (A-Z)", "Nome (Z-A)", "Data Cadastro (Mais Recente)", "Data Cadastro (Mais Antigo)"],
            help="Escolha como ordenar a lista de clientes"
        )
    
    # Aplicar filtros
    filtered_df = clients_df.copy()
    
    # Filtro por tipo
    if tipo_filter != "Todos":
        tipo_map = {
            "Empréstimos": "emprestimos",
            "Motoristas": "motoristas",
            "Comerciantes": "comerciantes"
        }
        filtered_df = filtered_df[filtered_df['tipo'] == tipo_map[tipo_filter]]
    
    # Filtro por nome
    if search_name:
        filtered_df = filtered_df[filtered_df['nome'].str.contains(search_name, case=False, na=False)]
    
    # Filtro por atividade
    if activity_filter != "Todos":
        # Obter todos os empréstimos para verificar atividade
        all_loans = db.get_all_loans()
        if not all_loans.empty:
            active_clients = set(all_loans['nome_cliente'].unique())
            if activity_filter == "Clientes Ativos":
                filtered_df = filtered_df[filtered_df['nome'].isin(active_clients)]
            elif activity_filter == "Clientes Inativos":
                filtered_df = filtered_df[~filtered_df['nome'].isin(active_clients)]
    
    # Filtro por período de cadastro
    if cadastro_filter != "Todos":
        try:
            filtered_df['created_at'] = pd.to_datetime(filtered_df['created_at'])
            today = pd.Timestamp.now()
            
            if cadastro_filter == "Última semana":
                start_date = today - pd.Timedelta(days=7)
            elif cadastro_filter == "Último mês":
                start_date = today - pd.Timedelta(days=30)
            elif cadastro_filter == "Últimos 3 meses":
                start_date = today - pd.Timedelta(days=90)
            elif cadastro_filter == "Último ano":
                start_date = today - pd.Timedelta(days=365)
            
            filtered_df = filtered_df[filtered_df['created_at'] >= start_date]
        except:
            pass  # Se houver erro na conversão de data, ignora o filtro
    
    # Ordenação
    if sort_by == "Nome (A-Z)":
        filtered_df = filtered_df.sort_values('nome', ascending=True)
    elif sort_by == "Nome (Z-A)":
        filtered_df = filtered_df.sort_values('nome', ascending=False)
    elif sort_by == "Data Cadastro (Mais Recente)":
        try:
            filtered_df['created_at'] = pd.to_datetime(filtered_df['created_at'])
            filtered_df = filtered_df.sort_values('created_at', ascending=False)
        except:
            pass
    elif sort_by == "Data Cadastro (Mais Antigo)":
        try:
            filtered_df['created_at'] = pd.to_datetime(filtered_df['created_at'])
            filtered_df = filtered_df.sort_values('created_at', ascending=True)
        except:
            pass
    
    # Resetar índice após filtros
    filtered_df = filtered_df.reset_index(drop=True)
    
    # Estatísticas melhoradas
    st.markdown("### 📊 Estatísticas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Clientes", len(filtered_df), delta=f"{len(filtered_df) - len(clients_df)}" if len(filtered_df) != len(clients_df) else None)
    
    with col2:
        emprestimos_count = len(filtered_df[filtered_df['tipo'] == 'emprestimos'])
        st.metric("🏦 Empréstimos", emprestimos_count)
    
    with col3:
        motoristas_count = len(filtered_df[filtered_df['tipo'] == 'motoristas'])
        st.metric("🚛 Motoristas", motoristas_count)
    
    with col4:
        comerciantes_count = len(filtered_df[filtered_df['tipo'] == 'comerciantes'])
        st.metric("🏪 Comerciantes", comerciantes_count)
    
    st.markdown("---")
    
    # Tabela de clientes - versão melhorada e organizada
    if not filtered_df.empty:
        # Seção de Lista de Clientes removida conforme solicitado
        st.info("📋 Lista de Clientes foi removida conforme solicitado.")
        
        # Ações em lote
        st.subheader("🔧 Ações em Lote")
        
        # Inicializar lista de seleção se não existir
        if 'selected_clients' not in st.session_state:
            st.session_state.selected_clients = []
        
        # Verificar se o DataFrame tem a coluna 'Cliente' e não está vazio
        has_valid_data = 'Cliente' in filtered_df.columns and not filtered_df.empty
        
        if not has_valid_data:
            st.warning("⚠️ Nenhum cliente encontrado ou dados inválidos.")
        
        # Seção de seleção múltipla
        st.markdown("#### 📋 Seleção de Clientes")
        
        # Botões para seleção rápida
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✅ Selecionar Todos", key="select_all_clients", disabled=not has_valid_data):
                if has_valid_data:
                    st.session_state.selected_clients = filtered_df['Cliente'].tolist()
                    st.rerun()
        
        with col2:
            if st.button("❌ Desmarcar Todos", key="deselect_all_clients"):
                st.session_state.selected_clients = []
                st.rerun()
        
        with col3:
            if st.button("🔄 Inverter Seleção", key="invert_selection", disabled=not has_valid_data):
                if has_valid_data:
                    current_selected = set(st.session_state.selected_clients)
                    all_clients = set(filtered_df['Cliente'].tolist())
                    st.session_state.selected_clients = list(all_clients - current_selected)
                    st.rerun()
        
        with col4:
            selected_count = len(st.session_state.selected_clients)
            st.metric("Selecionados", selected_count)
        
        # Checkboxes para seleção individual
        st.markdown("**Selecione os clientes:**")
        
        # Verificar novamente se temos dados válidos
        if has_valid_data:
            # Criar colunas para os checkboxes (3 colunas)
            num_clients = len(filtered_df)
            cols_per_row = 3
            num_rows = (num_clients + cols_per_row - 1) // cols_per_row
            
            for row in range(num_rows):
                cols = st.columns(cols_per_row)
                for col_idx in range(cols_per_row):
                    client_idx = row * cols_per_row + col_idx
                    if client_idx < num_clients:
                        with cols[col_idx]:
                            client_name = filtered_df.iloc[client_idx]['Cliente']
                            is_selected = client_name in st.session_state.selected_clients
                            
                            # Checkbox para seleção
                            if st.checkbox(
                                f"✅ {client_name[:20]}{'...' if len(client_name) > 20 else ''}", 
                                value=is_selected,
                                key=f"client_checkbox_{client_idx}"
                            ):
                                if client_name not in st.session_state.selected_clients:
                                    st.session_state.selected_clients.append(client_name)
                            else:
                                if client_name in st.session_state.selected_clients:
                                    st.session_state.selected_clients.remove(client_name)
        else:
            st.info("Nenhum cliente disponível para seleção.")
        
        st.markdown("---")
        
        # Ações em lote para clientes selecionados
        if st.session_state.selected_clients:
            st.markdown("#### ⚡ Ações para Clientes Selecionados")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🗑️ Deletar Selecionados", key="delete_selected_clients", type="primary"):
                    st.session_state.show_delete_confirmation = True
                    st.rerun()
            
            with col2:
                # Exportar apenas clientes selecionados
                if has_valid_data:
                    selected_df = filtered_df[filtered_df['Cliente'].isin(st.session_state.selected_clients)]
                    if not selected_df.empty:
                        csv_selected = selected_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Exportar Selecionados",
                            data=csv_selected,
                            file_name=f"clientes_selecionados_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                            key="export_selected_clients"
                        )
                    else:
                        st.info("Nenhum cliente selecionado para exportar.")
            
            with col3:
                if st.button("📊 Ver Detalhes", key="view_selected_details"):
                    st.session_state.show_selected_details = True
                    st.rerun()
            
            # Confirmação de exclusão
            if st.session_state.get('show_delete_confirmation', False):
                st.markdown("---")
                st.subheader("⚠️ Confirmação de Exclusão")
                
                st.warning("**ATENÇÃO:** Esta ação não pode ser desfeita!")
                st.write(f"**Clientes que serão deletados ({len(st.session_state.selected_clients)}):**")
                
                # Mostrar lista dos clientes selecionados
                for i, client in enumerate(st.session_state.selected_clients[:10]):  # Mostrar apenas os primeiros 10
                    st.write(f"{i+1}. {client}")
                
                if len(st.session_state.selected_clients) > 10:
                    st.write(f"... e mais {len(st.session_state.selected_clients) - 10} clientes")
                
                col_confirm, col_cancel = st.columns(2)
                
                with col_confirm:
                    if st.button("✅ Confirmar Exclusão", key="confirm_delete_clients", type="primary"):
                        deleted_count = 0
                        for client_name in st.session_state.selected_clients:
                            # Buscar o cliente no banco de dados
                            all_clients = db.get_all_clients()
                            client_row = all_clients[all_clients['nome'] == client_name]
                            
                            if not client_row.empty:
                                client_id = client_row.iloc[0]['id']
                                success, message = db.delete_client(client_id)
                                if success:
                                    deleted_count += 1
                        
                        st.success(f"✅ {deleted_count} clientes deletados com sucesso!")
                        st.session_state.selected_clients = []
                        st.session_state.show_delete_confirmation = False
                        st.rerun()
                
                with col_cancel:
                    if st.button("❌ Cancelar", key="cancel_delete_clients"):
                        st.session_state.show_delete_confirmation = False
                        st.rerun()
            
            # Detalhes dos clientes selecionados
            if st.session_state.get('show_selected_details', False):
                st.markdown("---")
                st.subheader("📊 Detalhes dos Clientes Selecionados")
                
                if has_valid_data:
                    selected_df = filtered_df[filtered_df['Cliente'].isin(st.session_state.selected_clients)]
                else:
                    selected_df = pd.DataFrame()  # DataFrame vazio se não há dados
                
                # Estatísticas dos selecionados
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Selecionados", len(selected_df) if not selected_df.empty else 0)
                
                with col2:
                    if not selected_df.empty and 'Empréstimos' in selected_df.columns:
                        total_loans = selected_df['Empréstimos'].sum()
                        st.metric("Total Empréstimos", total_loans)
                    else:
                        st.metric("Total Empréstimos", 0)
                
                with col3:
                    if not selected_df.empty and 'Valor Total' in selected_df.columns:
                        # Extrair valores numéricos dos valores formatados
                        def extract_value(val_str):
                            if val_str == "-":
                                return 0
                            # Remover R$ e vírgulas, converter para float
                            clean_val = val_str.replace("R$ ", "").replace(".", "").replace(",", ".")
                            try:
                                return float(clean_val)
                            except:
                                return 0
                        
                        total_value = selected_df['Valor Total'].apply(extract_value).sum()
                        st.metric("Valor Total", f"R$ {total_value:,.2f}")
                    else:
                        st.metric("Valor Total", "R$ 0,00")
                
                # Tabela detalhada dos selecionados
                if not selected_df.empty:
                    st.dataframe(selected_df, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum cliente selecionado para exibir detalhes.")
                
                if st.button("❌ Fechar Detalhes", key="close_details"):
                    st.session_state.show_selected_details = False
                    st.rerun()
        
        else:
            st.info("👆 Selecione clientes acima para realizar ações em lote")
        
        st.markdown("---")
        
        # Exportar lista completa (todos os clientes filtrados)
        st.markdown("#### 📊 Exportar Dados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Exportar Lista Completa", key="export_all_clients", disabled=not has_valid_data):
                if has_valid_data:
                    csv_all = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Baixar CSV Completo",
                        data=csv_all,
                        file_name=f"clientes_completo_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        key="download_all_clients"
                    )
        
        with col2:
            if st.button("📊 Relatório Estatístico", key="generate_report", disabled=not has_valid_data):
                if has_valid_data:
                    # Gerar relatório estatístico
                    report_data = {
                        'Total de Clientes': [len(filtered_df)],
                        'Clientes com Empréstimos': [len(filtered_df[filtered_df.get('Empréstimos', 0) > 0]) if 'Empréstimos' in filtered_df.columns else 0],
                        'Clientes Ativos': [len(filtered_df[filtered_df.get('Status', '') == 'Ativo']) if 'Status' in filtered_df.columns else 0],
                        'Data do Relatório': [datetime.now().strftime('%d/%m/%Y %H:%M')]
                    }
                    
                    report_df = pd.DataFrame(report_data)
                    csv_report = report_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Baixar Relatório",
                        data=csv_report,
                        file_name=f"relatorio_clientes_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        key="download_report"
                    )
    else:
        st.info("Nenhum cliente encontrado com os filtros aplicados.")

def support_page():
    st.title("🆘 Suporte e Solicitação de Recursos")
    
    st.subheader("Abrir Ticket")
    with st.form("support_form"):
        col1, col2 = st.columns(2)
        with col1:
            titulo = st.text_input("Título do ticket *", placeholder="Ex: Erro ao cadastrar empréstimo")
            tipo = st.selectbox("Tipo de ticket *", ["Problema", "Recurso (nova funcionalidade)"])
        with col2:
            imagem = st.file_uploader("Anexar imagem (opcional)", type=["png","jpg","jpeg"])
        descricao = st.text_area("Descrição detalhada *", height=150, placeholder="Explique o problema ou descreva a melhoria desejada")
        submitted = st.form_submit_button("Enviar Ticket", type="primary")
        if submitted:
            if not all([titulo, descricao, tipo]):
                st.error("Preencha os campos obrigatórios.")
            else:
                # salvar imagem em ./uploads
                saved_path = ""
                if imagem is not None:
                    import os
                    uploads_dir = "uploads"
                    os.makedirs(uploads_dir, exist_ok=True)
                    saved_path = os.path.join(uploads_dir, f"{int(datetime.now().timestamp())}_{imagem.name}")
                    with open(saved_path, 'wb') as f:
                        f.write(imagem.getbuffer())
                ticket_id = db.create_ticket(
                    titulo=titulo,
                    descricao=descricao,
                    tipo="problema" if tipo.startswith("Problema") else "recurso",
                    imagem=saved_path,
                    criado_por=st.session_state.get('username','anon')
                )
                st.success(f"Ticket #{ticket_id} criado com sucesso!")
                st.rerun()

    st.markdown("---")
    st.subheader("Meus Tickets")
    my_df = db.list_tickets(st.session_state.get('username'))
    if my_df.empty:
        st.info("Você ainda não possui tickets.")
    else:
        def color_status(val):
            if val == 'aberto':
                return 'background-color: #fff3cd; color: #856404'
            if val == 'pendente':
                return 'background-color: #cce5ff; color: #004085'
            if val == 'resolvido':
                return 'background-color: #d4edda; color: #155724'
            return ''
        show_df = my_df.copy()
        show_df = show_df[['id','titulo','tipo','status','created_at','updated_at','resolved_at']]
        show_df = show_df.rename(columns={'id':'ID','titulo':'Título','tipo':'Tipo','status':'Status','created_at':'Criado em','updated_at':'Atualizado em','resolved_at':'Resolvido em'})
        st.dataframe(show_df.style.map(color_status, subset=['Status']), use_container_width=True)

    if st.session_state.get('user_role') == 'admin':
        st.markdown("---")
        st.subheader("📋 Todos os Tickets (Admin)")
        all_df = db.list_tickets()
        if all_df.empty:
            st.info("Sem tickets até o momento.")
        else:
            all_df = all_df.sort_values('created_at', ascending=False)
            for _, row in all_df.iterrows():
                with st.expander(f"#{int(row['id'])} - {row['titulo']} ({row['status']})", expanded=False):
                    st.write(f"Tipo: {row['tipo']}")
                    st.write(f"Criado por: {row['criado_por']} em {row['created_at']}")
                    st.write(f"Descrição:\n{row['descricao']}")
                    if isinstance(row['imagem'], str) and len(row['imagem'])>0:
                        st.image(row['imagem'], caption="Anexo")
                    cols = st.columns(3)
                    with cols[0]:
                        if st.button("Marcar como Resolvido", key=f"resolve_{int(row['id'])}"):
                            if db.resolve_ticket(int(row['id']), st.session_state.get('username')):
                                # enviar email
                                try:
                                    email_service.send_reset_email("lucaseuro33@gmail.com", row['criado_por'], f"Ticket #{int(row['id'])} resolvido: {row['titulo']}")
                                except Exception:
                                    pass
                                st.success("Ticket resolvido e notificação enviada.")
                                st.rerun()
                    with cols[1]:
                        st.write(f"Atualizado em: {row['updated_at']}")
                    with cols[2]:
                        st.write(f"Resolvido por: {row.get('resolved_by','')}")

def admin_permissions_page():
    st.title("👥 Gerenciamento de Permissões")
    
    # Tabs para diferentes funcionalidades
    tab1, tab2, tab3 = st.tabs(["🔔 Solicitações de Admin", "👤 Gerenciar Usuários", "➕ Criar Usuário"])
    
    with tab1:
        st.subheader("🔔 Solicitações de Acesso Administrativo")
        
        admin_requests = db.get_admin_requests()
        
        if not admin_requests:
            st.info("Nenhuma solicitação de admin pendente.")
        else:
            st.warning(f"⚠️ {len(admin_requests)} solicitação(ões) de admin pendente(s)!")
            
            for username, request_data in admin_requests.items():
                with st.expander(f"📋 Solicitação de {username}", expanded=True):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Usuário:** {username}")
                        st.write(f"**Data da Solicitação:** {request_data['requested_at'][:19]}")
                        st.write(f"**Mensagem:** {request_data['message']}")
                    
                    with col2:
                        col_approve, col_reject = st.columns(2)
                        
                        with col_approve:
                            if st.button("✅ Aprovar", key=f"approve_{username}"):
                                success, message = db.approve_admin_request(username, st.session_state.username)
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                        
                        with col_reject:
                            if st.button("❌ Rejeitar", key=f"reject_{username}"):
                                success, message = db.reject_admin_request(username, st.session_state.username)
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
    
    with tab2:
        st.subheader("👤 Gerenciar Usuários Existentes")
        
        all_users = db.get_all_users()
        
        if not all_users:
            st.info("Nenhum usuário encontrado.")
        else:
            # Filtrar usuários (não mostrar o próprio admin)
            filtered_users = {k: v for k, v in all_users.items() if k != st.session_state.username}
            
            if not filtered_users:
                st.info("Nenhum outro usuário para gerenciar.")
            else:
                for username, user_data in filtered_users.items():
                    with st.expander(f"👤 {username} ({user_data['role']})", expanded=False):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Role Atual:** {user_data['role']}")
                            st.write(f"**Criado em:** {user_data.get('created_at', 'N/A')[:19]}")
                            if 'approved_at' in user_data:
                                st.write(f"**Aprovado em:** {user_data['approved_at'][:19]}")
                                st.write(f"**Aprovado por:** {user_data.get('approved_by', 'N/A')}")
                        
                        with col2:
                            if user_data['role'] == 'admin':
                                if st.button("⬇️ Rebaixar para User", key=f"demote_{username}"):
                                    success, message = db.update_user_role(username, 'user', st.session_state.username)
                                    if success:
                                        st.success(message)
                                        st.rerun()
                                    else:
                                        st.error(message)
                            else:
                                if st.button("⬆️ Promover para Admin", key=f"promote_{username}"):
                                    success, message = db.update_user_role(username, 'admin', st.session_state.username)
                                    if success:
                                        st.success(message)
                                        st.rerun()
                                    else:
                                        st.error(message)
    
    with tab3:
        st.subheader("➕ Criar Novo Usuário")
        
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Nome de usuário")
                new_password = st.text_input("Senha", type="password")
            
            with col2:
                confirm_password = st.text_input("Confirmar senha", type="password")
                user_role = st.selectbox("Tipo de usuário", ["user", "admin"])
            
            submit_button = st.form_submit_button("Criar Usuário")
            
            if submit_button:
                if not all([new_username, new_password, confirm_password]):
                    st.error("Por favor, preencha todos os campos!")
                elif new_password != confirm_password:
                    st.error("As senhas não coincidem!")
                elif len(new_password) < 6:
                    st.error("A senha deve ter pelo menos 6 caracteres!")
                elif new_username.endswith('.admin'):
                    st.error("❌ Não é possível criar usuários com .admin diretamente. Use o sistema de solicitações.")
                elif db.create_user(new_username, new_password, user_role):
                    st.success(f"Usuário {new_username} criado com sucesso como {user_role}!")
                else:
                    st.error("Usuário já existe!")
        
        st.markdown("---")
        st.info("""
        **💡 Dicas:**
        - Usuários com `.admin` no nome criam automaticamente uma solicitação
        - Apenas administradores podem aprovar/rejeitar solicitações
        - Use com cuidado ao promover usuários para admin
        """)

def data_import_page():
    st.title("📊 Importação de Dados - Planilhas Excel")
    
    st.markdown("""
    ### 📋 Formato Esperado da Planilha
    
    Sua planilha deve ter as seguintes características:
    
    **📁 Estrutura:**
    - Uma aba para cada mês (janeiro, fevereiro, março, etc.)
    - Cada aba deve conter as colunas listadas abaixo
    
    **📊 Colunas Obrigatórias:**
    - `Cliente` - Nome completo do cliente
    - `Valor Emprestado` - Valor solicitado pelo cliente
    - `Valor a Receber` - Valor total com juros
    - `Data de Pagamento` - Data de vencimento
    - `Status` - Pago, Pendente ou Atrasado
    
    **⚠️ Observações:**
    - Os nomes das abas devem ser exatamente: janeiro, fevereiro, março, etc.
    - Os status válidos são: pago, pendente, atrasado
    - Valores devem estar em formato numérico
    - Datas devem estar em formato brasileiro (DD/MM/AAAA)
    """)
    
    st.markdown("---")
    
    # Upload de arquivo
    st.subheader("📤 Upload da Planilha")
    
    # Opção para limpar dados existentes
    col1, col2 = create_responsive_columns(2)
    
    with col1:
        st.markdown("**📋 Opções de Importação:**")
        clear_existing = st.checkbox(
            "🗑️ Limpar dados existentes antes da importação",
            help="Remove todos os empréstimos existentes antes de importar os novos dados"
        )
    
    with col2:
        if clear_existing:
            st.warning("⚠️ **ATENÇÃO:** Todos os empréstimos existentes serão removidos!")
    
    uploaded_file = st.file_uploader(
        "Selecione sua planilha Excel",
        type=['xlsx', 'xls'],
        help="Arquivo Excel com abas de janeiro a dezembro"
    )
    
    if uploaded_file is not None:
        # Mostrar informações do arquivo
        st.info(f"📁 Arquivo selecionado: **{uploaded_file.name}**")
        
        # Processar arquivo
        with st.spinner("Processando planilha..."):
            result = process_excel_data(uploaded_file)
        
        if result['success']:
            # Mostrar estatísticas do processamento
            st.success("✅ Planilha processada com sucesso!")
            
            stats = result['stats']
            cols = create_responsive_columns(4)
            
            with cols[0]:
                st.metric("Total de Empréstimos", stats['total_loans'])
            
            with cols[1]:
                st.metric("Valor Total", f"R$ {stats['total_value']:,.2f}")
            
            with cols[2]:
                st.metric("Meses Processados", stats['months_processed'])
            
            with cols[3]:
                st.metric("Erros Encontrados", len(stats['errors']))
            
            # Mostrar erros se houver
            if stats['errors']:
                st.warning("⚠️ Alguns erros foram encontrados durante o processamento:")
                with st.expander("Ver erros detalhados", expanded=True):
                    for error in stats['errors']:
                        if error.startswith("DEBUG"):
                            st.info(f"🔍 {error}")
                        else:
                            st.error(f"• {error}")
                
                # Mostrar comparação com valores esperados
                st.markdown("---")
                st.subheader("📊 Comparação com Valores Esperados")
                
                col1, col2 = create_responsive_columns(2)
                
                with col1:
                    st.markdown("**📈 Valores Processados:**")
                    st.metric("Total Empréstimos", stats['total_loans'])
                    st.metric("Valor Total Emprestado", f"R$ {stats['total_value']:,.2f}")
                    st.metric("Meses Processados", stats['months_processed'])
                
                with col2:
                    st.markdown("**🎯 Valores Esperados (Planilha):**")
                    st.info("💡 **Para comparar:**")
                    st.markdown("- Total na planilha: **R$ 271.056,00**")
                    st.markdown("- Empréstimos esperados: **~233**")
                    st.markdown("- Diferença atual: **R$ -184.005,80**")
                    
                    if stats['total_value'] < 271056:
                        st.error(f"⚠️ **Faltam R$ {271056 - stats['total_value']:,.2f}**")
                        st.warning("🔍 **Possíveis causas:**")
                        st.markdown("- Alguns meses não foram processados")
                        st.markdown("- Linhas com dados inválidos foram puladas")
                        st.markdown("- Nomes das abas não reconhecidos")
                
                # Dicas para corrigir erros
                st.info("""
                **💡 Dicas para corrigir erros:**
                - Verifique se os nomes das colunas estão corretos
                - Confirme se os valores estão em formato numérico
                - Verifique se as datas estão no formato DD/MM/AAAA
                - Certifique-se de que os status são: pago, pendente ou atrasado
                """)
                
                # Diagnóstico específico para "nenhum dado válido"
                if stats['total_loans'] == 0 and stats['months_processed'] == 0:
                    st.markdown("---")
                    st.subheader("🔍 Diagnóstico: Nenhum Dado Válido")
                    
                    cols = create_responsive_columns(2)
                    
                    with cols[0]:
                        st.markdown("""
                        **📋 Possíveis Causas:**
                        - Abas não têm os nomes corretos dos meses
                        - Colunas não têm os nomes esperados
                        - Dados estão vazios ou em formato incorreto
                        - Planilha está vazia ou corrompida
                        """)
                    
                    with cols[1]:
                        st.markdown("""
                        **🔧 Soluções:**
                        - Use o botão "Baixar Exemplo" como modelo
                        - Verifique os nomes das abas (janeiro, fevereiro, etc.)
                        - Confirme os nomes das colunas
                        - Teste com dados simples primeiro
                        """)
            
            # Preview dos dados
            if result['data']:
                st.markdown("---")
                st.subheader("👀 Preview dos Dados")
                
                # Criar DataFrame para preview
                preview_df = pd.DataFrame(result['data'])
                
                # Formatar para exibição - usar campos que existem
                available_columns = ['nome_cliente', 'valor_solicitado', 'data_pagamento', 'taxa_juros', 'parcelas', 'status']
                display_columns = [col for col in available_columns if col in preview_df.columns]
                
                display_df = preview_df[display_columns].copy()
                
                # Formatar valores monetários se existirem
                if 'valor_solicitado' in display_df.columns:
                    display_df['valor_solicitado'] = display_df['valor_solicitado'].apply(lambda x: f"R$ {x:,.2f}")
                
                # Usar valor total da planilha se disponível, senão calcular
                if 'valor_total_planilha' in preview_df.columns:
                    display_df['valor_total'] = preview_df['valor_total_planilha'].apply(lambda x: f"R$ {x:,.2f}")
                elif 'valor_solicitado' in preview_df.columns and 'taxa_juros' in preview_df.columns:
                    valor_solicitado = preview_df['valor_solicitado']
                    taxa_juros = preview_df['taxa_juros']
                    valor_total = valor_solicitado * (1 + taxa_juros / 100)
                    display_df['valor_total'] = valor_total.apply(lambda x: f"R$ {x:,.2f}")
                
                # Formatar taxa de juros se existir
                if 'taxa_juros' in display_df.columns:
                    display_df['taxa_juros'] = display_df['taxa_juros'].apply(lambda x: f"{x:.1f}%")
                
                # Converter data_pagamento para string se necessário
                if pd.api.types.is_datetime64_any_dtype(display_df['data_pagamento']):
                    display_df['data_pagamento'] = display_df['data_pagamento'].dt.strftime('%d/%m/%Y')
                else:
                    # Se já for string ou outro tipo, manter como está
                    display_df['data_pagamento'] = display_df['data_pagamento'].astype(str)
                
                # Mapear nomes das colunas para exibição
                column_mapping = {
                    'nome_cliente': 'Cliente',
                    'valor_solicitado': 'Valor Emprestado',
                    'valor_total': 'Valor Total',
                    'taxa_juros': 'Taxa de Juros',
                    'parcelas': 'Parcelas',
                    'data_pagamento': 'Data Pagamento',
                    'status': 'Status'
                }
                
                # Renomear colunas que existem
                display_df = display_df.rename(columns={col: column_mapping[col] for col in display_df.columns if col in column_mapping})
                
                # Mostrar apenas as primeiras 10 linhas
                st.dataframe(display_df.head(10), use_container_width=True)
                
                if len(display_df) > 10:
                    st.info(f"Mostrando 10 de {len(display_df)} empréstimos. Todos serão importados.")
                
                # Botões de ação
                st.markdown("---")
                st.subheader("🚀 Importar Dados")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Confirmar Importação", type="primary", key="confirm_import"):
                        with st.spinner("Importando dados..."):
                            # Limpar dados existentes se solicitado
                            if clear_existing:
                                st.info("🗑️ Limpando dados existentes...")
                                for loan_type in ['emprestimos', 'motoristas', 'comerciantes']:
                                    df = db.get_loans(loan_type)
                                    if not df.empty:
                                        empty_df = pd.DataFrame(columns=df.columns)
                                        file_map = {
                                            'emprestimos': 'loans.csv',
                                            'motoristas': 'motoristas.csv', 
                                            'comerciantes': 'comerciantes.csv'
                                        }
                                        empty_df.to_csv(file_map[loan_type], index=False)
                                st.success("✅ Dados existentes removidos!")
                            
                            import_result = import_loans_data(result['data'])
                        
                        if import_result['imported'] > 0:
                            st.success(f"🎉 Importação concluída com sucesso!")
                            st.success(f"✅ {import_result['imported']} empréstimos importados")
                            st.success(f"👥 {import_result['clients_added']} clientes adicionados")
                            
                            if import_result['errors']:
                                st.warning("⚠️ Alguns erros durante a importação:")
                                for error in import_result['errors']:
                                    st.error(f"• {error}")
                        else:
                            st.error("❌ Nenhum empréstimo foi importado.")
                            
                            # Mostrar informações de debug
                            if import_result.get('debug_info'):
                                st.markdown("---")
                                st.subheader("🔍 Informações de Debug")
                                with st.expander("Ver logs de debug", expanded=True):
                                    for debug_msg in import_result['debug_info']:
                                        st.info(f"ℹ️ {debug_msg}")
                            
                            # Mostrar erros se houver
                            if import_result.get('errors'):
                                st.markdown("---")
                                st.subheader("❌ Erros Durante a Importação")
                                for error in import_result['errors']:
                                    st.error(f"• {error}")
                
                with col2:
                    if st.button("❌ Cancelar Importação", key="cancel_import"):
                        st.info("Importação cancelada.")
            
            else:
                st.warning("⚠️ Nenhum dado válido foi encontrado na planilha.")
        
        else:
            st.error(f"❌ Erro ao processar planilha: {result['error']}")
            
            # Seção de diagnóstico
            st.markdown("---")
            st.subheader("🔧 Diagnóstico de Problemas")
            
            cols = create_responsive_columns(2)
            
            with cols[0]:
                st.markdown("""
                **📋 Checklist da Planilha:**
                - ✅ Arquivo é Excel (.xlsx ou .xls)
                - ✅ Tem abas com nomes dos meses (janeiro, fevereiro, etc.)
                - ✅ Cada aba tem as colunas necessárias
                - ✅ Dados não estão vazios
                """)
            
            with cols[1]:
                st.markdown("""
                **🔍 Possíveis Soluções:**
                - Verifique se o arquivo não está corrompido
                - Tente salvar novamente no Excel
                - Confirme se as abas têm os nomes corretos
                - Verifique se não há caracteres especiais
                """)
            
            # Tentar diagnóstico adicional
            try:
                st.markdown("---")
                st.subheader("🔍 Análise do Arquivo")
                
                # Tentar ler apenas os nomes das abas
                try:
                    import io
                    uploaded_file.seek(0)  # Resetar posição do arquivo
                    
                    # Tentar ler com diferentes engines
                    engines_to_test = ['openpyxl']
                    
                    # Tentar xlrd apenas se disponível
                    try:
                        import xlrd
                        engines_to_test.append('xlrd')
                    except ImportError:
                        st.info("ℹ️ xlrd não disponível, testando apenas com openpyxl")
                    
                    for engine in engines_to_test:
                        try:
                            excel_file = pd.ExcelFile(uploaded_file, engine=engine)
                            sheet_names = excel_file.sheet_names
                            
                            st.success(f"✅ Arquivo lido com sucesso usando engine: {engine}")
                            st.write(f"**Abas encontradas:** {', '.join(sheet_names)}")
                            
                            # Verificar quais são meses válidos - lista expandida
                            month_names = [
                                'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 
                                'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro',
                                'janeiro 01', 'janeiro 1', 'fevereiro 02', 'fevereiro 2',
                                'março 03', 'março 3', 'abril 04', 'abril 4',
                                'maio 05', 'maio 5', 'junho 06', 'junho 6',
                                'julho 07', 'julho 7', 'agosto 08', 'agosto 8',
                                'setembro 09', 'setembro 9', 'outubro 10',
                                'novembro 11', 'dezembro 12',
                                'JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO',
                                'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO',
                                'JANEIRO 01', 'FEVEREIRO 02', 'MARÇO 03', 'ABRIL 04',
                                'MAIO 05', 'JUNHO 06', 'JULHO 07', 'AGOSTO 08',
                                'SETEMBRO 09', 'OUTUBRO 10', 'NOVEMBRO 11', 'DEZEMBRO 12'
                            ]
                            
                            valid_months = [name for name in sheet_names if name.strip() in month_names]
                            invalid_months = [name for name in sheet_names if name.strip() not in month_names]
                            
                            if valid_months:
                                st.success(f"✅ Meses válidos encontrados: {', '.join(valid_months)}")
                            
                            if invalid_months:
                                st.warning(f"⚠️ Abas que não são meses válidos: {', '.join(invalid_months)}")
                            
                            break
                            
                        except Exception as e:
                            st.warning(f"❌ Erro com engine {engine}: {str(e)}")
                            continue
                    
                    uploaded_file.seek(0)  # Resetar posição novamente
                    
                except Exception as e:
                    st.error(f"❌ Não foi possível analisar o arquivo: {str(e)}")
                    
            except Exception as e:
                st.error(f"❌ Erro no diagnóstico: {str(e)}")
    
    # Seção de exemplo
    st.markdown("---")
    st.subheader("📝 Exemplo de Estrutura")
    
    # Criar exemplo de dados
    example_data = {
        'Cliente': ['João Silva', 'Maria Santos', 'Pedro Costa'],
        'Valor Emprestado': [1000.00, 2500.00, 800.00],
        'Valor a Receber': [1200.00, 3000.00, 960.00],
        'Data de Pagamento': ['15/01/2024', '20/01/2024', '25/01/2024'],
        'Status': ['pendente', 'pago', 'atrasado']
    }
    
    example_df = pd.DataFrame(example_data)
    
    st.markdown("**Exemplo da aba 'Janeiro':**")
    st.dataframe(example_df, use_container_width=True)
    
    # Botão para baixar exemplo
    if st.button("📥 Baixar Planilha de Exemplo", key="download_example"):
        try:
            # Criar arquivo Excel com múltiplas abas
            from io import BytesIO
            
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Criar exemplo para janeiro
                jan_data = {
                    'Cliente': ['João Silva', 'Maria Santos', 'Pedro Costa'],
                    'Valor Emprestado': [1000.00, 2500.00, 800.00],
                    'Valor a Receber': [1200.00, 3000.00, 960.00],
                    'Data de Pagamento': ['15/01/2024', '20/01/2024', '25/01/2024'],
                    'Status': ['pendente', 'pago', 'atrasado']
                }
                jan_df = pd.DataFrame(jan_data)
                jan_df.to_excel(writer, sheet_name='janeiro', index=False)
                
                # Criar exemplo para fevereiro
                feb_data = {
                    'Cliente': ['Ana Lima', 'Carlos Oliveira'],
                    'Valor Emprestado': [1500.00, 3200.00],
                    'Valor a Receber': [1800.00, 3840.00],
                    'Data de Pagamento': ['10/02/2024', '15/02/2024'],
                    'Status': ['pendente', 'pago']
                }
                feb_df = pd.DataFrame(feb_data)
                feb_df.to_excel(writer, sheet_name='fevereiro', index=False)
            
            output.seek(0)
            
            st.download_button(
                label="📥 Baixar Arquivo Excel de Exemplo",
                data=output.getvalue(),
                file_name="exemplo_planilha_emprestimos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Baixe este arquivo para usar como modelo da sua planilha"
            )
            
        except Exception as e:
            st.error(f"Erro ao criar arquivo de exemplo: {str(e)}")
    
    # Dicas adicionais
    st.markdown("---")
    st.subheader("💡 Dicas Importantes")
    
    cols = create_responsive_columns(2)
    
    with cols[0]:
        st.info("""
        **✅ O que funciona:**
        - Abas com nomes em português
        - Valores em formato numérico
        - Datas em formato brasileiro
        - Status: pago, pendente, atrasado
        """)
    
    with cols[1]:
        st.warning("""
        **⚠️ Cuidados:**
        - Nomes das abas devem ser exatos
        - Colunas devem ter os nomes corretos
        - Valores não podem estar vazios
        - Status deve estar em minúsculas
        """)

def main():
    # Verificar se usuário está logado
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # Verificar se user_role está definido
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    
    if not st.session_state.logged_in:
        # Verificar se está na página de reset de senha
        if st.session_state.get('show_reset_password', False):
            reset_password_page()
        elif st.session_state.get('show_forgot_password', False):
            forgot_password_page()
        else:
            # Sidebar para login/cadastro
            st.sidebar.title("🔐 Autenticação")
            page = st.sidebar.radio("Escolha uma opção:", ["Login", "Cadastro"])
            
            if page == "Login":
                login_page()
            else:
                register_page()
    else:
        # Sidebar principal
        st.sidebar.title(f"👋 Olá, {st.session_state.username}")
        st.sidebar.markdown(f"**Função:** {st.session_state.user_role or 'N/A'}")
        
        if st.sidebar.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.sidebar.markdown("---")
        
        # Navegação baseada no tipo de usuário
        if st.session_state.get('user_role') == "admin":
            pages = [
                "📊 Dashboard Admin", 
                "🏦 Empréstimos Gerais", 
                "🚛 Motoristas", 
                "🏪 Comerciantes",
                "👥 Gestão de Clientes",
                "📊 Importar Dados",
                "🆘 Suporte",
                "👥 Gerenciar Permissões"
            ]
        else:
            pages = [
                "📋 Meus Empréstimos", 
                "🏦 Empréstimos Gerais", 
                "🚛 Motoristas", 
                "🏪 Comerciantes",
                "🆘 Suporte"
            ]
        
        selected_page = st.sidebar.radio("Navegação", pages)
        
        # Renderizar página selecionada
        if selected_page == "📊 Dashboard Admin" and st.session_state.get('user_role') == "admin":
            admin_dashboard_page()
        elif selected_page == "📋 Meus Empréstimos" and st.session_state.get('user_role') != "admin":
            user_dashboard_page()
        elif selected_page == "🏦 Empréstimos Gerais":
            loans_detail_page('emprestimos')
        elif selected_page == "🚛 Motoristas":
            loans_detail_page('motoristas')
        elif selected_page == "🏪 Comerciantes":
            loans_detail_page('comerciantes')
        elif selected_page == "👥 Gestão de Clientes" and st.session_state.get('user_role') == "admin":
            clients_management_page()
        elif selected_page == "📊 Importar Dados" and st.session_state.get('user_role') == "admin":
            data_import_page()
        elif selected_page == "🆘 Suporte":
            support_page()
        elif selected_page == "👥 Gerenciar Permissões" and st.session_state.get('user_role') == "admin":
            admin_permissions_page()

if __name__ == "__main__":
    main()
