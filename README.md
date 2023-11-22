## 1. About Us:
The project is being processed by the model experiments group at the IKZ - Leibniz Institut für Kristallzüchtung.
---
## 2. Introduction:
jupiter4852.py allows comunication with the Temperature Calibration Device "Jupiter 4852 Basic" over the RS422/RS232 Port with help of the Modbus Protocoll.
Currently the current temperature can be read and the setpoint can be read and written.

## 3. Useful resources:
__Isotech Jupiter 4852 Basic:__
https://isotech.co.uk/wp-content/uploads/2020/09/BASIC-SITE-Jupiter.pdf

__Comunications Manual between Jupiter 4852 Basic and PC with Modbus__
https://www.eurotherm.com/?wpdmdl=27877

## 5. Hardware setup:
 __The Jupiter 4852 must be connected to the comupter using the official adapter by Isotherm!__
 A RS232 to USB adapter can be used to connect to the computer after the Isoterm adapter.

## 6. Software setup:
### 6.1 Jupiter:

__Comms Resolution "rES" has to be "XX.X °C" not "XX.XX °C" which is used per default.__

__Modbus Address has to be "2" even if Cal Notepad appears to comunicate with "1".__

Assure that default settings are used:
Baudrate: 9600
Parity:   None
bytesize: 8
stopbits: 1
