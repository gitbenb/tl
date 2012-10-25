# tl/utils/email.py
#
# BHJTW 12-10-2012 taken from http://jackal777.wordpress.com/2011/07/19/sending-emails-via-gmail-with-python3/

""" email related functions. """

## tl imports

from tl.lib.config import getmainconfig

## basic imports

import smtplib
import os

## email imports


from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

## sendemail function

def sendmail(user, to, subject, text, attach, server=None, port=None):
   msg = MIMEMultipart()
   msg['From'] = user
   msg['To'] = to
   msg['Subject'] = subject
   msg.attach(MIMEText(text))

   part = MIMEBase('application', 'octet-stream')
   part.set_payload(open(attach, 'rb').read())
   encoders.encode_base64(part)
   part.add_header('Content-Disposition','attachment; filename="%s"' % os.path.basename(attach))
   msg.attach(part)

   cfg = getmainconfig()

   mailServer = smtplib.SMTP(server or mainconfig.emailserver or "localhost", 25 or mainconfig.emailport)
   mailServer.ehlo()
   mailServer.starttls()
   mailServer.ehlo()
   mailServer.login(user or mainconfig.emailfrom, pwd or mainconfig.emailpwd or "")
   result = mailServer.sendmail(user, to, msg.as_string())
   # Should be mailServer.quit(), but that crashes...
   mailServer.close()
   return result
