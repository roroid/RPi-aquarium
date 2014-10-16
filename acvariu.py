import thread
import time
import ephem
import datetime
import wiringpi

DELAY_PWM = 0.010
fade_old=0
io = wiringpi.GPIO(wiringpi.GPIO.WPI_MODE_PINS)
buton=0
STEP=1

def reset_pins(io):
    pins = [1,2,3,4,5,6,7, ]
    for pin in pins:
        io.pinMode(pin,io.OUTPUT)
        io.digitalWrite(pin, io.LOW)
    io.pinMode(0,io.INPUT)
    io.pinMode(5,io.INPUT)
reset_pins(io)
def pwm_dimm(io,dela,la,dir):
    pin = 1 # only supported on this pin
    io.pinMode(pin,io.PWM_OUTPUT)

    if dir==1:
	    #sus
	    print 'sus'
	    for i in range(dela,la):
		io.pwmWrite(pin, i+1)
	        time.sleep(DELAY_PWM)
    elif dir==0:
	   #jos
            print 'jos'
	    for i in range(dela,la,-STEP):
		io.pwmWrite(pin, i-1)
	        time.sleep(DELAY_PWM)
def hranitor():
	pin=3
	io.pinMode(pin,io.OUTPUT)
	io.digitalWrite(pin,io.HIGH)
	time.sleep(0.25)
	io.digitalWrite(pin,io.LOW)
def buton():
   prev_input=1
   c=1
   while True:
	input=io.digitalRead(0)
	if ((not prev_input) and input):
	    if (c==1):
		c=0
	        print "apasat1"
	        pwm_dimm(io,fade,1023,1)
	    else:
		c=1
		print "apasat 2"
                pwm_dimm(io,1023,fade,0)

	prev_input=input
	time.sleep(0.05)

def buton1():
   prev_input=1
   c=1
   while True:
	input=io.digitalRead(5)
	if ((not prev_input) and input):
	    hranitor()                
	prev_input=input
	time.sleep(0.05)	
def soarele():
   global fade_old
   global fade
   while True:
	#get current date
	acum=datetime.datetime.now()
	#create 12 hour
	ora_12=acum.replace(hour=12,minute=00,second=00,microsecond=0)
	#add as observer Arad city
	arad=ephem.Observer()
	arad.lat='46.166666700000000000'
	arad.long='21.316666700000040000'
	#computations for SUN
	s=ephem.Sun()
	s.compute()
	#calculate rising and if rising has passed see what was the rising
	rasarit=ephem.localtime(arad.next_rising(s))
	if ora_12.date()<rasarit.date():
		rasarit=ephem.localtime(arad.previous_rising(s))
	#calculate setting and if setting has passed see what was the setting
	apus=ephem.localtime(arad.next_setting(s))
	if ora_12.date()<apus.date():
		apus=ephem.localtime(arad.previous_setting(s))
	#max fade level that needs to be reach till 12
	niv_max=950
	#establish PWM at 0
	fade=0
	#calculate # of intervals from rising to 12o'clock
	tmp=ora_12-rasarit
	fade_in=niv_max/(((tmp.seconds)/60/60)+1)
	#if in below interval calculate PWM
	if rasarit<=acum and acum<=ora_12:
		tmp=ora_12-acum
		ore_r=(((tmp.seconds)/60/60))
		fade=niv_max-(ore_r*fade_in)
	#establis PWM if in interval 12-13 o'clock
	ora_13=ora_12.replace(hour=13,minute=00,second=00,microsecond=0)
	if ora_12<=acum and acum<=ora_13:
		fade=1023
	#calculate # of intervals from 13o'clock to setting
	tmp=apus-ora_12
	fade_out=niv_max/((tmp.seconds)/60/60)
	#if in below interval calculate PWM
	if ora_13<=acum and acum<=apus:
		tmp=acum-ora_13
		ore_r=(((tmp.seconds)/60/60))
		fade=niv_max-(ore_r*fade_out)
	if fade_old!=fade:
		print fade
		if fade_old<fade:
			pwm_dimm(io,fade_old,fade,1)
		else:
			pwm_dimm(io,fade_old,fade,0)
	ora_7=ora_12.replace(hour=7,minute=00,second=00,microsecond=0)
	ora_75=ora_12.replace(hour=7,minute=00,second=06,microsecond=0)
	if ora_7<=acum and acum <=ora_75:
		hranitor()
	ora_18=ora_12.replace(hour=18,minute=00,second=00,microsecond=0)
	ora_185=ora_12.replace(hour=18,minute=00,second=06,microsecond=0)	
	if ora_18<=acum and acum<=ora_185 :
		hranitor()
	fade_old=fade
	time.sleep(2)

# Create thread
try:
   thread.start_new_thread( soarele, () )
   thread.start_new_thread( buton, () )
   thread.start_new_thread( buton1, () )
except Exception, errtxt:
	print errtxt

while 1:
	pass
