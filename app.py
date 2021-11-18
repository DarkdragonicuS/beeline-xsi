from flask import Flask,request
from datetime import datetime,time
import xmltodict,requests

listenHost = '172.16.16.120'
listenPort = 5000
debugLogPath = 'c:\\obmen\\log.txt'
telegramChatIds = []
telegramToken = ''
endOfWorkTime = time(18)
startOfWorkTime = time(9)
weekEnd = [5,6]

app = Flask(__name__)

@app.route('/events/null', methods=['POST'])
def events():
    parseEvent(request.data)
    return 'OK'

def dosmth():
    print('hello')
    return 0

def parseEvent(data):
    xmlBody = xmltodict.parse(data)
    try:
        with open(debugLogPath,'a') as logFile:
                logFile.write(xmltodict.unparse(xmlBody))
                logFile.close()
        if xmlBody['xsi:Event']['xsi:eventData']['@xsi1:type'] == 'xsi:CallAnsweredEvent':
            answerer = xmlBody['xsi:Event']['xsi:eventData']['xsi:call']['xsi:endpoint']['xsi:addressOfRecord'].split('@')[0]
            caller = xmlBody['xsi:Event']['xsi:eventData']['xsi:call']['xsi:remoteParty']['xsi:address']['#text'].split(':')[1]
            if xmlBody['xsi:Event']['xsi:eventData']['xsi:call']['xsi:personality'] == 'Terminator':
                sendToChat(caller,answerer)
    except Exception:
        pass

def sendToChat(caller,answerer):
    message = 'На звонок от ' + caller + ' ответил ' + answerer
    print(message)
    currentTime = datetime.now().time()
    DoF = datetime.now().weekday()
    if endOfWorkTime <= currentTime <= startOfWorkTime or DoF in weekEnd:
        headers={
            'Content-Type':'application/json',
            'Accept':'application/json'
        }
        for chatId in telegramChatIds:
            params = {
                'chat_id':chatId,
                'text':message
            }
            requests.post(url='https://api.telegram.org/bot'+telegramToken+'/sendMessage',params=params,headers=headers)

app.run(host=listenHost, port=listenPort)
