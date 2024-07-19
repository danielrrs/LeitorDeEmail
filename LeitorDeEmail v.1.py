import streamlit as st
import pandas as pd
import imaplib
import email
from email.header import decode_header

# Função para obter os dados dos e-mails
def get_email_data():
    # Configurações da conta de e-mail
    username = "daniel.reis@seniormais.com.br"
    password = "daniel157"

    # Conectar ao servidor IMAP do Gmail
    mail = imaplib.IMAP4_SSL("imap.uhserver.com")
    mail.login(username, password)
    mail.select("inbox")

    # Pesquisar todos os e-mails
    status, messages = mail.search(None, 'ALL')

    # Converter os IDs das mensagens em uma lista
    mail_ids = messages[0].split()

    # Listas para armazenar dados dos e-mails
    emails_data = []

    # Loop para ler os e-mails
    for mail_id in mail_ids:
        status, msg_data = mail.fetch(mail_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        # Extrair o remetente, assunto e data
        from_ = msg.get("From")
        subject, encoding = decode_header(msg.get("Subject"))[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else "utf-8")
        date = msg.get("Date")
        
        # Extrair o conteúdo do e-mail
        email_content = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode()
                        email_content += body
                    except:
                        pass
        else:
            try:
                email_content = msg.get_payload(decode=True).decode()
            except:
                email_content = ""

        # Adicionar os dados do e-mail na lista
        emails_data.append([from_, subject, date, email_content])

    # Converter a lista de dados dos e-mails em um DataFrame do Pandas
    df = pd.DataFrame(emails_data, columns=["From", "Subject", "Date", "Content"])

    # Fechar a conexão com o servidor
    mail.logout()

    return df

# Obter os dados dos e-mails
df = get_email_data()

# Criar o painel com Streamlit
st.title("Painel de Chamados")
st.write("Aqui estão todos os e-mails:")

# Mostrar os dados dos e-mails no painel
for index, row in df.iterrows():
    st.subheader(f"Email {index + 1}")
    st.write(f"**De:** {row['From']}")
    st.write(f"**Assunto:** {row['Subject']}")
    st.write(f"**Data:** {row['Date']}")
    st.write(f"**Conteúdo:**\n{row['Content']}")
    st.write("\n\n")