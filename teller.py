import sqlite3
import telepot
from datetime import date

import noti

data = []
ccbakdcd, ccbaasno, ccbactcd = 0, 0, 0
def replyAptData(user):
    #print(user)
    res_list = noti.getData(ccbakdcd, ccbaasno, ccbactcd)
    msg = ''
    for r in res_list:
        #print( str(datetime.now()).split('.')[0], r )
        if len(r+msg)+1>noti.MAX_MSG_LENGTH:
            noti.sendMessage( user, msg )
            msg = r+'\n'
        else:
            msg += r+'\n'
    if msg:
        noti.sendMessage( user, msg )
    else:
        noti.sendMessage( user, '데이터가 없습니다.' )

def save( user, loc_param ):
    conn = sqlite3.connect('save.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users( user TEXT, location TEXT, PRIMARY KEY(user, location) )')
    try:
        cursor.execute('INSERT INTO users(user, location) VALUES (?, ?)', (user, loc_param))
    except sqlite3.IntegrityError:
        noti.sendMessage( user, '이미 해당 정보가 저장되어 있습니다.' )
        return
    else:
        noti.sendMessage( user, '저장되었습니다.' )
        conn.commit()

def clear( user ):
    conn = sqlite3.connect('save.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users')
    noti.sendMessage( user, '초기화 되었습니다.' )
    conn.commit()

def check( user ):
    conn = sqlite3.connect('save.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users( user TEXT, location TEXT, PRIMARY KEY(user, location) )')
    cursor.execute('SELECT * from users WHERE user="%s"' % user)
    for data in cursor.fetchall():
        row = data[1]
        noti.sendMessage( user, row )

text = ''
def handle(text, loc_param):
    chat_id = 5874810443
    if text.startswith('정보확인'):
        #print('try to 전송', args[1])
        replyAptData( chat_id )
    elif text.startswith('정보저장'):
        #print('try to 저장', args[1])
        save( chat_id, loc_param )
    elif text.startswith('저장초기화'):
        #print('try to 초기화')
        clear( chat_id )
    elif text.startswith('저장확인'):
        #print('try to 확인')
        check( chat_id )
    else:
        noti.sendMessage(chat_id, '모르는 명령어입니다.\n정보확인, 정보저장, 저장초기화, 저장확인, 확인 중 하나의 명령을 입력하세요.')

today = date.today()
current_month = today.strftime('%Y%m')

bot = telepot.Bot(noti.TOKEN)
#bot.message_loop(handle)
