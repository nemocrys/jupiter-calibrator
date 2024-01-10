import warnings
import serial
from modbus_crc import add_crc
import time


class Jupiter:
    def __init__(self, com, bd, stopbits, bytesize, timeout):
        self.com = com
        self.bd = bd
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.timeout = timeout

        self.retrys = 0 # for repeating the setTemperature comand after a fail
        
        self.ser = serial.Serial(self.com,
                     bytesize = self.bytesize,
                     baudrate = self.bd,
                     stopbits = self.stopbits,
                     timeout= self.timeout)
        
        print(f"T_Jupiter = {self.readCurrentTemperature()}°C")
        
        
        
        
    # Returns command string with Cycle Redunency Check (CRC) string at end
    def addCRC(self, command):
        signedCommand = add_crc(command)
        return signedCommand
    
    # send a command to the Jupiter
    # returns the answer from the Jupiter.
    def sendAndReadCommand(self, command):
        signedCommand = self.addCRC(command)
        self.ser.write(signedCommand)
        response1 = self.ser.readline()
        response2 = self.ser.readline() # catch the whole message incase of a "\n" character. this is bad coding, the better soultion would be to calculate the byte length of the response and then read that abound of bytes
        return response1 + response2


    # input: temperature in °C
    # result: Jupiter will now have the input temperature
    def setTemperature(self, temperature):
        temperatureFormated = int(round(temperature*10,1)) # format number, e.g. 32.18 (°C) to 321 (°C)
        
        # temperature is converted to hexstring; "x0" is removed from hexstring; hexstring is interpret as int with base 16; and is converted to binary. easy.
        binaryTemperature = int(hex(temperatureFormated)[2:],16).to_bytes(2, 'big') 
        command = b"\x02\x06\x00\x02" + binaryTemperature
        res = self.sendAndReadCommand(command) # command is send and response is catched to avoid misinterpretation

        # verify that the temperature was changed to desiered temperature. raises error if not.
        if temperatureFormated != int(round(self.readSetpointTemperature()*10,1)):
            if self.retrys >= 3:
                raise Exception(f"""Temperature could not be set. ({self.retrys} retrys).
Temperature send   :{temperatureFormated}
Temperature recived:{int(round(self.readSetpointTemperature()*10,1))}
(Both should be the same 3-digit, base-10 number.)\nCheck if cabels and if settings are correct.""")
            else:
                warnings.warn(f"Temperature could not be set. ({self.retrys} retrys).\nNew try...")
            self.retrys = self.retrys + 1
            self.setTemperature(temperature)
            

    # returns current Temperature of Jupiter in °C
    def readCurrentTemperature(self):
        command = b"\x02\x03\x00\x01\x00\x02\x95\xF8"
        res = self.sendAndReadCommand(command)
        tCurrent = int.from_bytes(res[res.find(b"\x04")+1:-4], "big")/10
        return tCurrent
    
    # returns desiered Temperature / Setpoint (SP) of Jupiter in °C
    def readSetpointTemperature(self):
        command = b"\x02\x03\x00\x01\x00\x02\x95\xF8"
        res = self.sendAndReadCommand(command)
        SP  = int.from_bytes(res[res.find(b"\x04")+3:-2], "big")/10
        return SP
