'''
Created on Nov 8, 2015

@author: zhuoli
'''
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

import ConsoleUtilities


class Email:

    DEBUG = True;

    def __init__(self, gmail_user, gmail_pwd):
        self.gmail_user = gmail_user
        self.gmail_pwd = gmail_pwd
         
    def Authenticate(self):

        if Email.DEBUG:
            return

         # Authenticate
        server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server_ssl.ehlo() # optional, called by login()
        server_ssl.login(self.gmail_user, self.gmail_pwd)  
        server_ssl.close()

    def send_email(self,recipient, subject, body):

        if Email.DEBUG:
            return

        FROM = self.gmail_user
        TO = recipient if type(recipient) is list else [recipient]
        COMMASPACE = ', '
        
        msg = MIMEMultipart()
        msg['From'] = self.gmail_user
        msg['To'] = COMMASPACE.join(TO)
        msg['Subject'] = subject  
        msg.attach(MIMEText(body))
        msg.attach(MIMEText('\n More price here: http://coinmarketcap.com/currencies/views/all/', 'plain'))
         
        try:
            # SMTP_SSL Example
            server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server_ssl.ehlo() # optional, called by login()
            server_ssl.login(self.gmail_user, self.gmail_pwd)  
            # ssl server doesn't support or need tls, so don't call server_ssl.starttls() 
            server_ssl.sendmail(FROM, TO, msg.as_string())
            #server_ssl.quit()
            server_ssl.close()
            ConsoleUtilities.WriteLine('successfully sent the mail')
        except:
            ConsoleUtilities.WriteLine('failed send the mail')
            
            