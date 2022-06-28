import serial
import time
import smtplib

from datetime import datetime

gmail_user = 'temp' #insert gmail username (note do not include @gmail.com) for sending account here
gmail_password = 'password123' #insert gmail password for sending account here

print("Start")
#These will be different for various devices and on Windows it will probably be a COM port.
sensor1Port = "COM7" #Jaffa
humidifierPort = "COM11" #Minneola
sensor2Port = "COM13" #Valencia
purifierPort = "COM3" #Hamlin
anchorPort = "COM16" #anchor

tankEmpty = False
anchorConnected = True

hBT = serial.Serial(humidifierPort, 9600)#Start communications with the bluetooth units
pBT = serial.Serial(purifierPort, 9600)
s1BT = serial.Serial(sensor1Port, 9600)
s2BT = serial.Serial(sensor2Port, 9600)

print("Connected")
hBT.flushInput() #This gives the bluetooth a little kick
pBT.flushInput()
s1BT.flushInput()
s2BT.flushInput()

onOff = "Start On";
onOff2 = "Start 2 On"

while True:
    print("Ping") #Let's check for inputs from the bluetooth units
    
    #the try-except-else is for the simpe geofencing system
    #the geofencing works by attaching a bluetooth capable device that you can carry with you to the hub, this device is called the anchor
    #each time the hub tries to read from the bluetooth devices, it will first try to establish a connection to the anchor
    #if a connection is made, the user is still in proximity to the hub, the hub proceeds to operate as usual
    #if a connection cannot be made, this means the user has carried the anchor with them outside of proximity of the hub
    #because the user is outside the proximity, they are not around to gain the benefits of the air quality being improved, air quality improving devices do not need to run
    #as the devices do not need to run, set anchorConnected to false, which later in the code will have the hub send the turn off command to the actuatable devices
    
    #if you do not wish to have this feature enabled, simple remove the try-except-else code and replace it with anchorConnected = True
    try:
        aC = serial.Serial(anchorPort, 9600)
    except:
        anchorConnected = False
    else:
        anchorConnected = True
        aC.close()
    
    if anchorConnected == True:
        s1BT.flushInput() #remove potentially old inputs that are no longer accurate
        hBT.flushInput()
        pBT.flushInput()
        s2BT.flushInput()
        
        input_data = s1BT.readline()#read humidity from Jaffa
        input_data2 = s1BT.readline()#read ppm from Jaffa
        
        #raw input to string
        strInput = input_data.decode() #humidity
        strInput2 = input_data2.decode() #ppm
        
        #string to float in order to do maths
        intput = float(strInput) #humidity
        ppm = float(str Input2) #ppm
        
        s1BT.write(str.encode('1')) #inform the Jaffa that it has been read from, to restart running averages
        
        
        s2BT.flushInput()
        
        input_dataB1 = s2BT.readline() #read dustval from Valencia
        input_dataB2 = s2BT.readline() #read ppm from Valencia
        input_dataB3 = s2BT.readline() #read humidity from Valencia
        
        #raw input to string
        strInputB1 = input_dataB1.decode() #dustval
        strInputB2 = input_dataB2.decode() #ppm
        strInputB3 = input_dataB3.decode() #humidity
        
        #string to float in order to do maths
        dustVal = float(strInputB1)
        ppm2 = float(strInputB2)
        humidity2 = float(strInputB3)
        
        s2BT.write(str.encode('1')) #inform the Minneola that it has been read from, to restart running averages
        
        intput = (intput + humidity2) / 2 #average the humidity of the two devices
        ppm = (ppm + ppm2) / 2 #average the ppm of the two devices
        
        
        hBT.flushInput()
        input_dataC = hBT.readline() #get the water level from Minneola
        strInputC = input_dataC.decode()
        waterLevel = float(strInputC)
        
        if waterLevel < 60 and tankEmpty == False: #send an em-mail that the water level is low in the humidifier tank
            hBT.write(str.encode('0')) #actuate Minneola, as it is the device which has the humidifier attached
            onOff = "Off"
            tankEmpty = True
            
            sent_from = gmail_user
            to = ['example@fake.com'] #fill in whatever e-mail you want to sent the alert to here
            subject = 'Water Level Low'
            body = 'The water level in your humidifiers tank is near empty, powering off until refilled'

            email_text = """\
            From: %s
            To: %s
            Subject: %s

            %s
            """ % (sent_from,",".join(to),subject,body)

            try:
                smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                smtp_server.ehlo()
                smtp_server.login(gmail_user, gmail_password)
                smtp_server.sendmail(sent_from, to, email_text)
                smtp_server.close()
                print("E-mail sent successfully!")
            except Exception as ex:
                print("Something went wrong...", ex)
        elif waterLevel >= 60 and tankEmpty == True: #if the tank has water, we are allowed actuate Minneola again
            tankEmpty = False
        
        if(intput > 45): #humidifier on/off based on humidity
            hBT.write(str.encode('0'))
            onOff = "Off"
        elif(intput < 40 and tankEmpty != True):
            hBT.write(str.encode('1'))
            onOff = "On"
        
        dustiness = ((dustVal/1024)-0.0356)*120000*0.035; #convert the raw dustval float into an actual 2.5pm value using this formula
        
        if(dustiness > 1000 or ppm > 400): #air purifier on/off based on either 2.5pm value or ppm of volatile compounds
            pBT.write(str.encode('1'))
            onOff2 = "On"
        elif(dustiness < 700 and ppm < 300):
            pBT.write(str.encode('0'))
            onOff2 = "Off"
        
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        
        print(current_time + " " + onOff + " " + str(intput) + " " + onOff2 + " " + str(dustiness) + " " + str(ppm)) #output system status to console
    
    else: #send command to turn off the actuatable devices, as the anchor has left proximity
        hBT.write(str.encode('0'))
        pBT.write(str.encode('0'))
        
    time.sleep(60) #air quality only changes so rapidly in a home, checking once a minute is frequently enough. If you like, you can change seconds waited for update more or less frequently

hBT.close()
pBT.close()
s1BT.close()
s2BT.close()
print("Done")