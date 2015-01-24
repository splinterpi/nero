#! /usr/bin/env python

class MyClass:
    """A simple example class"""
    i = 12345
    def f( self, proc ):
        tens = (((proc/10)%10)*10);
	ones = (proc%10); 
	# print tens
	# print ones 

# Select Tens Display
	if tens < 10: 
		print 'zero'
	if tens == 10:
		print 'ten'
        if tens == 20:
                print 'twenty'
        if tens == 30:
                print 'thirty'

# Select Ones Display
	if ones == 0:
		print 'zero'	
	if ones == 1:
		print 'one'
	if ones == 2:
		print 'two'
	if ones == 3:
		print 'three'
	if ones == 4:
		print 'four'
	if ones == 5:
		print 'five'
	if ones == 6:
		print 'six'
	if ones == 7:
		print 'seven'
	if ones == 8:
		print 'eight'
	if ones == 9:
		print 'nine'

	
x = MyClass()

for i in range(0, 39):
	x.f( i )

