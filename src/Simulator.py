from math import sin, cos, tan, radians, degrees, sqrt, pi, floor
from copy import copy, deepcopy

from .Vector3d import Vector3d
from .Planet import Earth
from .Orbit import Orbit

class _simulator:
	def __init__(self):
		self.t, self.td = 0, 0.01
		self._fdTemp = 0

		self.rocket = None
		self.simulationTargets = []
		self.limitedTime = 0
		self.planet = Earth
		self.limitedLambda = None

		self.launchPoint = Vector3d(self.planet.radius, 0, 0)

		self.inPhysics = True
		self.isRunning = False

		self.rawCommands = {}

		self.breakPoints = [0]
		self.reportData = []
		self.reportDict = {}

		self.startRecording = False
		self.isRecording = False

	def SetRocket(self, rocket):
		self.rocket = rocket
		self.rocket.location = self.launchPoint
		self.rocket.rotation = self.rocket.location.Normal()
		# self.rocket.Rotate2(azimuth=90, angle=0)
		self.apogee, self.maxSpeed, self.maxQ = {"time":0, "rocket":self.rocket.Snapshot()}, {"time":0, "rocket":self.rocket.Snapshot()}, {"time":0, "rocket":self.rocket.Snapshot()}

		self.limitedTime = self.rocket.BurnTime()
		self._fdTemp = 0.5*rocket.dragEfficient*rocket.area
		### really???
		# rocket.fuelConsumption = rocket.FuelMass() / rocket.BurnTime() * self.td
		# rocket.fuelMaxMass = rocket.FuelMass()
		### really???

		# print(self._fdTemp*self.rocket.speed**2)

	def Report(self):
		### TODO:
		# more pretty reporting system
		str = "Rocket %s" %self.rocket.name
		str += "\nTotal Flight Time :\t\tT+%.2lfs"%self.t
		str += "\nTotal Mass : \t\t\t%.2lfKg"%(self.rocket.TotalMass())
		str += "\nTotal Stages : \t\t\t%d"%(self.rocket.stageCount)

		# for i in self.rocket.stages:
		# 	str += "\n\nSTAGE #%d"%i.number
		# 	str += "\nFuel Mass : \t\t\t%.2lfKg"%i.stageFuelMass()
		# 	str += "\nUsed Fuel Mass : \t\t%.2lfKg"%(i.stageFuelMaxMass() - i.stageFuelMass())
		# 	str += "\nThrust : \t\t\t%.2lfKN"%(i.totalMaxThrust/1000)
		# 	str += "\nBurnTime : \t\t\t%.2lfs"%i.burnTime
		# 	str += "\nFuelConsumption : \t\t%.2lfKg/s"%i.totalFC

		# str += "\n\nAPOGEE"
		# str += "\nlocation : \t\t\t%.2lf %.2lf %.2lfKm"%(self.apogee["rocket"]["location"].x/1000, self.apogee["rocket"]["location"].y/1000, self.apogee["rocket"]["location"].z/1000)
		# str += "\nTime : \t\t\t\tT+%.2lfs"%(self.apogee["time"])
		# str += "\nAcceleration : \t\t\t%.2lfkm/s^2"%(self.apogee["rocket"]["acce"].z/1000)
		# str += "\nSpeed : \t\t\t%.2lf %.2lf %.2lfkm/s"%(self.apogee["rocket"]["velocity"].x/1000, self.apogee["rocket"]["velocity"].y/1000, self.apogee["rocket"]["velocity"].z/1000)
		# # points = self.CalculateOrbit(r1=self.apogee["rocket"]["location"].z, v1=self.apogee["rocket"]["velocity"].VectorSize(), angle=self.apogee["rocket"]["angle"])
		# # print("points at apogee", points)

		# str += "\n\nMAX Q"
		# str += "\nlocation : \t\t\t%.2lf %.2lf %.2lfKm"%(self.maxQ["rocket"]["location"].x/1000, self.maxQ["rocket"]["location"].y/1000, self.maxQ["rocket"]["location"].z/1000)
		# str += "\nTime : \t\t\t\tT+%.2lfs"%(self.maxQ["time"])
		# str += "\nAcceleration : \t\t\t%.2lfkm/s^2"%(self.maxQ["rocket"]["acce"].z/1000)
		# str += "\nSpeed : \t\t\t%.2lf %.2lf %.2lfkm/s"%(self.maxQ["rocket"]["velocity"].x/1000, self.maxQ["rocket"]["velocity"].y/1000, self.maxQ["rocket"]["velocity"].z/1000)

		# str += "\n\nMAX S"
		# str += "\nlocation : \t\t\t%.2lf %.2lf %.2lfKm"%(self.maxSpeed["rocket"]["location"].x/1000, self.maxSpeed["rocket"]["location"].y/1000, self.maxSpeed["rocket"]["location"].z/1000)
		# str += "\nTime : \t\t\t\tT+%.2lfs"%(self.maxSpeed["time"])
		# str += "\nAcceleration : \t\t\t%.2lfkm/s^2"%(self.maxSpeed["rocket"]["acce"].z/1000)
		# str += "\nSpeed : \t\t\t%.2lf %.2lf %.2lfkm/s"%(self.maxSpeed["rocket"]["velocity"].x/1000, self.maxSpeed["rocket"]["velocity"].y/1000, self.maxSpeed["rocket"]["velocity"].z/1000)

		for i, v in enumerate(self.reportData):
			# print(v)
			r = v["rocket"]
			str += "\n\nBREAK POINT #%d"%i
			str += "\nTime : \t\t\t\tT+%.2lfs"%(v["time"])
			str += "\nStage : \t\t\t%d/%d"%(r["stageIndex"], len(r["stages"]))
			str += "\nlocation : \t\t\t%.2lf %.2lf %.2lfKm"%(r["location"].x/1000, r["location"].y/1000, r["location"].z/1000)
			str += "\naltitude : \t\t\t%.2lfKm"%((r["location"].Size() - self.planet.radius)/1000 )
			str += "\nTotal Mass : \t\t\t%.2lfkg"%(r["TotalMass"])
			str += "\nTWR : \t\t\t\t%.2lf / %.2lf"%(r["TWR"], r["possible TWR"])
			str += "\nAcceleration : \t\t\t%.2lf %.2lf %.2lfKm/s^2"%(r["acce"].x/1000, r["acce"].y/1000, r["acce"].z/1000)
			str += "\nRotation : \t\t\t%.2lf %.2lf %.2lf"%(r["rotation"].x, r["rotation"].y, r["rotation"].z)
			str += "\nSpeed : \t\t\t%.2lf %.2lf %.2lfkm/s\t\t%.2lfkm/s"%(r["velocity"].x/1000, r["velocity"].y/1000, r["velocity"].z/1000, r["velocity"].Size()/1000)
			# str += "\nSpeed : \t\t\t%.2lfkm/s"%(r["velocity"].VectorSize()/1000)
			d = Sim.ToPolarCoordinates(r["location"])
			# str += "\nLocation in PC : \t\t%.2lf %.2lf %.2lf"%(d.x, d.y, d.z/1000)

		print(str)

		# if self.orbit:
		# 	self.orbit.Report()

	def RocketForce(self, rocket, idelCutOff=False):
		ad, fd = self.airDensity2(rocket.location.Size()-self.planet.radius), Vector3d(0, 0, 0)
		if ad:
			fd = (-rocket.velocity.Normalize())*self._fdTemp*ad*rocket.velocity.VectorSize()**2

		thrust = rocket.rotation.Normal() * rocket.Thrust()

		### self.planet -> rocket.gravityPlanet
		gravity = (-rocket.location.Normal()) * rocket.TotalMass() * self.planet.Gravity(rocket.location.Size())

		return thrust + gravity + fd

	def Run(self, f=None):
		self.isRunning = True
		while self.isRunning and(not self.limitedTime or (self.t <= self.limitedTime and not self.IsCrash(self.rocket)) or (self.limitedLambda and self.limitedLambda(self))):
			# if self.inPhysics: self.PhysicsStep()
			# else: self.OrbitStep()
			self.rocket.CheckStages(self.t)

			self.ThirdPhysicsStep(self.rocket)

			self.BreakPoints()
			self.Command()

			if f:f(self)
			if self.isRecording:
				self.RocketSnapshot(self.rocket)

			self.t += self.td

		self.RocketSnapshot(self.rocket)

	def ThirdPhysicsStep(self, rocket):
		rocket.force = self.RocketForce(rocket)
		rocket.acce = rocket.force / rocket.TotalMass()
		rocket.velocity += rocket.acce*self.td
		rocket.location += rocket.velocity*self.td

	def BreakPoints(self):
		bpList = [-self.td <= self.t - i <= self.td for i in self.breakPoints]
		if True in bpList:
			self.breakPoints.pop(bpList.index(True))
			self.RocketSnapshot(self.rocket)

	def Command(self):
		keys = list(self.rawCommands.keys())

		cmdList = [-self.td <= self.t - i <= self.td for i in keys]
		if True in cmdList:
			index = cmdList.index(True)
			for cmd in self.rawCommands[keys[index]]:

				if cmd[2] == "seperation":
					cmd[1].Seperate()
				elif cmd[2] == "angle":
					cmd[1].Rotate2(angle=cmd[3])
				elif cmd[2] == "azimuth":
					cmd[1].Rotate2(azimuth=cmd[3])
				elif cmd[2] == "rotate":
					cmd[1].Rotate(x=cmd[3], y=cmd[4], z=cmd[5])
				elif cmd[2] == "ignition":
					cmd[1].Ignition()
				elif cmd[2] == "cutoff":
					cmd[1].CutOff()
				elif cmd[2] == "quit":
					self.isRunning = False
				elif cmd[2] == "SAS on":
					self.rocket.On("SAS")
				elif cmd[2] == "record":
					self.isRecording = True
					self.startRecording = self.t
				elif cmd[2] == "throttle":
					cmd[1].SetThrottle(cmd[3])

			self.rawCommands.pop(keys[index], None)

	def RocketSnapshot(self, rocket):
		data = {
			"time":self.t,
			"rocket":rocket.Snapshot()
		}
		self.reportData.append(data)
		self.reportDict["%.2lf"%self.t] = data

	def Snapshot(self):
		snapshot = {
			"time":self.t,
			"td":self.td,
			"rocket":self.rocket.Snapshot(),
			"simulationTargets":[i.Snapshot() for i in self.simulationTargets],
			"limitedTime":self.limitedTime,
			"planet":self.planet.Snapshot(),
			"inPhysics":self.inPhysics,
			"isRunning":self.isRunning,
			"breakPoints":self.breakPoints
		}

	### Sim should not finished when velocity is 0 and alt is 0
	# Sim should be ended when crashed.
	# need to make crash checker.
	def IsCrash(self, rocket):
		v = (rocket.location.Size() <= 0 and 30 <= rocket.velocity.Size())
		if v:
			print("CRASHEDDD!")
			self.RocketSnapshot(rocket)
		return v

	def AddCommand(self, time, target, command, *args):
		if time not in self.rawCommands:
			self.rawCommands[time] = []

		self.rawCommands[time].append((time, target, command, *args))

	@staticmethod
	def ToPolarCoordinates(location):
		return Vector3d(degrees(location.x/pi/Sim.planet.radius), degrees(location.y/pi/Sim.planet.radius), location.z)

	@staticmethod
	def projectionThrust(thrust, heading, angle):
		v = sin(radians(angle))
		h = cos(radians(angle))
		# print("%.2lf, %.2lf"%(v*thrust, h*thrust))

		x = sin(radians(heading))
		y = cos(radians(heading))

		# print("%.2lf, %.2lf"%(x*h*thrust, y*h*thrust))
		# print(thrust)
		return h*x*thrust, h*y*thrust, v*thrust

	@staticmethod
	def airDensity(alt):
		if alt < 40*1000:
			return 1.22*(0.9)**(alt/1000000)
		else:
			return 0

	@staticmethod
	def airDensity2(alt):
		alt = alt*1000
		p0 = 101.325*1000
		t0 = 288.15
		g = 9.80665
		L = 0.0065
		R = 8.31447
		M = 0.0289644

		p = p0*(1-(L*alt)/t0)**(g*M/R/L)
		return max(floor(p.real), 0)
Sim = _simulator()
