'''
GUI for measuring Relative Humidity using HS-1101 Sensor

ExpEYES program developed as a part of GSoC-2015 project
Project Tilte: Sensor Plug-ins, Add-on devices and GUI Improvements for ExpEYES

Mentor Organization:FOSSASIA
Mentors: Hong Phuc, Mario Behling, Rebentisch
Author: Praveen Patil
License : GNU GPL version 3
'''


'''
For Calculations this data sheet is used:
https://www.parallax.com/sites/default/files/downloads/27920-Humidity-Sensor-Datasheet.pdf

Slope of the curve and y-intercept is determined for 4 different linear sections of the response curve 
given in the data sheet using

y=mx+c 		Here y is capacity ( cap) in pF and x is relative humidity (RH) in % and c is y-intercept
m = dy/dx
c =y-mx
and 
x= (y-c)/m

For Humidity 0% to 50%
c= 163 in pF
m = 0.3

For Humidity 50% to 70%
c= 160.25 in pF
m = 0.375

For Humidity 70% to 90%
c= 156.75 in pF
m = 0.425

For Humidity 90% to 100%
c= 136.5 in pF
m = 0.65
'''


#connect HS1011 between IN1 and GND

import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

from Tkinter import *
import time, math, sys
if sys.version_info.major==3:
        from tkinter import *
else:
        from Tkinter import *

sys.path=[".."] + sys.path


import expeyes.eyesj as eyes
import expeyes.eyeplot as eyeplot
import expeyes.eyemath as eyemath

WIDTH  = 600   # width of drawing canvas
HEIGHT = 400   # height    

class humidity:
	tv = [ [], [], [] ]			# Lists for Readings
	TIMER = 2000				# Time interval between reads
	MINY = 0				# Humidity Range
	MAXY = 250
	running = False
				
	def start(self):
		self.running = True
		self.index = 0
		self.tv = [ [], [], [] ]
		
		try:
			self.MAXTIME = int(DURATION.get())
			
			g.setWorld(0, self.MINY, self.MAXTIME, self.MAXY,_('Time in second'),_('C & RH '))
			self.TIMER = int(TGAP.get())
			Total.config(state=DISABLED)
			Dur.config(state=DISABLED)
			self.msg(_('Starting the Measurements'))
			root.after(self.TIMER, self.update)
		except:
			self.msg(_('Failed to Start'))

	def stop(self):
		self.running = False
		Total.config(state=NORMAL)
		Dur.config(state=NORMAL)
		self.msg(_('User Stopped the measurements'))

	def update(self):
		if self.running == False:
			return
		t,v = p.get_voltage_time(3)  # Read IN1 for time
		if len(self.tv[0]) == 0:
			self.start_time = t
			elapsed = 0
		else:
			elapsed = t - self.start_time
		self.tv[0].append(elapsed)
		
		cap = p.measure_cap()
		self.tv[1].append(cap)
		
		if cap< 180: 
         		RH= (cap -163)/0.3
		elif 180<cap<186: 
        		RH= (cap -160.25)/0.375
		elif 186<cap<195: 
        		RH= (cap -156.75)/0.425
		else:
			RH= (cap -136.5)/0.65


		self.tv[2].append(RH)
		if len(self.tv[0]) >= 2:
			g.delete_lines()
			
			g.line(self.tv[0], self.tv[1],1)    # red line - Capacity in pF
			g.line(self.tv[0], self.tv[2],2)	# blue line - Relative Humidity in %
		if elapsed > self.MAXTIME:
			self.running = False
			Total.config(state=NORMAL)
			Dur.config(state=NORMAL)
			self.msg(_('Completed the Measurements'))
			return 
		root.after(self.TIMER, self.update)

	
	def save(self):
		try:
			fn = filename.get()
		except:
			fn = 'Humidiy.dat'
		p.save([self.tv],fn)
		self.msg(_('Data saved to %s')%fn)

	def clear(self):
		if self.running == True:
			return
		self.nt = [ [], [] ]
		g.delete_lines()
		self.msg(_('Cleared Data and Trace'))

	def msg(self,s, col = 'blue'):
		msgwin.config(text=s, fg=col)

	def quit(self):
		#p.set_state(10,0)
		sys.exit()

p = eyes.open()
p.disable_actions()

root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  

g = eyeplot.graph(root, width=WIDTH, height=HEIGHT, bip=False)
pt = humidity()

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

b3 = Label(cf, text = _('Read Every'))
b3.pack(side = LEFT, anchor = SW)
TGAP = StringVar()
Dur =Entry(cf, width=5, bg = 'white', textvariable = TGAP)
TGAP.set('2000')
Dur.pack(side = LEFT, anchor = SW)
b3 = Label(cf, text = _('mS,'))
b3.pack(side = LEFT, anchor = SW)
b3 = Label(cf, text = _('for total'))
b3.pack(side = LEFT, anchor = SW)
DURATION = StringVar()
Total =Entry(cf, width=5, bg = 'white', textvariable = DURATION)
DURATION.set('100')
Total.pack(side = LEFT, anchor = SW)
b3 = Label(cf, text = _('Seconds.'))
b3.pack(side = LEFT, anchor = SW)


b3 = Button(cf, text = _('SAVE to'), command = pt.save)
b3.pack(side = LEFT, anchor = N)
#b3.pack(side = LEFT, anchor = SW)
filename = StringVar()
e1 =Entry(cf, width=15, bg = 'white', textvariable = filename)
filename.set('Humidity.dat')
e1.pack(side = RIGHT, anchor = SW)

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)


cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)
e1.pack(side = LEFT)


b3 = Label(cf, text = _('   RED Line - Capacity in pF'), fg = 'red')
b3.pack(side = LEFT, anchor = SW)
b3 = Label(cf, text = _('    BLUE Line - Relative Humidity in %.'), fg = 'blue')
b3.pack(side = LEFT, anchor = SW)

b5 = Button(cf, text = _('QUIT'), command = pt.quit)
b5.pack(side = RIGHT, anchor = N)
b4 = Button(cf, text = _('CLEAR'), command = pt.clear)
b4.pack(side = RIGHT, anchor = N)
b1 = Button(cf, text = _('STOP'), command = pt.stop)
b1.pack(side = RIGHT, anchor = N)
b1 = Button(cf, text = _('START'), command = pt.start)
b1.pack(side = RIGHT, anchor = N)

mf = Frame(root, width = WIDTH, height = 10)
mf.pack(side=TOP)
msgwin = Label(mf,text=_('Message'), fg = 'blue')
msgwin.pack(side=LEFT, anchor = S, fill=BOTH, expand=1)

root.title(_('Relative Humidity using HS-1101 sensor'))
root.mainloop()
