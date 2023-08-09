from umqtt.simple import MQTTClient
from machine import Timer,Pin
import network
import os
import time
import machine


SERVER ="7c11acf6a_XXXXXX_5385_XXXXXXXXX.s2.eu.hivemq.cloud" #"broker.hivemq.com" HIveMQ cluster name
ssl_params = {"server_hostname": SERVER} 
ssid='#########'
password='####'
CLIENT_ID = "asdaw@#j8787"

zzzzz_topic_sub='ntp'     
zzzzz_topic_status='nts'
zzzz_topic_random='nts11'


# led setup
led = Pin(2, Pin.OUT)
#ledD0=Pin(16,Pin.OUT)
ledD0 = machine.Pin(16, machine.Pin.OUT)

wlan=network.WLAN(network.STA_IF)
#ap_if = network.WLAN(network.AP_IF)


wlan.active(True)



#ap_if.config(essid=ssid, password=password)

connectedToWIFI=False

def do_connect():
    global connectedToWIFI    
    if not wlan.isconnected():
 #       print('connecting to network...')
        wlan.connect('username', 'passwd')        
        while not wlan.isconnected():
            #print('wlan not connected')
            connectedToWIFI=False
            time.sleep(10)
            pass
    connectedToWIFI=True
  #  print('wlan connected',connectedToWIFI)
   # print('network config:', wlan.ifconfig())
    time.sleep(2)
    show_NW_STATUS()

def show_NW_STATUS():
    ledD0.off()
    #while True:     
      #ledD0.value(not ledD0.value())
      #time.sleep(0.5)
      #print('wlan value ',connectedToWIFI)
     

do_connect()



led12=Pin(12,Pin.OUT)#D6-led1
led13=Pin(13,Pin.OUT)#D7-LED2
led14=Pin(14,Pin.OUT)#D5-LED3
led15=Pin(15,Pin.OUT)#D8-LED4

client=None

def publishLEDStatus(data):
#    print('client data to publish ',data)
    client.publish(zzzz_topic_status,data)
#    print('successfuly published the data')
    


def controlLights(data):
    #print('pro-data::',data)
    if data == "LED1-ON":
        led12.value(1)
    elif data == "LED2-ON":
        led13.value(1)
    elif data == "LED3-ON":
        led14.value(1)
    elif data == "LED4-ON":
        led15.value(1)         
    elif data == "LED1-OFF":
        led12.value(0)
    elif data == "LED2-OFF":
        led13.value(0)
    elif data == "LED3-OFF":
        led14.value(0)
    elif data == "LED4-OFF":
        led15.value(0)
    publishLEDStatus(data)
        
 

def restart_and_reconnect():
  #print('Failed to connect to MQTT broker. Reconnecting...')
  ledD0.on()
  time.sleep(5)  
  machine.reset()

def sub_cb(topic, msg):             # Callback function when a subscription message is received
  #print((topic, msg))             # Print the received topic message
  data=msg.decode()
  #print(data)
  controlLights(data)
  #print('done') 

def connect_and_subscribe():
    c = MQTTClient(CLIENT_ID, SERVER,port=8883,user='#####',password='####1#',ssl=True,ssl_params=ssl_params)   # MQTTClient class instance, and set the connection hold interval to 30 seconds
    c.connect()                             # mqtt connects
    client=c
    c.set_callback(sub_cb)                  # Set callback function
    c.subscribe(zzzzz_topic_sub)
    '''Send BOOT message'''
    c.publish("boot","boot")       
   # print("Connected to %s" % SERVER)
    return client

try:
  client = connect_and_subscribe()
except OSError as e:
    print(e)
    restart_and_reconnect()

while True:
  try:
    #print('MQTT client in waiting state..')
    client.check_msg() 
    client.publish(zzzz_topic_random, "up")
    time.sleep(1)
  except OSError as e:
    print(e)
    restart_and_reconnect()

#try:
   # tim1 = Timer(1)                          # Create Timer 1
   # tim1.init(period=20000, mode=Timer.PERIODIC,callback=lambda n:c.ping())
   # Send PING at 20-second intervals to keep connected

 #   while True:
        #print('MQTT client in waiting state..')
  #      c.wait_msg()                    # Waiting for messages in a loop
#except OSError as e:
 #restart_and_reconnect()
  
#finally:
 #   print('MQTT client finally disconnected')
    #c.disconnect()                     # When abnormal, disconnect MQTT



