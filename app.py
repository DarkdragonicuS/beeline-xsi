from time import sleep
from flask import Flask,request
from datetime import datetime,time
import xmltodict,requests,json
from threading import Thread
####################   REMOTE DEBUG   #############################
import debugpy                                                    #
debugpy.listen(('0.0.0.0', 5678))                                 #  
debugpy.wait_for_client()                                         #
###################################################################

listenHost = '0.0.0.0'
listenPort = 5000
externalUrl = ''
debugLogPath = ''
telegramChatIds = []
telegramToken = ''
xsiAbonents = []
xsiSubscribes = dict()
xsiToken = ''
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
                logFile.write(xmltodict.unparse(xmlBody).replace('\n',''))
                logFile.write('\n')
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

def subscriptionUpdateJob():
    while True:
        sleep(60)
        for abonent in xsiSubscribes:
            print('Checking subscription for abonent ' + abonent + '...',end='')
            if not checkSubscription(xsiSubscribes[abonent]):
                print('done!')
                print('Updating subscription...',end='')
                xsiSubscribes[abonent] = subscribeToEvent(abonent)
                print('done!')
            else:
                print('done!')
                print('Subscription isn\'t expired.')

def checkSubscription(subscriptionId):
    headers = {
        'X-MPBX-API-AUTH-TOKEN':xsiToken,
        'Accept':'application/json'
    }
    params = {
        'subscriptionId':subscriptionId
    }
    response = requests.get(url='https://cloudpbx.beeline.ru/apis/portal/subscription',params=params,headers=headers)
    if 'expires' in response.json():
        return True
    else:
        return False

def subscribeToEvent(pattern):
    url = 'https://cloudpbx.beeline.ru/apis/portal/subscription'
    headers = {
        'X-MPBX-API-AUTH-TOKEN':xsiToken,
        'Content-Type':'application/json'
    }
    params = {
        'pattern':pattern,
        'expires':86400,
        'subscriptionType':'BASIC_CALL',
        'url':externalUrl
    }
    response = requests.put(url=url,headers=headers,data=json.dumps(params))
    return response.json()['subscriptionId']

def serverRun():
    app.run(host=listenHost, port=listenPort)

Thread(target=serverRun).start()

# initial subscription
for abonent in xsiAbonents:
    #xsiSubscrubeIds[xsiSubscrubeIds.index(abonent)] = subscribeToEvent(abonent)
    xsiSubscribes[abonent] = subscribeToEvent(abonent)

Thread(target=subscriptionUpdateJob).start()

