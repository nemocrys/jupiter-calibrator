from jupiter4852 import Jupiter

J = Jupiter('/dev/ttyr03', bd = 9600, stopbits = 1, bytesize = 8, timeout= 0.1)

J.setTemperature(34.56)
tCurrent = J.readCurrentTemperature()
tTarget  = J.readTargetTemperature()

print(tCurrent) # should be the current temperature of the Jupiter
print(tTarget)  # should be 34.56
