# Configuração de Email para Reset de Senha
# Este arquivo é opcional e pode ser usado para integrar com serviços de email

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self):
        # Configurações do servidor de email
        # Para Gmail, use:
        # self.smtp_server = "smtp.gmail.com"
        # self.smtp_port = 587
        
        # Para Outlook, use:
        # self.smtp_server = "smtp-mail.outlook.com"
        # self.smtp_port = 587
        
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email = "seu_email@gmail.com"  # Substitua pelo seu email
        self.password = "sua_senha_de_app"  # Use senha de app do Gmail
        
    def send_reset_email(self, to_email, username, reset_token):
        """Envia email com link de reset de senha"""
        try:
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = "Recuperação de Senha - Sistema de Empréstimos"
            
            # Corpo do email
            body = f"""
            Olá {username},
            
            Você solicitou a recuperação de senha para sua conta no Sistema de Empréstimos.
            
            Use o token abaixo para redefinir sua senha:
            
            Token: {reset_token}
            
            Este token é válido por 1 hora.
            
            Se você não solicitou esta recuperação, ignore este email.
            
            Atenciosamente,
            Sistema de Empréstimos
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Conectar e enviar
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            text = msg.as_string()
            server.sendmail(self.email, to_email, text)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Erro ao enviar email: {e}")
            return False

# Exemplo de uso:
# email_service = EmailService()
# email_service.send_reset_email("usuario@email.com", "usuario", "token123")

# NOTA: Para usar este serviço, você precisa:
# 1. Configurar um email válido
# 2. Usar senha de aplicativo (não a senha normal)
# 3. Habilitar "Acesso menos seguro" ou usar OAuth2
# 4. Integrar este serviço no database.py na função generate_reset_token


