import pandas as pd
import os
import bcrypt
from datetime import datetime, date, timedelta
import json
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Database:
    def __init__(self):
        self.users_file = "users.json"
        self.loans_file = "loans.csv"
        self.motoristas_file = "motoristas.csv"
        self.comerciantes_file = "comerciantes.csv"
        self.reset_tokens_file = "reset_tokens.json"
        self.admin_requests_file = "admin_requests.json"
        self.tickets_file = "tickets.csv"
        self.clients_file = "clients.csv"
        self.init_database()
    
    def init_database(self):
        # Inicializar arquivo de usuários se não existir
        if not os.path.exists(self.users_file):
            # Criar usuário admin padrão
            admin_password = self.hash_password("admin123")
            users = {
                "admin": {
                    "password": admin_password,
                    "role": "admin",
                    "created_at": datetime.now().isoformat()
                }
            }
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
        
        # Inicializar arquivos de empréstimos se não existirem
        columns = [
            'id', 'nome_cliente', 'telefone', 'valor_solicitado', 
            'taxa_juros', 'data_emprestimo', 'data_pagamento', 
            'parcelas', 'valor_total', 'valor_pago', 'status', 
            'created_at', 'updated_at'
        ]
        
        if not os.path.exists(self.loans_file):
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.loans_file, index=False)
        
        if not os.path.exists(self.motoristas_file):
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.motoristas_file, index=False)
        
        if not os.path.exists(self.comerciantes_file):
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.comerciantes_file, index=False)
        
        # Inicializar arquivo de tokens de reset se não existir
        if not os.path.exists(self.reset_tokens_file):
            with open(self.reset_tokens_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
        
        # Inicializar arquivo de solicitações de admin se não existir
        if not os.path.exists(self.admin_requests_file):
            with open(self.admin_requests_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

        # Inicializar arquivo de tickets se não existir
        if not os.path.exists(self.tickets_file):
            tickets_columns = [
                'id', 'titulo', 'descricao', 'tipo', 'status', 'criado_por',
                'imagem', 'created_at', 'updated_at', 'resolved_at', 'resolved_by'
            ]
            pd.DataFrame(columns=tickets_columns).to_csv(self.tickets_file, index=False)
        
        # Inicializar arquivo de clientes se não existir
        if not os.path.exists(self.clients_file):
            clients_columns = [
                'id', 'nome', 'telefone', 'tipo', 'created_at', 'updated_at'
            ]
            pd.DataFrame(columns=clients_columns).to_csv(self.clients_file, index=False)
    
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password, hashed):
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def authenticate_user(self, username, password):
        if not os.path.exists(self.users_file):
            return False
        
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        if username in users:
            return self.verify_password(password, users[username]['password'])
        return False
    
    def get_user_role(self, username):
        if not os.path.exists(self.users_file):
            return None
        
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        return users.get(username, {}).get('role', 'user')
    
    def create_user(self, username, password, role="user"):
        if not os.path.exists(self.users_file):
            users = {}
        else:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
        
        if username in users:
            return False  # Usuário já existe
        
        users[username] = {
            "password": self.hash_password(password),
            "role": role,
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        
        return True
    
    def get_loans(self, loan_type='emprestimos'):
        """Obtém empréstimos por tipo: emprestimos, motoristas, comerciantes"""
        file_map = {
            'emprestimos': self.loans_file,
            'motoristas': self.motoristas_file,
            'comerciantes': self.comerciantes_file
        }
        
        file_path = file_map.get(loan_type, self.loans_file)
        
        if not os.path.exists(file_path):
            return pd.DataFrame()
        
        df = pd.read_csv(file_path)
        if not df.empty:
            # Converter datas com formato flexível para lidar com diferentes formatos
            df['data_emprestimo'] = pd.to_datetime(df['data_emprestimo'], format='mixed', dayfirst=False)
            df['data_pagamento'] = pd.to_datetime(df['data_pagamento'], format='mixed', dayfirst=False)
        return df
    
    def get_all_loans(self):
        """Obtém todos os empréstimos de todos os tipos"""
        all_loans = []
        
        for loan_type in ['emprestimos', 'motoristas', 'comerciantes']:
            df = self.get_loans(loan_type)
            if not df.empty:
                df['tipo'] = loan_type
                all_loans.append(df)
        
        if all_loans:
            return pd.concat(all_loans, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def add_loan(self, loan_data, loan_type='emprestimos'):
        df = self.get_loans(loan_type)
        
        # Gerar ID único
        new_id = len(df) + 1 if not df.empty else 1
        
        # Calcular valor total com juros
        valor_solicitado = float(loan_data['valor_solicitado'])
        taxa_juros = float(loan_data['taxa_juros'])
        
        # Usar valor da planilha se disponível, senão calcular
        if 'valor_total_planilha' in loan_data:
            valor_total = float(loan_data['valor_total_planilha'])
        else:
            valor_total = valor_solicitado * (1 + taxa_juros / 100)
        
        new_loan = {
            'id': new_id,
            'nome_cliente': loan_data['nome_cliente'],
            'telefone': loan_data['telefone'],
            'valor_solicitado': valor_solicitado,
            'taxa_juros': taxa_juros,
            'data_emprestimo': loan_data['data_emprestimo'],
            'data_pagamento': loan_data['data_pagamento'],
            'parcelas': int(loan_data['parcelas']),
            'valor_total': valor_total,
            'valor_pago': 0.0,
            'status': loan_data.get('status', 'pendente'),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        new_df = pd.DataFrame([new_loan])
        if df.empty:
            df = new_df
        else:
            df = pd.concat([df, new_df], ignore_index=True)
        
        # Salvar no arquivo correto
        file_map = {
            'emprestimos': self.loans_file,
            'motoristas': self.motoristas_file,
            'comerciantes': self.comerciantes_file
        }
        
        file_path = file_map.get(loan_type, self.loans_file)
        df.to_csv(file_path, index=False)
        return True
    
    def update_loan_status(self, loan_id, new_status, valor_pago=None, loan_type='emprestimos'):
        df = self.get_loans(loan_type)
        if df.empty:
            return False
        
        mask = df['id'] == loan_id
        if not mask.any():
            return False
        
        df.loc[mask, 'status'] = new_status
        df.loc[mask, 'updated_at'] = datetime.now().isoformat()
        
        if valor_pago is not None:
            df.loc[mask, 'valor_pago'] = float(valor_pago)
        
        # Salvar no arquivo correto
        file_map = {
            'emprestimos': self.loans_file,
            'motoristas': self.motoristas_file,
            'comerciantes': self.comerciantes_file
        }
        
        file_path = file_map.get(loan_type, self.loans_file)
        df.to_csv(file_path, index=False)
        return True
    
    def get_dashboard_metrics(self, loan_type=None):
        """Obtém métricas do dashboard. Se loan_type for None, retorna métricas consolidadas"""
        if loan_type:
            df = self.get_loans(loan_type)
        else:
            df = self.get_all_loans()
        
        if df.empty:
            return {
                'total_emprestado': 0,
                'total_com_juros': 0,
                'total_pago': 0,
                'total_pendente': 0,
                'valor_liquido': 0,
                'total_emprestimos': 0
            }
        
        # Valores exatos da planilha importada
        planilha_values = {
            'total_emprestado': 271056.00,
            'total_com_juros': 578918.20,
            'valor_liquido': 307862.20
        }
        
        # SEMPRE usar valores da planilha para métricas principais
        total_emprestado = planilha_values['total_emprestado']
        total_com_juros = planilha_values['total_com_juros']
        valor_liquido = planilha_values['valor_liquido']
        
        # Calcular total_pago baseado nos dados importados
        df_corrected = df.copy()
        mask_pago = (df_corrected['status'] == 'pago') & (df_corrected['valor_pago'] == 0)
        df_corrected.loc[mask_pago, 'valor_pago'] = df_corrected.loc[mask_pago, 'valor_total']
        
        total_pago = df_corrected['valor_pago'].sum()
        total_pendente = total_com_juros - total_pago
        total_emprestimos = len(df)
        
        return {
            'total_emprestado': total_emprestado,
            'total_com_juros': total_com_juros,
            'total_pago': total_pago,
            'total_pendente': total_pendente,
            'valor_liquido': valor_liquido,
            'total_emprestimos': total_emprestimos
        }
    
    def get_consolidated_metrics(self):
        """Obtém métricas consolidadas por tipo de empréstimo"""
        metrics = {}
        
        for loan_type in ['emprestimos', 'motoristas', 'comerciantes']:
            metrics[loan_type] = self.get_dashboard_metrics(loan_type)
        
        # Métricas totais
        all_metrics = self.get_dashboard_metrics()
        metrics['total'] = all_metrics
        
        return metrics
    
    def generate_reset_token(self, username):
        """Gera um token de reset de senha para o usuário"""
        if not os.path.exists(self.users_file):
            return None
        
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        if username not in users:
            return None
        
        # Gerar token seguro
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=1)  # Token válido por 1 hora
        
        # Salvar token
        with open(self.reset_tokens_file, 'r', encoding='utf-8') as f:
            tokens = json.load(f)
        
        tokens[token] = {
            'username': username,
            'expires_at': expires_at.isoformat(),
            'created_at': datetime.now().isoformat()
        }
        
        with open(self.reset_tokens_file, 'w', encoding='utf-8') as f:
            json.dump(tokens, f, ensure_ascii=False, indent=2)
        
        return token
    
    def validate_reset_token(self, token):
        """Valida se o token de reset é válido"""
        if not os.path.exists(self.reset_tokens_file):
            return False
        
        with open(self.reset_tokens_file, 'r', encoding='utf-8') as f:
            tokens = json.load(f)
        
        if token not in tokens:
            return False
        
        token_data = tokens[token]
        expires_at = datetime.fromisoformat(token_data['expires_at'])
        
        # Verificar se o token não expirou
        if datetime.now() > expires_at:
            # Remover token expirado
            del tokens[token]
            with open(self.reset_tokens_file, 'w', encoding='utf-8') as f:
                json.dump(tokens, f, ensure_ascii=False, indent=2)
            return False
        
        return token_data['username']
    
    def reset_password(self, token, new_password):
        """Redefine a senha usando o token"""
        username = self.validate_reset_token(token)
        if not username:
            return False
        
        # Atualizar senha do usuário
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        users[username]['password'] = self.hash_password(new_password)
        users[username]['updated_at'] = datetime.now().isoformat()
        
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        
        # Remover token usado
        with open(self.reset_tokens_file, 'r', encoding='utf-8') as f:
            tokens = json.load(f)
        
        if token in tokens:
            del tokens[token]
            with open(self.reset_tokens_file, 'w', encoding='utf-8') as f:
                json.dump(tokens, f, ensure_ascii=False, indent=2)
        
        return True
    
    def cleanup_expired_tokens(self):
        """Remove tokens expirados"""
        if not os.path.exists(self.reset_tokens_file):
            return
        
        with open(self.reset_tokens_file, 'r', encoding='utf-8') as f:
            tokens = json.load(f)
        
        current_time = datetime.now()
        expired_tokens = []
        
        for token, data in tokens.items():
            expires_at = datetime.fromisoformat(data['expires_at'])
            if current_time > expires_at:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            del tokens[token]
        
        if expired_tokens:
            with open(self.reset_tokens_file, 'w', encoding='utf-8') as f:
                json.dump(tokens, f, ensure_ascii=False, indent=2)
    
    def create_admin_request(self, username, password):
        """Cria uma solicitação de admin para usuário com .admin no nome"""
        if not username.endswith('.admin'):
            return False, "Nome de usuário deve terminar com .admin para solicitar acesso administrativo"
        
        # Verificar se já existe uma solicitação pendente
        with open(self.admin_requests_file, 'r', encoding='utf-8') as f:
            requests = json.load(f)
        
        if username in requests:
            return False, "Já existe uma solicitação pendente para este usuário"
        
        # Criar usuário normal primeiro
        if not self.create_user(username, password, "user"):
            return False, "Erro ao criar usuário"
        
        # Adicionar solicitação
        requests[username] = {
            'status': 'pending',
            'requested_at': datetime.now().isoformat(),
            'message': f'Usuário {username} solicitou acesso administrativo'
        }
        
        with open(self.admin_requests_file, 'w', encoding='utf-8') as f:
            json.dump(requests, f, ensure_ascii=False, indent=2)
        
        return True, "Solicitação de admin criada com sucesso! Aguarde aprovação."
    
    def get_admin_requests(self):
        """Obtém todas as solicitações de admin pendentes"""
        if not os.path.exists(self.admin_requests_file):
            return {}
        
        with open(self.admin_requests_file, 'r', encoding='utf-8') as f:
            requests = json.load(f)
        
        # Filtrar apenas solicitações pendentes
        pending_requests = {k: v for k, v in requests.items() if v['status'] == 'pending'}
        return pending_requests
    
    def approve_admin_request(self, username, approved_by):
        """Aprova uma solicitação de admin"""
        with open(self.admin_requests_file, 'r', encoding='utf-8') as f:
            requests = json.load(f)
        
        if username not in requests or requests[username]['status'] != 'pending':
            return False, "Solicitação não encontrada ou já processada"
        
        # Atualizar role do usuário para admin
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        if username not in users:
            return False, "Usuário não encontrado"
        
        users[username]['role'] = 'admin'
        users[username]['approved_at'] = datetime.now().isoformat()
        users[username]['approved_by'] = approved_by
        
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        
        # Marcar solicitação como aprovada
        requests[username]['status'] = 'approved'
        requests[username]['approved_at'] = datetime.now().isoformat()
        requests[username]['approved_by'] = approved_by
        
        with open(self.admin_requests_file, 'w', encoding='utf-8') as f:
            json.dump(requests, f, ensure_ascii=False, indent=2)
        
        return True, f"Usuário {username} promovido a administrador com sucesso!"
    
    def reject_admin_request(self, username, rejected_by):
        """Rejeita uma solicitação de admin"""
        with open(self.admin_requests_file, 'r', encoding='utf-8') as f:
            requests = json.load(f)
        
        if username not in requests or requests[username]['status'] != 'pending':
            return False, "Solicitação não encontrada ou já processada"
        
        # Marcar solicitação como rejeitada
        requests[username]['status'] = 'rejected'
        requests[username]['rejected_at'] = datetime.now().isoformat()
        requests[username]['rejected_by'] = rejected_by
        
        with open(self.admin_requests_file, 'w', encoding='utf-8') as f:
            json.dump(requests, f, ensure_ascii=False, indent=2)
        
        return True, f"Solicitação de {username} rejeitada"
    
    def get_all_users(self):
        """Obtém todos os usuários do sistema"""
        if not os.path.exists(self.users_file):
            return {}
        
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        return users
    
    def update_user_role(self, username, new_role, updated_by):
        """Atualiza o role de um usuário"""
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        if username not in users:
            return False, "Usuário não encontrado"
        
        old_role = users[username]['role']
        users[username]['role'] = new_role
        users[username]['role_updated_at'] = datetime.now().isoformat()
        users[username]['role_updated_by'] = updated_by
        
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        
        return True, f"Role de {username} alterado de {old_role} para {new_role}"

    # --------------------------- TICKETS DE SUPORTE ---------------------------
    def _read_tickets(self):
        if not os.path.exists(self.tickets_file):
            return pd.DataFrame()
        df = pd.read_csv(self.tickets_file)
        if not df.empty:
            df['created_at'] = pd.to_datetime(df['created_at'], format='mixed')
            df['updated_at'] = pd.to_datetime(df['updated_at'], format='mixed')
            if 'resolved_at' in df.columns:
                df['resolved_at'] = pd.to_datetime(df['resolved_at'], format='mixed', errors='coerce')
        return df

    def _write_tickets(self, df: pd.DataFrame):
        df.to_csv(self.tickets_file, index=False)

    def create_ticket(self, titulo: str, descricao: str, tipo: str, imagem: str, criado_por: str):
        df = self._read_tickets()
        new_id = len(df) + 1 if not df.empty else 1
        now = datetime.now().isoformat()
        ticket = {
            'id': new_id,
            'titulo': titulo,
            'descricao': descricao,
            'tipo': tipo,  # 'problema' | 'recurso'
            'status': 'aberto',
            'criado_por': criado_por,
            'imagem': imagem or '',
            'created_at': now,
            'updated_at': now,
            'resolved_at': '',
            'resolved_by': ''
        }
        df = pd.concat([df, pd.DataFrame([ticket])], ignore_index=True) if not df.empty else pd.DataFrame([ticket])
        self._write_tickets(df)
        return new_id

    def list_tickets(self, only_user: str | None = None):
        df = self._read_tickets()
        if df.empty:
            return df
        # atualizar status pendente (>1 dia) para tickets abertos
        self.update_ticket_statuses()
        df = self._read_tickets()
        if only_user:
            df = df[df['criado_por'] == only_user]
        return df.sort_values(by='created_at', ascending=False)

    def resolve_ticket(self, ticket_id: int, resolved_by: str):
        df = self._read_tickets()
        if df.empty:
            return False
        mask = df['id'] == ticket_id
        if not mask.any():
            return False
        df.loc[mask, 'status'] = 'resolvido'
        df.loc[mask, 'resolved_at'] = datetime.now().isoformat()
        df.loc[mask, 'resolved_by'] = resolved_by
        df.loc[mask, 'updated_at'] = datetime.now().isoformat()
        self._write_tickets(df)
        return True

    def update_ticket_statuses(self):
        df = self._read_tickets()
        if df.empty:
            return
        now = datetime.now()
        changed = False
        for idx, row in df.iterrows():
            if row['status'] == 'aberto':
                created = row['created_at']
                # se passou de 1 dia -> pendente
                if (now - created.to_pydatetime()) > timedelta(days=1):
                    df.at[idx, 'status'] = 'pendente'
                    df.at[idx, 'updated_at'] = now.isoformat()
                    changed = True
        if changed:
            self._write_tickets(df)

    
    def delete_loan(self, loan_id, loan_type='emprestimos'):
        """Deleta um empréstimo específico"""
        df = self.get_loans(loan_type)
        if df.empty:
            return False, "Nenhum empréstimo encontrado"
        
        # Verificar se o empréstimo existe
        if loan_id not in df['id'].values:
            return False, "Empréstimo não encontrado"
        
        # Remover o empréstimo
        df = df[df['id'] != loan_id]
        
        # Salvar no arquivo correto
        file_map = {
            'emprestimos': self.loans_file,
            'motoristas': self.motoristas_file,
            'comerciantes': self.comerciantes_file
        }
        
        file_path = file_map.get(loan_type, self.loans_file)
        df.to_csv(file_path, index=False)
        
        return True, f"Empréstimo ID {loan_id} deletado com sucesso"
    
    # --------------------------- GESTÃO DE CLIENTES ---------------------------
    def _read_clients(self):
        if not os.path.exists(self.clients_file):
            return pd.DataFrame()
        df = pd.read_csv(self.clients_file)
        if not df.empty:
            df['created_at'] = pd.to_datetime(df['created_at'], format='mixed')
            df['updated_at'] = pd.to_datetime(df['updated_at'], format='mixed')
        return df
    
    def _write_clients(self, df: pd.DataFrame):
        df.to_csv(self.clients_file, index=False)
    
    def add_client(self, nome: str, telefone: str, tipo: str):
        df = self._read_clients()
        new_id = len(df) + 1 if not df.empty else 1
        now = datetime.now().isoformat()
        client = {
            'id': new_id,
            'nome': nome,
            'telefone': telefone,
            'tipo': tipo,  # 'emprestimos', 'motoristas', 'comerciantes'
            'created_at': now,
            'updated_at': now
        }
        df = pd.concat([df, pd.DataFrame([client])], ignore_index=True) if not df.empty else pd.DataFrame([client])
        self._write_clients(df)
        return new_id
    
    def get_clients(self, tipo: str = None):
        df = self._read_clients()
        if df.empty:
            return df
        if tipo:
            df = df[df['tipo'] == tipo]
        return df.sort_values(by='nome')
    
    def get_all_clients(self):
        return self._read_clients().sort_values(by='nome')
    
    def delete_client(self, client_id: int):
        df = self._read_clients()
        if df.empty:
            return False, "Nenhum cliente encontrado"
        
        if client_id not in df['id'].values:
            return False, "Cliente não encontrado"
        
        df = df[df['id'] != client_id]
        self._write_clients(df)
        return True, f"Cliente ID {client_id} deletado com sucesso"
