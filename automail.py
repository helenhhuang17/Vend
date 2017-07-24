from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import date,timedelta
import export_sales
import shift_planning

today = date.today()

outlets = ["MTA","JFK","GAR"]
for outlet in outlets:
    export_sales.print_sales(today,today+timedelta(1),outlet,
        "logs/{}.csv".format(outlet))

fromaddr = "john.shen@hsa.net"
toaddr = "alejandra.resendiz@hsa.net"

msg = MIMEMultipart()

msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Products Sold {}".format(date.today())

body = "Automated Message: Here are the products sold for the day."

msg.attach(MIMEText(body, 'plain'))

for f in outlets:
    attachment = open("logs/{}.csv".format(f), "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % f)
    msg.attach(part)

server = SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, "5tE[V5BX9;")
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()
