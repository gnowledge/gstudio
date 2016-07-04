import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email import message

def send_page(to_user,page_name,page_content,subject,id):
	msg = MIMEMultipart('alternative')
	msg['Subject'] = subject
	msg['From'] = "ps.mio.bits@gmail.com"
	msg['To'] = to_user 
	msg['_id'] = id
	
	html = """\
	<html>
	<head></head>
	<body>
		<H1>{pg_name}</H1>
		<H2>{pg_content}</H2>
		<p>Hi!<br>
			<font color="blue"> How are ssssyou?</font><br>
			Here is the <a href="http://www.python.org">link</a> you wanted.
		</p>
	</body>
	</html>
	""".format(pg_name=page_name,pg_content=page_content)

	msg.attach(MIMEText(html, 'html'))
	smtpObj=smtplib.SMTP('smtp.gmail.com', 587)
	smtpObj.ehlo()
	smtpObj.starttls()
	smtpObj.login('ps.mio.bits@gmail.com','1Guesswhat')
	smtpObj.sendmail('ps.mio.bits@gmail.com',to_user,msg.as_string())
	smtpObj.quit()