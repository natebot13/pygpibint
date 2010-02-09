#!/usr/bin/env python
# encoding: utf-8

"""
hp4284.py
Current version development: 0.1
Author: Michael King
Copyright (c) 2009 Vanderbilt University. All rights reserved.
"""

import sys, os
from data_acquisition import vxi_11

class hp4284(vxi_11.vxi_11_connection):
	def __init__(self, host, device="gpib0,17", raise_on_err=1, timeout=180000, device_name="HP 4284A"):
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
	
