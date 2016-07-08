import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.mime.message import MIMEMessage
#from email import message
import urllib

def send_page(to_user,page_name,page_content,subject,m_id,ref):
	msg = MIMEMultipart('alternative')
	msg["Message-ID"] = email.utils.make_msgid()
	msg["In-Reply-To"] = m_id

	if(ref==None):
		msg["References"] = m_id
	else:
		msg["References"] = ref+"\n"+m_id

	msg['Subject'] = subject
	msg['From'] = "ps.mio.bits@gmail.com"
	msg['To'] = to_user
	
	html = urllib.urlopen("indexa.htm").read()
	html = html + page_name
	htmla = urllib.urlopen("indexb.htm").read()
	html = html+htmla+page_content
	htmla = urllib.urlopen("indexc.htm").read()
	html = html + htmla

	msg.attach(MIMEText(html, 'html'))
	smtpObj=smtplib.SMTP('smtp.gmail.com', 587)
	smtpObj.ehlo()
	smtpObj.starttls()
	smtpObj.login('ps.mio.bits@gmail.com','1Guesswhat')
	smtpObj.sendmail('ps.mio.bits@gmail.com',to_user,msg.as_string())
	smtpObj.quit()
	
