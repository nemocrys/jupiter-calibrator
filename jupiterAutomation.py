from jupiter4852 import Jupiter

import time
import os
import warnings
import logging
import datetime

# This Script does fully automate the calibration Process of the Jupiter.
# Note that this Script only controlls the Jupiter the sensors have to be controlled with a different script (Multilog)
# The Script stays at the choosen Setpoints (see/edit below) for 25min to 40min to achive stationarity and then continues to the next temperature
# When the Script is finished the Script cools down to 20°C (but does not shutdown the device!)


############### INPUT ###############
temperatureList  = [50,150,250,350,450,550,650] # EDIT SETPOINTS (in °C) HERE!
setpointTimeList = [35, 25, 25, 25, 25, 40, 60] # EDIT WAITTIME (in minutes) FOR EACH TEMPERATURE HERE!
#####################################



# Preperation
## Generate Folder and File
### Generate Folder
date = datetime.datetime.now().strftime("%Y-%m-%d")
for i in range(100):
    if i == 99:
        raise ValueError("Too high directory count.")
    directory = f"./jupiterdata_{date}_#{i+1:02}"
    if not os.path.exists(directory):
        os.makedirs(directory)
        break
        
### calculate runtime
totalTime = 0
for time in setpointTimeList:
    totalTime = totalTime+time
    
logging.basicConfig(level=logging.DEBUG, filename=os.path.join(directory, "log"), filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', datefmt="%d-%b-%y %H:%M:%S")
logging.info("starting log")
logging.info(f"Total Runtime: {round(totalTime/60,1)}h")
print(f"Total Runtime: {round(totalTime/60,1)}h")
logging.debug(f"SetPoints:      {temperatureList} [°C]")
logging.debug(f"Setpoint Times: {setpointTimeList} [min]")

### Generate CSV
with open(os.path.join(directory, "data.csv"), "w", encoding="utf-8") as f: 
    f.write("time_abs,time_rel,time_rel_SP,tTarget,T_cal\n")
logging.info("created Path and Files")

## Init device
try:
    J = Jupiter('/dev/ttyr03', bd = 9600, stopbits = 1, bytesize = 8, timeout = 0.1)
    logging.debug(f"Current Temperature of Jupiter: {J.readCurrentTemperature()} °C")
    logging.info("Jupiter was started")
except:
    logging.critical("Failed to start Jupiter - Abort!")
    raise ConnectionError("No Conection to Jupiter-Device")


# Loop
logging.info("starting measurement")
start_time = datetime.datetime.now(datetime.timezone.utc).astimezone()
for setpointNr in range(len(temperatureList)):
    
    # set new temperature
    targetTemperature = temperatureList[setpointNr]
    J.setTemperature(targetTemperature)
    setpointStartTime = datetime.datetime.now(datetime.timezone.utc).astimezone()
    print(f"{setpointStartTime}: Next Temperature: {targetTemperature}°C")
    
    # Calculate how much time is needed for the setpoint
    setpointTime = setpointTimeList[setpointNr]

    logging.info(f"Next Temperature: {targetTemperature}°C, holding for {setpointTime} min.")

    while True:

        # get times
        time_abs = datetime.datetime.now(datetime.timezone.utc).astimezone()
        time_rel = round((time_abs - start_time).total_seconds(), 3)
        setpointRelTime = round((time_abs - setpointStartTime).total_seconds(), 3)

        currentTemperature = J.readCurrentTemperature()

        # save data
        with open(os.path.join(directory, "data.csv"), "a", encoding="utf-8") as f:
            f.write(f"{time_abs},{time_rel},{setpointRelTime},{targetTemperature},{currentTemperature}\n")

        # abort if script takes to long.
        if time_rel >= 60*60*10:
            J.setTemperature(20)
            logging.critical("Script took longer then 10h. Setpoint was set to 20°C and script was aborted.")
            raise ValueError("Script took longer then 10h. Setpoint was set to 20°C and script was aborted.")
        if setpointRelTime >= 60*60*2:
            J.setTemperature(20)
            logging.critical("Setpoint took longer then 2h. Setpoint was set to 20°C and script was aborted.")
            raise ValueError("Setpoint took longer then 2h. Setpoint was set to 20°C and script was aborted.")

        # check if next setpoint should start
        if setpointRelTime >= setpointTime:
            logging.debug("next checkpoint is triggert.")
            break
        
        #calculate sleep time
        time_abs_end = datetime.datetime.now(datetime.timezone.utc).astimezone()
        calcTime = round((time_abs_end - time_abs).total_seconds(), 3)
        if calcTime < 1:
            time.sleep(1-calcTime)
        else:
            logging.warning(f"Calculation time is larger then sampling time!\nt_calc={calcTime}s")
            warnings.warn(f"Calculation time is larger then sampling time!\nt_calc={calcTime}s")



# cool Device down if finished
J.setTemperature(20)
print(f"{time_abs_end}: Measurement is finished, cooling to Room Temperature!") 
logging.info("Measurement is finished, cooling to Room Temperature!") 
