#!/usr/bin/env python
# encoding: utf-8

"""
hp4156.py
Current version development: 0.2
Author: Michael King
Copyright (c) 2009 Vanderbilt University. All rights reserved.
"""

# TODO debug the errors which occur during runtime. (They don't seem to be show-stopping, but are of concern for completeness.)

import sys, os
from data_acquisition import vxi_11

class hp4156(vxi_11.vxi_11_connection):
	def __init__(self, host, device="gpib0,17", raise_on_err=1, timeout=180000,device_name="HP 4156A"):
		"""
		Initiates a connection to host ip address, which is a string argument given to hp4156. ie x = hp4156("127.0.0.1"). 
		
		Standard configuration for gpib is declared and initialized on instantiation of the class. It may be necessary to confirm these setting for the parameter analyzer if there are problems connecting to the equipment.
		"""
		vxi_11.vxi_11_connection.__init__(self, host=host, device=device, raise_on_err=raise_on_err, timeout=timeout, device_name=device_name)
		self.write(":FORM:DATA ASCii")
		pass
	
	def reset(self):
		"""Resets configuration of HP 4156A to default."""
		self.write("*rst")
		pass
	
	def measurementMode(self, arg1, arg2):
		"""
		arg1 is the measurement mode. Valid arguements are Sweep = SWE, Sampling = SAMP, Quasi-static CV measurement = QSCV.
		
		arg2 is the integration time. Valid arguments are short = SHOR, medium = MED, long = LONG.
		"""
		if (arg1 == "SWE" or arg1 == "SAMP" or arg1 == "QSCV") and (arg2 == "SHOR" or arg2 == "LONG" or arg2 == "MED"):
			self.write(":PAGE:CHAN:MODE " + arg1)
			self.write(":PAGE:MEAS:MSET:ITIM " + arg2)
		else:
			print "Invalid measurement mode or integration time. Exiting."
			sys.exit()
		pass
	
	def stringSmuMod(self, arg):
		"""
		Method only called when appropriate, users don't need to modify their input. Generally I will know when it is appropriate to do this and do so accordingly.
		"""
		arg[0] = "'" + arg[0] + "'"
		arg[2] = "'" + arg[2] + "'"
		return arg
	
	def smu(self, arg1, arg2):
		"""
		Defines parameters for setting up an SMU on the HP 4156A. 
		
		arg1 is the desired SMU, ie SMU1, SMU2, etc, entered as a string variable. 
		
		arg2 is the parameters for that SMU. ie smu1 = ['VD','CONS','ID','V','0.1','3mA'] # Variable NAME, Variable FUNCtion(var, cons), INAME, MODE (V, I or COMMon), if the variable is constant this requires a value CONStant ,COMPliance for the variable. Where each element is described after the #.
		"""
		self.arg2 = self.stringSmuMod(arg2)
		self.smuSetup = [":PAGE:CHAN:"+arg1+":VNAME %s",":PAGE:CHAN:"+arg1+":FUNC %s",":PAGE:CHAN:"+arg1+":INAME %s", ":PAGE:CHAN:"+arg1+":MODE %s", ":PAGE:MEAS:CONS:"+ arg1 + " %s",":PAGE:MEAS:CONS:" + arg1 + ":COMP %s"]
		self.write(self.smuSetup[0] % self.arg2[0])
		self.write(self.smuSetup[1] % self.arg2[1])
		self.write(self.smuSetup[2] % self.arg2[2])
		self.write(self.smuSetup[3] % self.arg2[3])
		if arg2[1] != "VAR1" and arg2[1] != "VAR2" and arg2[3] != "COMM" and arg2[1] != "VAR1\'":
			self.write(self.smuSetup[4] % arg2[4])
			self.write(self.smuSetup[5] % arg2[5])
		pass
		
	def disableSmu(self, arg):
		"""
		Disables the specified unit: valid arguments are: VSU1, VSU2, VMU1, VMU2, SMU1, SMU2, SMU3, SMU4. Parameter arg is a list of valid arguements.
		"""
		for i in arg:
			self.write(":PAGE:CHAN:" + i + ":DIS")
		pass
	
	def varStringMod(self, arg):
		"""
		Method only called when appropriate, users don't need to modify their input. Generally I will know when it is appropriate to do this and do so accordingly.
		"""
		arg[0] = "'" + arg[0] + "'"
		return arg
	
	def var(self, arg1, arg2):
		"""
		Describes the measurement parameters for an independent variable, arg1, and its specifications arg2. 
		
		Similar to smu(), we have arg1 as the desired VAR, ie VAR1, VAR2, as a string input. If using VAR2, stop is replaced by number of points.
		
		arg2 describes several critical values of the VAR, ie var1 = ['\'LIN\'','-0.1','0.01','1.5','1nA']	# SPACing (LINear or LOGarithmic), STARting value, STEP size, STOPing value, COMPliance limit.
		"""
		self.arg2 = self.varStringMod(arg2)
		self.string = ":PAGE:MEAS:" + arg1 + ":"
		if arg1 == "VAR1":
			self.write(self.string + "SPAC %s" % self.arg2[0])
			self.write(self.string + "STAR %s" % self.arg2[1])
			self.write(self.string + "STEP %s" % self.arg2[2])
			self.write(self.string + "STOP %s" % self.arg2[3])
			self.write(self.string + "COMP %s" % self.arg2[4])
			
		elif arg1 == "VAR2":
			self.write(self.string + "SPAC %s" % self.arg2[0])
			self.write(self.string + "STAR %s" % self.arg2[1])
			self.write(self.string + "POIN %s" % self.arg2[3])
			self.write(self.string + "STEP %s" % self.arg2[2])
			self.write(self.string + "COMP %s" % self.arg2[4])
		pass
	
	def daqStringMod(self, arg):
		"""
		Method only called when appropriate, users don't need to modify their input. Generally I will know when it is appropriate to do this and do so accordingly.
		"""
		self.stuff = []
		for i in arg:
			self.stuff.append("\'" + i + "\'")
		return self.stuff
	
	def daq(self, arg):
		"""
		Queries the HP 4156A for data for specified data, and returns the data to an object.	
		
		arg is intended to be a object (tuple/list) of strings containing data of interest to the operator. example usage:
		arg = ('VD','VS','VG','ID','IS','IG')
		myData = daq(arg)
		"""
		self.argData = []
		self.stuff = self.daqStringMod(arg) # Fix this
		for i in self.stuff:
			self.write(":DATA? %s" % i)
			self.fluff = self.read()
			self.argData.append(self.fluff[2:])
		return self.argData
	
	def single(self):
		"""Performs a single sweep/measurement/thing."""
		self.write(":PAGE:SCON:SING")
		self.write("*WAI?")
		pass
	
	def visualizeTwoYs(self, x, y1, y2):
		"""
		Takes three list arguments ie:
		
		#x = ['XVAR','LIN',"XMIN","XMAX"]
		#y1 = ['Y1VAR','LOG',"Y1MIN","Y1MAX"]
		#y2 = ['Y2VAR','LOG',"Y2MIN","Y2MAX"]
		
		Visualizes two sets of data, y1 and y2.
		"""
		self.x = self.varStringMod(x)
		self.y1 = self.varStringMod(y1)
		self.y2 = self.varStringMod(y2)
		self.write(":PAGE:DISP:GRAP:GRID ON")
		self.write(":PAGE:DISP:GRAP:X:NAME %s" % self.x[0])
		self.write(":PAGE:DISP:GRAP:Y1:NAME %s" % self.y1[0])
		self.write(":PAGE:DISP:GRAP:Y2:NAME %s" % self.y2[0])
		self.write(":PAGE:DISP:GRAP:X:SCAL %s" % self.x[1])
		self.write(":PAGE:DISP:GRAP:Y1:SCAL %s" % self.y1[1])
		self.write(":PAGE:DISP:GRAP:Y2:SCAL %s" % self.y2[1])
		self.write(":PAGE:DISP:GRAP:X:MIN %s" % self.x[2])
		self.write(":PAGE:DISP:GRAP:Y1:MIN %s" % self.y1[2])
		self.write(":PAGE:DISP:GRAP:Y2:MIN %s" % self.y2[2])
		self.write(":PAGE:DISP:GRAP:X:MAX %s" % self.x[3])
		self.write(":PAGE:DISP:GRAP:Y1:MAX %s" % self.y1[3])
		self.write(":PAGE:DISP:GRAP:Y2:MAX %s" % self.y2[3])
		pass
	
	def visualize(self, x, y1):
		"""
		Takes two list arguments ie:
		
		x = ['XVAR','LIN',"XMIN","XMAX"]
		y1 = ['Y1VAR','LOG',"Y1MIN","Y1MAX"]
		
		Visualizes a set of data, y1.
		"""
		self.x = self.varStringMod(x)
		self.y1 = self.varStringMod(y1)
		self.write(":PAGE:DISP:GRAP:GRID ON")
		self.write(":PAGE:DISP:GRAP:X:NAME %s" % self.x[0])
		self.write(":PAGE:DISP:GRAP:Y1:NAME %s" % self.y1[0])
		self.write(":PAGE:DISP:GRAP:X:SCAL %s" % self.x[1])
		self.write(":PAGE:DISP:GRAP:Y1:SCAL %s" % self.y1[1])
		self.write(":PAGE:DISP:GRAP:X:MIN %s" % self.x[2])
		self.write(":PAGE:DISP:GRAP:Y1:MIN %s" % self.y1[2])
		self.write(":PAGE:DISP:GRAP:X:MAX %s" % self.x[3])
		self.write(":PAGE:DISP:GRAP:Y1:MAX %s" % self.y1[3])
		pass
	
	def abort(self):
		pass
	
	def stress(self, term, func, mode, name, value=0.0, duration=100000):
		"""Sets up the stress conditions for the 4156."""
		self.name=self.varStringMod(name)
		self.write(":PAGE:STR:SET:DUR %s" % duration)
		self.write(":PAGE:STR:%s:NAME %s" % (term,self.name))
		self.write(":PAGE:STR:%s:FUNC %s" % (term,func))
		self.write(":PAGE:STR:%s:MODE %s" % (term,mode))
		self.write(":PAGE:STR:SET:CONS:%s %s" % (term,value))
		pass
	
