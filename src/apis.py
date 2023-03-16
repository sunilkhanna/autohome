import ptvsd
from fastapi import FastAPI
from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi import Form
import paho.mqtt.client as mqtt
import time
import configparser
import json


ptvsd.enable_attach(address=("localhost",8098))
#ptvsd.wait_for_attach()
ptvsd.break_into_debugger()
#MQTT broker
mqttBroker = '7c11acf6a6d04453856605869f574213.s2.eu.hivemq.cloud'
mqttPort=8883
#mqttBroker="broker.hivemq.com"


#-------Cloud-1 Noida setup----------//
noida_topic_pub="ntp"
noida_topic_sub="nts"

#-------Cloud-2 SVPI setup----------//
svpi_topic_pub="stp"
svpi_topic_sub="sts"

global stats
stats='11'


BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))
router = APIRouter()
app = FastAPI()

# the callback function, it will be triggered when receiving messages
def on_message(mqttClient, userdata, msg):           
    print(f"{msg.topic} {msg.payload}")
    recvdMsg=str(msg.payload.decode("utf-8")).strip()
    print(recvdMsg.strip())
    if(recvdMsg.strip()=='boot'):
        #read the status file and publish the messages
        print('Client or MCU rebooted..')
        regainStats()    


def on_connect(mqttClient, userdata, flags, rc):    
    # subscribe, which need to put into on_connect
    # if reconnect after losing the connection with the broker, it will continue to subscribe to the raspberry/topic topic 
    if rc==0:
        mqttClient.connected_flag=True       
       # mqttClient.subscribe(noida_topic_pub)
       # print('connected..')

def on_disconnect(mqttClient, userdata, rc):    
    mqttClient.connected_flag=False
    

mqtt.Client.connected_flag=False #create flag in class
mqttClient = mqtt.Client("HomeAutomation")
# enable TLS for secure connection

mqttClient.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
mqttClient.username_pw_set("sunilkhanna","Sunil321#")
mqttClient.on_connect = on_connect
mqttClient.on_disconnect=on_disconnect
mqttClient.on_message = on_message
mqttClient.loop_start()
mqttClient.connect(mqttBroker,mqttPort)



while not mqttClient.connected_flag:
    print('wait in loop')
    time.sleep(1)


@app.get("/updateProps/{data}")
def updateStats(request: Request,data: str):
    '''Method use to update the status of controllable items '''
    
    print("updating status to property file")
    config = configparser.RawConfigParser()
    config.read('./src/stats.properties') #//TODO - error handling support
    spr=data.split('-')   
    print(data,"--",spr[0].lower())    
    config.set('GNDASection', spr[0].lower(),data.upper())
    with open('./src/stats.properties', 'w') as configfile:
        config.write(configfile)
        configfile.close()

def getStatsJson():
    ''' get the data from stats file '''
    configx = configparser.RawConfigParser()
    configx.read('./src/stats.properties')
    configSectionx=configx['GNDASection']
    dictx={}
    for key in configSectionx:
        dictx.update({key.upper():configSectionx.get(key)})
    jsonDataStats=json.dumps(dictx)                 
    return jsonDataStats
    
def regainStats():
    ''' Let's back to the original state after reboot '''
    print("regain status on MCU boot")
    config = configparser.RawConfigParser()
    config.read('./src/stats.properties')
    configSection=config['GNDASection']
    for key in configSection:
        print(configSection.get(key))
        mqttClient.publish(noida_topic_pub,configSection.get(key))    
    
    
@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):    
    return templates.TemplateResponse("login.html", {"request": request})

#@app.post("/login/")
#async def login(username: str = Form(), password: str = Form()):
 #   return {"username": username}


@app.get("/outside1/{id}")
async def read_but(request: Request,id: str):    
    buttonStatus=id.split("-")
    print('*********Button pressed')
    if mqttClient.connected_flag:
        result=mqttClient.publish(noida_topic_pub,id) ##------publish message to broker------------    
        result.wait_for_publish()
        print(result.mid,result.is_published(),result.__next__(),result.next(),result.rc)    
        status = result[0]
        if status == 0:
            print("Message Sent  to topic-- " +noida_topic_pub)
            #updateStats(id)#udpate the stats
            if buttonStatus[1]=="ON":
                return "OFF"
            return "ON"  
        print("Failed to send message to topic"+ noida_topic_pub)
        return buttonStatus[1]


@app.post("/home")
def do_something(request: Request, uname: str = Form(...), psw: str = Form(...)):
    print(uname)
    print("psw "+psw)
    if(uname.__eq__('sunil') &  psw.__eq__('khanna')): 
        ledStatus = getStatsJson()
        #{"LED1":"LED1-ON","LED2":"LED2-ON","LED3":"LED3-ON","LED4":"LED4-OFF","LED5":"LED5-ON"}
        return templates.TemplateResponse("home.html",  {"request": request,"ledStatus":ledStatus})
    else:
        return "Invalid Username/Password"

@app.get("/items/", response_class=HTMLResponse)
async def read_items():
    return """   """    