#!/usr/bin/env python
# encoding: utf-8

"""
hp.py
Current version development: 0.2
Author: Michael King
Copyright (c) 2009 Vanderbilt University. All rights reserved.
"""

# TODO debug the errors which occur during runtime. (They don't seem to be show-stopping, but are of concern for completeness.)

import sys, os
from data_acquisition import vxi_11

class hp4156(vxi_11.vxi_11_connection):
	def __init__(self, host, device="gpib0,17", raise_on_err=1, timeout=180000, device_name="HP 4156A"):
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
	
	def measurementMode(self, measurementMode, integrationTime):
		"""
		arg1 is the measurement mode. Valid arguements are Sweep = SWE, Sampling = SAMP, Quasi-static CV measurement = QSCV.
		
		arg2 is the integration time. Valid arguments are short = SHOR, medium = MED, long = LONG.
		"""
		if (measurementMode == "SWE" or measurementMode == "SAMP" or measurementMode == "QSCV") and (integrationTime == "SHOR" or integrationTime == "LONG" or integrationTime == "MED"):
			self.write(":PAGE:CHAN:MODE " + measurementMode)
			self.write(":PAGE:MEAS:MSET:ITIM " + integrationTime)
		else:
			print "Invalid measurement mode or integration time. Exiting."
			sys.exit()
		pass
	
	def smu(self, smu, vname, func, iname, mode, value, compliance):
		"""
		Defines parameters for setting up an SMU on the HP 4156A. 
		
		arg1 is the desired SMU, ie SMU1, SMU2, etc, entered as a string variable. 
		
		arg2 is the parameters for that SMU. ie smu1 = ['VD','CONS','ID','V','0.1','3mA'] # Variable NAME, Variable FUNCtion(var, cons), INAME, MODE (V, I or COMMon), if the variable is constant this requires a value CONStant ,COMPliance for the variable. Where each element is described after the #.
		"""
		self.vname=self.varStringMod(vname)
		self.iname=self.varStringMod(iname)
		self.write(":PAGE:CHAN:%s:VNAME %s" % (smu, self.vname))
		self.write(":PAGE:CHAN:%s:FUNC %s" % (smu, func))
		self.write(":PAGE:CHAN:%s:INAME %s" % (smu, self.iname))
		self.write(":PAGE:CHAN:%s:MODE %s" % (smu, mode))
		if func != "VAR1" and func != "VAR2" and mode != "COMM" and func != "VAR1\'":
			self.write(":PAGE:MEAS:CONS:%s %s" % (smu, value))
			self.write(":PAGE:MEAS:CONS:%s:COMP %s" % (smu, compliance))
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
		arg = "'" + arg + "'"
		return arg
	
	def var(self, vname, spacing, startVal, stepSize, finalVal, compliance, points=0.0):
		"""
		Describes the measurement parameters for an independent variable, arg1, and its specifications arg2. 
		
		Similar to smu(), we have arg1 as the desired VAR, ie VAR1, VAR2, as a string input. If using VAR2, stop is replaced by number of points.
		
		arg2 describes several critical values of the VAR, ie var1 = ['\'LIN\'','-0.1','0.01','1.5','1nA']	# SPACing (LINear or LOGarithmic), STARting value, STEP size, STOPing value, COMPliance limit.
		"""
		self.spacing = self.varStringMod(spacing)#Check
		if arg1 == "VAR1":
			self.write(":PAGE:MEAS:%s:SPAC %s" % (vname, self.spacing))
			self.write(":PAGE:MEAS:%s:STAR %s" % (vname, startVal))
			self.write(":PAGE:MEAS:%s:STEP %s" % (vname, stepSize))
			self.write(":PAGE:MEAS:%s:STOP %s" % (vname, finalVal))
			self.write(":PAGE:MEAS:%s:COMP %s" % (vname, compliance))
			
		elif arg1 == "VAR2":
			self.write(":PAGE:MEAS:%s:SPAC %s" % (vname, self.spacing))
			self.write(":PAGE:MEAS:%s:STAR %s" % (vname, startVal))
			self.write(":PAGE:MEAS:%s:POIN %s" % (vname, points))
			self.write(":PAGE:MEAS:%s:STEP %s" % (vname, stepSize))
			self.write(":PAGE:MEAS:%s:COMP %s" % (vname, compliance))
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
		self.write("*OPC?")
		pass
	
	def visualizeTwoYs(self, xname, xscal, xmin, xmax, y1name, y1scal, y1min, y1max, y2name, y2scal, y2min, y2max):
		"""
		Takes three list arguments ie:
		
		#x = ['XVAR','LIN',"XMIN","XMAX"]
		#y1 = ['Y1VAR','LOG',"Y1MIN","Y1MAX"]
		#y2 = ['Y2VAR','LOG',"Y2MIN","Y2MAX"]
		
		Visualizes two sets of data, y1 and y2.
		"""
		self.xname = self.varStringMod(xname)#check
		self.y1name = self.varStringMod(y1name)#check
		self.y2name = self.varStringMod(y2name)#check
		self.write(":PAGE:DISP:GRAP:GRID ON")
		self.write(":PAGE:DISP:GRAP:X:NAME %s" % self.xname)
		self.write(":PAGE:DISP:GRAP:Y1:NAME %s" % self.y1name)
		self.write(":PAGE:DISP:GRAP:Y2:NAME %s" % self.y2name)
		self.write(":PAGE:DISP:GRAP:X:SCAL %s" % xscal)
		self.write(":PAGE:DISP:GRAP:Y1:SCAL %s" % y1scal)
		self.write(":PAGE:DISP:GRAP:Y2:SCAL %s" % y2scal)
		self.write(":PAGE:DISP:GRAP:X:MIN %s" % xmin)
		self.write(":PAGE:DISP:GRAP:Y1:MIN %s" % y1min)
		self.write(":PAGE:DISP:GRAP:Y2:MIN %s" % y2min)
		self.write(":PAGE:DISP:GRAP:X:MAX %s" % xmax)
		self.write(":PAGE:DISP:GRAP:Y1:MAX %s" % y1max)
		self.write(":PAGE:DISP:GRAP:Y2:MAX %s" % y2max)
		pass
	
	def visualize(self, xname, xscal, xmin, xmax, yname, yscal, ymin, ymax):
		"""
		Takes two list arguments ie:
		
		x = ['XVAR','LIN',"XMIN","XMAX"]
		y1 = ['Y1VAR','LOG',"Y1MIN","Y1MAX"]
		
		Visualizes a set of data, y1.
		"""
		self.xname = self.varStringMod(xname)#check
		self.yname = self.varStringMod(yname)#check
		self.write(":PAGE:DISP:GRAP:GRID ON")
		self.write(":PAGE:DISP:GRAP:X:NAME %s" % self.xname)
		self.write(":PAGE:DISP:GRAP:Y1:NAME %s" % self.yname)
		self.write(":PAGE:DISP:GRAP:X:SCAL %s" % xscal)
		self.write(":PAGE:DISP:GRAP:Y1:SCAL %s" % yscal)
		self.write(":PAGE:DISP:GRAP:X:MIN %s" % xmin)
		self.write(":PAGE:DISP:GRAP:Y1:MIN %s" % ymin)
		self.write(":PAGE:DISP:GRAP:X:MAX %s" % xmax)
		self.write(":PAGE:DISP:GRAP:Y1:MAX %s" % ymax)
		pass
	
	def abort(self):
		pass
	
	def stress(self, term, func, mode, name, value=0.0, duration=100000):
		"""Sets up the stress conditions for the 4156."""
		self.name=self.varStringMod(name)#check
		self.write(":PAGE:STR:SET:DUR %s" % duration)
		self.write(":PAGE:STR:%s:NAME %s" % (term,self.name))
		self.write(":PAGE:STR:%s:FUNC %s" % (term,func))
		self.write(":PAGE:STR:%s:MODE %s" % (term,mode))
		self.write(":PAGE:STR:SET:CONS:%s %s" % (term,value))
		pass
	
