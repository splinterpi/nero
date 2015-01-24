#! /usr/bin/env python

f = open('/home/reesd/temp_data.log','r')
lines = f.readlines()
temp = []
for line in lines:
	temp.append(line.split(	)[2])

temp = map(float, temp)

max = max(temp)
min = min(temp)

print 'min: ',
print min,
print ' C'
print 'max: ',
print max,
print ' C'
