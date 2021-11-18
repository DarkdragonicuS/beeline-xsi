from flask import Flask,request
import xmltodict

listenHost = '127.0.0.1'
listenPort = 5000
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
    if xmlBody['xsi:Event']['xsi:eventData']['@xsi1:type'] == 'xsi:CallAnsweredEvent':
        answerer = xmlBody['xsi:Event']['xsi:eventData']['xsi:call']['xsi:endpoint']['xsi:addressOfRecord'].split('@')[0]
        caller = xmlBody['xsi:Event']['xsi:eventData']['xsi:call']['xsi:remoteParty']['xsi:address']['#text'].split(':')[1]
        sendToChat(caller,answerer)

def sendToChat(caller,answerer):
    print('На звонок от ' + caller + ' ответил ' + answerer)

app.run(host=listenHost, port=listenPort)
