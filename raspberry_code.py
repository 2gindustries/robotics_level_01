import RPi.GPIO as GPIO
import time
import pandas as pd
import numpy as np
import pickle
from sklearn.exceptions import DataConversionWarning
import warnings

warnings.filterwarnings(action='ignore', category=UserWarning)

ledPin = 11    # define ledPin
trigPin = 16
echoPin = 18
MAX_DISTANCE = 220          # define the maximum measuring distance, unit: cm
timeOut = MAX_DISTANCE*60   # calculate timeout according to the maximum measuring distance
        
def pulseIn(pin,level,timeOut): # obtain pulse time of a pin under timeOut
    t0 = time.time()
    while(GPIO.input(pin) != level):
        if((time.time() - t0) > timeOut*0.000001):
            return 0;
    t0 = time.time()
    while(GPIO.input(pin) == level):
        if((time.time() - t0) > timeOut*0.000001):
            return 0;
    pulseTime = (time.time() - t0)*1000000
    return pulseTime
    
def getSonar():     # get the measurement results of ultrasonic module,with unit: cm
    GPIO.output(trigPin,GPIO.HIGH)      # make trigPin output 10us HIGH level 
    time.sleep(0.00001)     # 10us
    GPIO.output(trigPin,GPIO.LOW) # make trigPin output LOW level 
    pingTime = pulseIn(echoPin,GPIO.HIGH,timeOut)   # read plus time of echoPin
    distance = pingTime * 340.0 / 2.0 / 10000.0     # calculate distance with sound speed 340m/s 
    return distance
    
def setup():
    GPIO.setmode(GPIO.BOARD)       # use PHYSICAL GPIO Numbering
    GPIO.setup(ledPin, GPIO.OUT)   # set the ledPin to OUTPUT mode
    GPIO.output(ledPin, GPIO.LOW)  # make ledPin output LOW level
    GPIO.setup(trigPin, GPIO.OUT)   # set trigPin to OUTPUT mode
    GPIO.setup(echoPin, GPIO.IN)    # set echoPin to INPUT mode

def loop():
    last_five_distances = []
    while(True):
        distance = getSonar() # get distance
        last_five_distances.append(distance)
        predicted_value = 0
        if len(last_five_distances) > 5:
            last_five_distances.pop(0)  # Remove the oldest distance value
        print(last_five_distances)
        if len(last_five_distances) == 5:
            data_to_predict = np.array([last_five_distances])

            # Make a prediction
            predicted_value = loaded_model.predict(data_to_predict)
            print("Predicted value:" , predicted_value)
        if predicted_value <  10:
            GPIO.output(ledPin, GPIO.HIGH)
        else:
            GPIO.output(ledPin, GPIO.LOW)
        print ("The distance is : %.2f cm"%(distance))
        time.sleep(1)

with open('data/linear_regression_model.pkl', 'rb') as file:
    loaded_model = pickle.load(file)

if __name__ == '__main__':     # Program entrance
    GPIO.cleanup()
    print ('Program is starting...')
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        GPIO.cleanup()         # release GPIO resource
