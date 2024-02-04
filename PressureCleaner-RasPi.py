#Title: Pressure Clearner Pi/Vex Communication
#Author: Connor Alfonso

#Order of Events
#Wait for Vex to finish positioning Camera
#Take Picture 1: Pre-Wash Picture First surface
#Analyze Picture 1 and add number to dictionary
#Send Signal to Vex to Clean
#Wait for Vex to finish positioning Camera after cleaning
#Take Picture 2: Post-Wash Picture First surface
#Analyze Picture 2 and add number to dictionary
#Compare grayscale
#If decision that surface id clean move right
#Take Picture 3: Pre-Wash Picture Second surface
#Analyze Picture 3 and add number to dictionary
#Send Signal to Vex to Clean
#Wait for Vex to finish positioning Camera after cleaning
#Take Picture 4: Post-Wash Picture Second surface
#Analyze Picture 4 and add number to dictionary

import RPi.GPIO as GPIO
import time
import picamera
import math
from PIL import Image

camera = picamera.PiCamera()
camera.rotation = 90
camera.resolution =(1000, 500)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

VexToPiTakePicture = 13
PiToVexClean = 6
PiToVexMoveRight = 5

GPIO.setup(VexToPiTakePicture, GPIO.IN)
GPIO.setup(PiToVexClean,GPIO.OUT)
GPIO.setup(PiToVexMoveRight,GPIO.OUT)

GPIO.output(PiToVexClean, GPIO.LOW)
GPIO.output(PiToVexMoveRight, GPIO.LOW)

averagesOfSurfaces = {}
user_already_notified = 1

def wait_for_Vex_Signal(signal):
    global user_already_notified
    
    while (GPIO.input(signal) == 0):
        time.sleep(0.5)
        if (user_already_notified == 1):
            user_already_notified = 0
            print("Waiting for Vex.")

def wait_for_Vex_Signal_Off(signal):
    global user_already_notified
    
    while (GPIO.input(signal) != 0):
        time.sleep(0.5)
        if (user_already_notified == 1):
            user_already_notified = 0
            print("Waiting for Vex to turn off signal.")

def analyze_Picture(picture, counter):
    image_file = Image.open(picture)
    image_file = image_file.convert('L')
    image_file.save('/home/pi/Desktop/SurfaceBW%s.jpg' % counter)
    sumOfBrightness = 0
    for i in range(1000):
        for j in range(500):
            sumOfBrightness = sumOfBrightness + image_file.getpixel((i,j))
    avgBrightness = int(sumOfBrightness/500000)
    averagesOfSurfaces["Avg" + str(counter)] = avgBrightness
    print(averagesOfSurfaces)

def send_signal_to_Vex(signal):
    GPIO.output(signal, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(signal, GPIO.LOW)
    
###########################
isItDirty1 = True
isitDirty2 = True

while (isItDirty1):
    wait_for_Vex_Signal(VexToPiTakePicture)
    user_already_notified = 1
    wait_for_Vex_Signal_Off(VexToPiTakePicture)
    user_already_notified = 1
    
    camera.capture('/home/pi/Desktop/Surface1PreWash.jpg')
    analyze_Picture('/home/pi/Desktop/Surface1PreWash.jpg', "Sf1PreWash")
    
    send_signal_to_Vex(PiToVexClean)
    print("Message sent to Vex to Clean")
    wait_for_Vex_Signal(VexToPiTakePicture)                                 
    print("Received message from Vex that Cleaning cycle done")
    camera.capture('/home/pi/Desktop/Surface1PostWash.jpg')
    analyze_Picture('/home/pi/Desktop/Surface1PostWash.jpg', "Sf1PostWash")
    if((averagesOfSurfaces.get('AvgSf1PreWash')) < ((averagesOfSurfaces.get('AvgSf1PostWash'))+10)): 
        isItDirty1 = not(isItDirty1)
        print("Tested Cleaning- Good to Go")
        send_signal_to_Vex(PiToVexMoveRight)
    if((averagesOfSurfaces.get('AvgSf1PreWash')) >= ((averagesOfSurfaces.get('AvgSf1PostWash'))+10)): 
        print("Tested Cleaning- Not Good To Go - Will Clean Again")

while (isItDirty2):
    wait_for_Vex_Signal(VexToPiTakePicture)
    camera.capture('/home/pi/Desktop/Surface2PreWash.jpg')
    analyze_Picture('/home/pi/Desktop/Surface2PreWash.jpg', "Sf2PreWash")
    send_signal_to_Vex(PiToVexClean)
    wait_for_Vex_Signal(VexToPiTakePicture)
    camera.capture('/home/pi/Desktop/Surface2PostWash.jpg')
    analyze_Picture('/home/pi/Desktop/Surface2PostWash.jpg', "Sf2PostWash")
    if((averagesOfSurfaces.get('AvgSf2PreWash')) < ((averagesOfSurfaces.get('AvgSf2PostWash'))+10)): 
        isItDirty2 = not(isItDirty2)
        print("Tested Cleaning- Good to Go")
    if((averagesOfSurfaces.get('AvgSf2PreWash')) >= ((averagesOfSurfaces.get('AvgSf2PostWash'))+10)): 
        print("Tested Cleaning- Not Good To Go - Will Clean Again")


