import cv2
import numpy as np
import pytesseract
import datetime
import paho.mqtt.client as paho
import time
from number_plate import print_number
char0 = "-"
char1 = "."
ABC = 'abc'
sub_topic = "esp32/trigercam"
pub_topic = "esp32/car"
cap = cv2.VideoCapture(0)
cap1 = cv2.VideoCapture(1)

def on_publish(client, userdata, mid):
    print("mid: "+str(mid))
 
def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))
    
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))       
    ABC = msg.payload.decode("utf-8")
    print("Publishing...")
    ret, frame = cap.read()
    ret1, frame1 = cap1.read()
    if(msg.payload.decode("utf-8") == "1"):
        print("11111111")
        while (str(ABC)=='1'):
            if (ret):
                now = datetime.datetime.now()
                dt =  now.strftime("%Y/%m/%d %a %H:%M:%S")
                new_dt = ''.join(filter(str.isalnum, dt))
                data = ''
                while (len(data)!=11):
                    ret, frame = cap.read()
                    cropped, image = print_number.Find_number(frame)
                    data = print_number.Print_number(image)
                    if (len(data)==11):
                        if char0 in data:
                            if char1 in data:
                                break
                            else:
                                data=''
                        else:
                            data=''
                data_in = data
                new_data = ''.join(filter(str.isalnum, data_in))
                f = open('IN.txt', 'a')
                timein = now
                print("Date_IN:",timein)
                cv2.imwrite("IN/" + new_data+ "_" + new_dt + ".jpg", cropped)
                print("Bien so xe la:")
                print(data_in)
                f.write("Time in: {} || License plate: {} ".format(dt,data_in))
                f.close()
                (rc, mid) = client.publish(pub_topic, str(data_in), qos=1)
                ABC = "0"
                cv2.waitKey(1)
                if (len(data_in)==11):
                    break 
        # if (ret1):
        #     cv2.imshow("Image",frame1)
    if(msg.payload.decode("utf-8") == "3"):
        print("3333333")
        while True:
            if (ret1):
                now = datetime.datetime.now()
                dt =  now.strftime("%Y/%m/%d %a %H:%M:%S")
                new_dt = ''.join(filter(str.isalnum, dt))
                data = ''
                while (len(data)!=11):
                    ret1, frame1 = cap1.read()
                    cropped, image = print_number.Find_number(frame1)
                    data = print_number.Print_number(image)
                    if (len(data)==11):
                        if char0 in data:
                            if char1 in data:
                                break
                            else:
                                data=''
                        else:
                            data=''
                data_out = data
                new_data = ''.join(filter(str.isalnum, data_out))
                f = open('OUT.txt', 'a')
                timeout = now
                print("Date_OUT:",timeout)
                cv2.imwrite("OUT/" + new_data +"_" + new_dt+ ".jpg", cropped)
                print("Bien so xe la:")
                print(data_out)
                f.write("Time out: {} || License plate: {} ".format(dt,data_out))
                f.close()
                (rc, mid) = client.publish(pub_topic, str(data_out), qos=1)
                ABC = "0"
                cv2.waitKey(1)
                if (len(data_out)==11):
                    break            
client = paho.Client()
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish

client.connect('broker.mqttdashboard.com', 1883)
client.subscribe(sub_topic, qos=1)

while True: 
    ret, frame = cap.read()
    ret1, frame1 = cap1.read()
    if (ret):
        cv2.imshow("Entrance", frame)
    if (ret1):
        cv2.imshow("Exit",frame1)
    key = cv2.waitKey(1)

    # Check for new messages every 0.1 seconds
    client.loop(timeout=0.1)

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
client.disconnect()