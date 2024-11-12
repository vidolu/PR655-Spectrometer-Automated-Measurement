import serial
import time
import os

import RPi.GPIO as GPIO

STEP = 20    # define Step Pin
DIR = 21     # define Direction Pin
CW = 1
CCW = 0
SPR = 200    #Motor SPR    

MICRO = 1/16    #Microstep Configuration
RATIO = 7.2     #Gear Ratio

stepCount = int(SPR*RATIO/MICRO)
delay = 0.005*MICRO

REVOLUTIONS = 0.01 #Number of Revolutions to Execute

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)       # use BCM GPIO Numbering
    GPIO.setup(STEP, GPIO.OUT)
    GPIO.setup(DIR, GPIO.OUT)
    GPIO.output(DIR, CW)  # Direction Clockwise

def loop():
    state = GPIO.input(DIR)
    for x in range(stepCount):
	    GPIO.output(STEP, GPIO.HIGH)
	    sleep(delay)
	    GPIO.output(STEP, GPIO.LOW)
	    sleep(delay)
	
    time.sleep(1.5)
	
    if state:
	    GPIO.output(DIR, CCW)
    else:
	    GPIO.output(DIR, CW)

def step():
    state = GPIO.input(DIR)
    for x in range(int(1/MICRO)):
	    GPIO.output(STEP, GPIO.HIGH)
	    time.sleep(delay)
	    GPIO.output(STEP, GPIO.LOW)
	    time.sleep(delay)

def destroy():
    GPIO.cleanup()
    

# PR655_init(serial.Serial) - Initialize PR655 to remote mode after cleanup 
#   returns True/False if initialization succeeds/fails
def PR655_init(PR655):
    # Clean Serial Read
    PR655.reset_input_buffer()
    reset = False
    while not reset:

        serialReset = PR655.readline()
        print(serialReset.decode("Ascii").rstrip("\n") + "...CLEANING UP")

        for char in b'Q\r':
            PR655.write(bytes([char]))

        if serialReset == b'':
            print(" CLEAN COMPLETE")
            reset = True

    time.sleep(5)

    # Enable REMOTE MODE
    for char in b'PHOTO':
        PR655.write(bytes([char]))

    time.sleep(2)

    serialIni = PR655.readline()
    if "REMOTE MODE" not in serialIni.decode("Ascii"):
        print("FAILED TO ENABLE.")
        return False

    else:
        # Enable Full Duplex
        print(serialIni.decode("Ascii") + " ENABLED...")
        for char in b'E\r':
            PR655.write(bytes([char]))
        return True

# PR655_spectral(serial.Serial) - Collect Spectral measurement PR655 
def PR655_spectral(PR655, name):
    # File Open
    directory = os.getcwd() + "/data"
    filename = name + ".txt"
    filepath = os.path.join(directory, filename)

    os.makedirs(directory, exist_ok=True)
    f = open(filepath, "a")

    #PR655 OUTPUT
    done = False
    getReading = True
    while not done:
        # Take a spectral measurement
        if getReading:
            for char in b'M5\r':
                PR655.write(bytes([char]))
            getReading = False
        # Read data out of the buffer until a carraige return / new line is found
        serialString = PR655.readline()
        # Print the contents of the serial data
        try:
            if not serialString == b'' :
                f.write(serialString.rstrip(b'\n').decode("Ascii"))
        except:
            pass
        if serialString == b'>':
            done = True

    # File Close
    f.close()
    print(filepath)

def main():
    try:
        # Determine the script's directory
        script_directory = os.path.dirname(os.path.abspath(__file__))
        log_file_path = os.path.join(script_directory, 'timing_log.txt')
    
    
    
        # Record the start time
        start_time = time.time()
    
        #Setup Motor Config
        setup()
    
        #Start serial connection
        PR655 = serial.Serial(port="/dev/ttyACM0", baudrate=9600, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
        fileNum = 0

        #Initialize PR655, take measurement if successful
        if PR655_init(PR655):
            dataPoints = int(stepCount*REVOLUTIONS*MICRO)
            print(f"{dataPoints} Data Points \n")
            for x in range(dataPoints):
                progress = float(x/dataPoints)
                time.sleep(2)
                PR655_spectral(PR655, "step_" + str(fileNum))
                fileNum += 1
                step()
                print(f"In Progress...{progress:.2%}")
    
        # Record the end time
        end_time = time.time()

        # Calculate the elapsed time
        elapsed_time = end_time - start_time
    
        print(f"Elapsed time: {elapsed_time} seconds")
    
        f = open(log_file_path, "a")
        f.write(f"Elapsed time: {elapsed_time} seconds")
        f.close()
    
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be executed.
        destroy()

if __name__ == "__main__":
    main()
