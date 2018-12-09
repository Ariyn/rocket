import math
from copy import copy

from .Simulator import Sim
from .Vector3d import Vector3d
from .Decorators import Args, On, Off, Toggle, ActionablePart, Snapshot

class Parts:
	def __init__(self, name, mass, selfType):
		self.name = name
		self.mass = mass
		self.type = selfType
		self.snapItems = []

		if hasattr(self, "isActive"):
			self.isActive = copy(self.isActive)

		self.child, self.children = None, {
			"all":[],
			Motor:[],
			PropellentTank:[],
			Controller:[],
			Seperator:[]
		}
		self.parent = None

	def __str__(self):
		return self.__repl__()

	def __repl__(self):
		return self.type+" "+self.name

	def Mass(self):
		return self.mass

	def Snapshot(self):
		retVal = {
			"name":self.name,
			"mass":self.mass
		}

		for i in self.snapItems:
			if type(i) == str:
				name = value = i
			elif type(i) == tuple:
				name, value = i[0], i[1]

			retVal[name] = getattr(self, value)

		return retVal

	def Traversal(self):
		retVal = [self]

		for i in self.children:
			retVal += i.Traversal()

		return retVal

	def AddChild(self, child):
		self.child = child

		for i in self.children:
			try:
				self.children[i] += child.children[i]
			except AttributeError as e:
				print(e)
				print(self.children, i, child)
				exit(-3)

		self.children["all"].append(child)
		self.children[type(child)].append(child)

		child.parent = self

class NewStage:
	def __init__(self):
		self.number = 0
		self.commands = []
		self.timer = -1
		self.isActivated = False

	def AddCommand(self, target, command, **kwargs):
		command = command[0].upper() + command[1:]
		self.commands.append((target, command, kwargs))

	def SetTimer(self, time):
		self.timer = time

	def Snapshot(self):
		return {
			"number":self.number,
			"commands":copy(self.commands),
			"timer":self.timer
		}


@ActionablePart
class Seperator(Parts):
	def __init__(self, name, mass, seperationTorque=0):
		super(Seperator, self).__init__(name, mass, "Seperator")

		self.upper, self.downer = None, None
		self.seperationTorque = seperationTorque

		setattr(self, "SetUpper", lambda self, rocket:self.Set(rocket, "Upper"))
		setattr(self, "SetDowner", lambda self, rocket:self.Set(rocket, "Downer"))

		self.snapItems = ["upper", "downer", "seperationTorque"]

	def Set(self, rocket, loc):
		if type(rocket) != Rocket:
			return False

		rocket.SetSeperator(self)

		if loc == "Upper":
			self.upper = rocket
		elif loc == "Downer":
			self.downer = rocket

	def Get(self, rocket):
		if rocket == self.upper:
			return self.downer
		elif rocket == self.downer:
			return self.upper
		else:
			return None

	## inTime = add timer to simulator
	@Toggle("isSeperated")
	@Args("rocket")
	@Args("inTime")
	def Seperation(self, rocket, inTime=0):
		# print(rocket, rocket.rootPart)
		# print(self.parent, self.parent.children)

		for category in rocket.activeParts:
			for i in self.children[category]:
				if i in rocket.activeParts[category]:
					rocket.activeParts[category].remove(i)

		### for perfect seperation, this code should remove every children parts in rocket.parts
		for category in self.children:
			for i in self.children[category]:
				self.parent.children[category].remove(i)
				# if i.isActivated == True:
				# 	pass

		self.parent = None
		# return True

class Controller(Parts):
	def __init__(self, name, mass):
		super(Controller, self).__init__(name, mass, "Controller")
		self.consume = {
			"electricity":0
		}
		self.capacity = {
			"electricity":0
		}

		self.isControllable = True
		self.rotationSpeed = 0

	def SetReource(self, type, require, capacity):
		self.consume[type] = require
		self.capacity[type] = require

	def SetRotationSpeed(self, speed):
		self.rotationSpeed = speed

@ActionablePart
class Motor(Parts):
	def __init__(self, name, thrust, impulse, mass):
		thrust *= 1000

		super(Motor, self).__init__(name, mass, "Motor")

		self.ignition = False

		self.thrust = thrust
		self.impulse = impulse

		self.fuelConsumption = thrust / (impulse * 9.86)
		self.fuelTanks = []
		self.ratio = None

		self.throttle = 0
		self.lastThrottle = 1

		self._funcs = [self.Thrust, self.Impulse, self.Mass] # , self.BurnTime

		self.snapItems = ["thrust", "impulse", "fuelConsumption"]

	@On("isIgnited")
	@Args()
	def Ignition(self):
		# print(self)
		self.throttle = self.lastThrottle

		return self.ignition

	@Off("isIgnited")
	@Args()
	def CutOff(self):
		self.lastThrottle = self.throttle
		self.throttle = 0

		return self.ignition

	# def FuelConsume(self):
	# 	NotEnoughFuel = False
	# 	### Fuel Consumption Strategy?

	# 	fcl = [i[2]*self.fuelConsumptionTemp for key, i in self.fuelRatios.items()]
	# 	fctl=[self.tanks[index].mass < value for index, value in enumerate(fcl)]

	# 	if True in fctl:
	# 		NotEnoughFuel = True
	# 	else:
	# 		for index, value in enumerate(fcl):
	# 			self.tanks[index].mass -= value
	# 			# print(self.tanks[index].mass)

	# 	return not NotEnoughFuel

	def SetConsumpRatio(self, *args):
		ratios, ratioSum = [], 0

		for i in range(0, len(args), 2):
			self.fuelTanks.append(args[i])
			args[i].AddDrainer(self)
			ratios.append([args[i], args[i+1]])
			ratioSum += args[i+1]

		for i in ratios:
			i.append(self.fuelConsumption/ratioSum*i[1])

		self.ratio = ratios

	def Drain(self, td=None):
		if not td:
			td = Sim.td

		fuels = [i[0].Drain(i[2]*td) for i in self.ratio]
		return False if False in fuels else True

	def Thrust(self, idle = False):
		return self.thrust * self.throttle if idle else self.thrust * self.throttle if self.Drain() else 0

	def SetThrottle(self, throttle):
		self.lastThrottle = self.throttle
		self.throttle = throttle

	def Impulse(self):
		return self.Impulse

class PropellentTank(Parts):
	def __init__(self, name, fuelType, mass):
		super(PropellentTank, self).__init__(name, mass, "Propellent Tank")

		self.maxMass = mass

		self.fuel = fuelType
		self.fuelDrainer = []

		self.snapItems = ["maxMass", "fuel", "ratio"]

	def AddDrainer(self, part):
		self.fuelDrainer.append(part)

	def Drain(self, amount):
		retVal = False

		if amount < self.mass:
			self.mass -= amount
			retVal = amount

		return retVal

# class Stage:
# 	def __init__(self, emptyMass):
# 		self.number = 0

# 		self.emptyMass = emptyMass
# 		self.totalMass = emptyMass

# 		self.motors = []
# 		self.tanks = []
# 		self.fuelRatios = {}

# 		self.totalFC = 0
# 		self.totalMaxThrust = 0
# 		self.thrustRatio = 1

# 		self.burnTime = 0

# 		self._funcs = ["AddPropellentTank", "AddMotor", "BurnTime", "Motor", "Thrust", "FuelConsume", "currentMass"]

# 	def stageFuelMass(self):
# 		return sum(i.mass for i in self.tanks)

# 	def stageFuelMaxMass(self):
# 		return sum(i.maxMass for i in self.tanks)

# 	def currentMass(self):
# 		return self.stageFuelMass()+self.emptyMass

# 	def Snapshot(self):
# 		dic = dict()

# 		for i in ["number", "emptyMass", "totalMass", "totalFC", "totalMaxThrust", "thrustRatio", "burnTime"]:
# 			dic[i] = getattr(self, i)

# 		dic["motors"] = []
# 		for ind in self.motors:
# 			dic["motors"].append({
# 				"motor":ind["motor"].Snapshot(),
# 				"burnTime":ind["burnTime"]
# 			})

# 		dic["tanks"] = []
# 		for ind in self.tanks:
# 			dic["tanks"].append(ind.Snapshot())

# 		dic["fuelRatios"] = copy(self.fuelRatios)

# 		return dic

# 	def SetStage(self, num):
# 		self.number = num

# 	def AddPropellentTank(self, tank):
# 		self.tanks.append(tank)
# 		if self.tanks[-1].ratio:
# 			self.fuelRatios[self.tanks[-1].ratio[0]] = self.tanks[-1].ratio

# 		self.fuelConsumptionTemp = self.totalFC / sum(i[2] for key, i in self.fuelRatios.items()) * Sim.td

# 	def AddMotor(self, m):
# 		index = len(self.motors)
# 		self.totalFC += m.fuelConsumption

# 		burnTime = self.stageFuelMass() / self.totalFC

# 		for i in self.motors:
# 			i["burnTime"] = burnTime

# 		motorData ={
# 			"motor":copy(m),
# 			"burnTime":burnTime,
# 			"functions":{}
# 		}

# 		for i in m._funcs:
# 			name = ""
# 			### TODO
# 			# dict.__setattr__() return error
# 			# if hasattr(motorData, i.__name__):
# 			# 	name = "Motor_"
# 			if i.__name__ in motorData:
# 				name = "Motor_"
# 			name += i.__name__

# 			motorData["functions"][name] = i
# 			# setattr(motorData, name, i)

# 		self.fuelConsumptionTemp = self.totalFC / sum(i[2] for key, i in self.fuelRatios.items()) * Sim.td

# 		self.motors.append(motorData)
# 		self.totalMaxThrust += m.thrust
# 		self.burnTime = burnTime

# 	def BurnTime(self, index=None):
# 		if index:
# 			return self.motors[index]["burnTime"]
# 		else:
# 			return [i["burnTime"] for i in self.motors]

# 	def Motor(self, index=None):
# 		if index:
# 			return self.motors[index]
# 		else:
# 			return self.motors

# 	def Mass(self):
# 		return self.stageFuelMass() + self.emptyMass

# 	def Thrust(self):
# 		if self.totalFC < self.stageFuelMass():
# 			return sum(i["motor"].Thrust() for i in self.motors) * self.thrustRatio
# 		else:
# 			##### calculate engine fuel distribution strategy
# 			return 0

# 	def FuelConsume(self):
# 		NotEnoughFuel = False
# 		### Fuel Consumption Strategy?

# 		fcl = [i[2]*self.fuelConsumptionTemp for key, i in self.fuelRatios.items()]
# 		fctl=[self.tanks[index].mass < value for index, value in enumerate(fcl)]

# 		if True in fctl:
# 			NotEnoughFuel = True
# 		else:
# 			for index, value in enumerate(fcl):
# 				self.tanks[index].mass -= value
# 				# print(self.tanks[index].mass)

# 		return not NotEnoughFuel

# 	def Ignition(self, index=False):
# 		if index:
# 			self.motors[index].Ignition()
# 		else:
# 			for i in self.motors:
# 				i["motor"].Ignition()

# 	def CutOff(self, index=False):
# 		if index:
# 			self.motors[index].CutOff()
# 		else:
# 			for i in self.motors:
# 				i["motor"].CutOff()

class Rocket:
	def __init__(self, name):
		self.name = name
		self.area = 0
		self.dragEfficient = 0.75

		self.focusedStage = None

		self.stages = []
		self.stageIndex = 0
		self.focusIndex = 0
		self.stageCount = 0

		self.heading = 90
		self.angle = 90
		self.rotation = Vector3d(0, 0, 0)

		self.throttle = 0.0
		self.sas = False

		self.force = Vector3d(0, 0, 0)
		self.acce, self.velocity = Vector3d(0, 0, 0), Vector3d(0, 0, 0)
		self.location, self.rotation = Vector3d(0, 0, 0), Vector3d(0, 0, 0)
		# self.totalMass = (lambda stages:lambda:sum(i.currentMass() for i in stages))(self.stages)
		self.Rotate(self.heading, self.angle)

		self.rootPart = None
		self.parts = None
		self.activeParts = {
			"all":[],
			Motor:[],
			Seperator:[]
		}
		self.controller = None

	def CheckStages(self, t):
		stage = self.stages[self.stageIndex]
		if not stage.isActivated and stage.timer < t:
			self.NextStage()

	def SetRootPart(self, part):
		self.rootPart = part
		self.parts = part.children

		self.parts["all"].append(part)
		self.parts[type(part)].append(part)

		### index = 0 or -1?
		self.controller = self.parts[Controller][0]

	def Snapshot(self):
		return {
			"name":self.name,
			"area":self.area,
			"dragEfficient":self.dragEfficient,
			"focusIndex":self.focusIndex,
			"stageCount":self.stageCount,
			"heading":self.heading,
			"angle":self.angle,

			"stageIndex":self.stageIndex,

			"acce":copy(self.acce),
			"velocity":copy(self.velocity),
			"location":copy(self.location),
			"rotation":copy(self.rotation),

			# "focusedStage": self.focusedStage.Snapshot(),
			"stages":[i.Snapshot() for i in self.stages],

			"maxQ":self.maxQ(),
			"TotalMass":self.TotalMass(),
			"TWR":self.Thrust() / self.TotalMass(),
			"possible TWR":self.MaxThrust()/self.TotalMass(),
		}

	def Calculate(self, t, td):
		self.CheckStages(t)
		self.ContinousRotation(td)

	def MaxThrust(self):
		return sum(i.Thrust(idle = True) for i in self.activeParts[Motor])

	def TotalMass(self):
		# print(self.focusIndex, self.stages[:self.focusIndex])
		# return sum(i.currentMass() for i in self.stages[:self.focusIndex])
		return sum(i.Mass() for i in self.parts["all"])

	def AddStage2(self, stage):
		self.stages.append(stage)
		# self.stageIndex += 1
		stage.number = len(self.stages)

	def NextStage(self):
		stage = self.stages[self.stageIndex]

		for target, command, kwargs in stage.commands:

			if target not in self.rootPart.children["all"]:
				continue

			func = getattr(target, command)
			args = getattr(func, "args")
			# print(args)
			#### need to check isConnected
			if func:
				if "rocket" in args:
					kwargs["rocket"] = self
				# print(func, kwargs, self.stageIndex, stage)
				# print(stage.commands)
				if kwargs:
					isActive = func(**kwargs)
				else:
					isActive = func()
					# print(command, isActive)

				## insert this code into decorator???
				if isActive:
					self.activeParts["all"].append(target)
					self.activeParts[type(target)].append(target)
				else:
					# print(isActive, self.activeParts["all"], target)
					self.activeParts["all"].remove(target)
					self.activeParts[type(target)].remove(target)

		# print(self.activeParts[Motor])
		self.stageIndex += 1

	# def AddStage(self, stage):
	# 	self.stages.append(stage)
	# 	stage.SetStage(len(self.stages))

	# 	for i in stage._funcs:
	# 		setattr(self, "Stage%d%s"%(stage.number, i), getattr(stage, i))

	# 	self.SetFocusedStage(stage)
	# 	self.stageCount += 1
	# 	self.focusIndex += 1

	def SetRotation(self, x=0, y=0, z=0):
		self.rotationAngle = Vector3d(x, y, z)

	def ContinousRotation(self, td):
		d = self.rotationAngle.Normal() * td * self.controller.rotationSpeed
		self.rotationAngle -= d

		self.Rotate(d.x, d.y, d.z)

	def Rotate(self, x=0, y=0, z=0):
		self.rotation = self.rotation.xRotate(x).yRotate(y).zRotate(z)
		# print(self.rotation, x, y, z)

	def Rotate2(self, azimuth=None, angle=None):
		# print("rotation??", Sim.t)
		if not azimuth:
			azimuth = 0
		else: self.heading = azimuth

		if not angle:
			angle = 0
		else: self.angle = angle

		rotation = self.location.zRotate(azimuth)
		rotation = rotation.Rotate(angle).Normal()
		self.rotation = rotation

	### calculate burntime for each mortors or stages's ignited mortors
	def BurnTime(self):
		pass

	def Thrust(self):
		thrust = 0

		for i in self.activeParts[Motor]:
			thrust += i.Thrust()
		return thrust

	def SetFocusedStage(self, stage):
		self.focusedStage = stage
		for i in ["AddPropellentTank", "AddMotor", "BurnTime", "Motor", "Thrust", "FuelConsume", "stageFuelMass", "stageFuelMaxMass", "currentMass"]:
			setattr(self, i, (lambda key:lambda *args:getattr(self.focusedStage, key)(*args))(i))

	def Mass(self):
		return sum(i.Mass() for i in self.stages)

	def maxQ(self):
		return Sim.airDensity(self.location.z) * 0.5 * (self.velocity.z**2)

	### command list
	def Seperate(self):
		if 2 <= len(self.stages):
			self.focusIndex -= 1
			# print(self.focusedStage.number, self.focusIndex-1, self.stages[self.focusIndex-1].number)
			self.SetFocusedStage(self.stages[self.focusIndex-1])
			# print(self.focusedStage.number)

	def SetThrottle(self, percent):
		self.throttle = percent / 100

		for i in self.activeParts[Motor]:
			i.SetThrottle(self.throttle)

	def Ignition(self, *args):
		# print(self.focusedStage.number)
		for i in self.focusedStage.motors:
			i["motor"].SetThrottle(self.throttle)
			# print(i["motor"].Thrust())
		self.focusedStage.Ignition(*args)

	def CutOff(self, *args):
		self.focusedStage.CutOff(*args)

	def On(self, part):
		if part == "SAS":
			self.sas = True

	def CU(self, sim):
		if (sim.t*100) % 100 == 0:
			if self.sas : self.Rotate2(azimuth = self.heading, angle = self.angle)
