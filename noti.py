import sys
import sqlite3
import telepot
from datetime import date
import traceback
import requests
import xml.etree.ElementTree as ET
import token

TOKEN = token.TOKEN
MAX_MSG_LENGTH = 300
bot = telepot.Bot(TOKEN)

def getData(ccbakdcd, ccbaasno, ccbactcd):
    url = 'http://www.cha.go.kr/cha/SearchKindOpenapiDt.do?ccbaKdcd=' + ccbakdcd + '&ccbaAsno=' + ccbaasno + '&ccbaCtcd=' + ccbactcd
    response = requests.get(url)
    root = ET.fromstring(response.text)
    ccbaMnm1 = root.findtext(".//item//ccbaMnm1")
    content = root.findtext(".//item//content")

    res_list = [ccbaMnm1, content]
    return res_list

def sendMessage(user, msg):
    try:
        bot.sendMessage(user, msg)
    except:
        traceback.print_exc(file=sys.stdout)

def run(date_param, param='11710'):
    conn = sqlite3.connect('logs.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS logs( user TEXT, log TEXT, PRIMARY KEY(user, log) )')
    conn.commit()
    getData()
    user_cursor = sqlite3.connect('save.db').cursor()
    user_cursor.execute('CREATE TABLE IF NOT EXISTS users( user TEXT, location TEXT, PRIMARY KEY(user, location) )')
    user_cursor.execute('SELECT * from users')

    for data in user_cursor.fetchall():
        print(data)
        user, param = data[0], data[1]
        #print(user, date_param, param)
        res_list = getData()
        msg = ''
        for r in res_list:
            try:
                cursor.execute('INSERT INTO logs (user,log) VALUES ("%s", "%s")'%(user,r))
            except sqlite3.IntegrityError:
                # 이미 해당 데이터가 있다는 것을 의미합니다.
                pass
            else:
                #print( str(datetime.now()).split('.')[0], r )
                if len(r+msg)+1>MAX_MSG_LENGTH:
                    sendMessage( user, msg )
                    msg = r+'\n'
                else:
                    msg += r+'\n'
        if msg:
            sendMessage( user, msg )
    conn.commit()

if __name__=='__main__':
    today = date.today()
    current_month = today.strftime('%Y%m')

    #print( '[',today,']received token :', TOKEN )

    #pprint( bot.getMe() )

    run(current_month)
