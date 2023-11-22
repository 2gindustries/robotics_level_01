import RPi.GPIO as GPIO
import time
import numpy as np
import pickle
import warnings

warnings.filterwarnings(action='ignore', category=UserWarning)

ledPin = 11   # ledPin
trigPin = 16
echoPin = 18
MAX_DISTANCE = 220
timeOut = MAX_DISTANCE*60
        
def pulseIn(pin,level,timeOut):
    """
    Obtain pulse time of a pin under timeOut
    """

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
    
def getSonar():
    """
    Get the measurement results of ultrasonic module,with unit: cm
    """

    GPIO.output(trigPin,GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(trigPin,GPIO.LOW)
    pingTime = pulseIn(echoPin,GPIO.HIGH,timeOut)
    distance = pingTime * 340.0 / 2.0 / 10000.0
    return distance
    
def setup():
    """
    Setup of the different pins
    """

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
        predicted_value = 10
        if len(last_five_distances) > 5:
            last_five_distances.pop(0)  # Remove the oldest distance value
        print(last_five_distances)
        if len(last_five_distances) == 5:
            data_to_predict = np.array([last_five_distances])

            # Prediction
            predicted_value = loaded_model.predict(data_to_predict)
            print("Predicted value:" , predicted_value)
        if predicted_value <  10:
            GPIO.output(ledPin, GPIO.HIGH)
        else:
            GPIO.output(ledPin, GPIO.LOW)
        print ("The distance is : %.2f cm"%(distance))
        time.sleep(1)

# We load the model made in ml_model.ipynb
with open('data/linear_regression_model.pkl', 'rb') as file:
    loaded_model = pickle.load(file)

if __name__ == '__main__':
    GPIO.cleanup()
    print ('Program is starting...')
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        GPIO.cleanup()
