from math import sqrt, cosh, log, atan, acosh, pi

from .Simulator import Sim
from .Vector3d import Vector3d, MatrixDot
from .Orbit import Orbit
from .Falcon9 import Falcon9

"""
TODO:
Rocket Blueprint System - RBS
	parse blueprint and make all rocket parts automatically.
More Powerful Staging System - MPSS
	Falcon Heavy's stage 4,3 shares same main engine.
	Concept of staging is totally different thing from Seperation.
Dynamic ISP
Rocket Shape, Engine Compile
	compile engine isp, thrust specs
	compile rocket drag efficiency
"""

datas = [tuple("time,location.x,location.y,location.z,velocity.x,velocity.y,velocity.z,accel.x,accel.y,accel.z,thrust.x,thrust.y,thrust.z".split(","))]
newDatas = []
def printRocket(*args):
	global newDatas
	string = "\t".join(["%.2lf"%i for i in args])
	# newDatas.append(string)
	# print(string)

def convertToCSV(self):
	t = 180

	if int(self.t*100)%100 == 0:
		v = self.rocket.location
		print("%.2lf\t%.2lf\t%.2lf\t%.2lf"%(self.t, v.x/1000, v.y/1000, v.z/1000))

	if 29 <= self.t <= 39.99:
		v = self.rocket.rotation
		# v = self.orbit.GetPositionByTime(self.t - self.orbitT)
		# print("%.2lfs\t%.2lf\t%.2lf\t%.2lf"%(self.t, v.x, v.y, v.z))

	if not self.inPhysics:
		# print(int(self.t*100))
		# v = self.rocket.location
		# print("%.2lf\t%.2lf\t%.2lf"%(v.x/1000, v.y/1000, v.z/1000))
		if 250 <= self.t and int(self.t*100)%100 == 0:
			v = self.rocket.location
			# v = self.orbit.GetPositionByTime(self.t - self.orbitT)
			# print("%.2lf\t%.2lf\t%.2lf"%(v.x/1000, v.y/1000, v.z/1000))

	if -Sim.td < self.t-t <= Sim.td:
		# Sim.CalculateOrbit()
		t = 0
		# print(self.rocket.TotalMass())
	# printRocket(self.t, self.rocket.location.x,self.rocket.location.y,self.rocket.location.z, self.rocket.velocity.x,self.rocket.velocity.y,self.rocket.velocity.z, self.rocket.acce.x,self.rocket.acce.y,self.rocket.acce.z,self.force.x,self.force.y,self.force.z, self.rocket.TotalMass())
	pass


### orbit step and 3d physics step not matched
### looks like problem during orbit creation

Sim.SetRocket(Falcon9)

### Rocket.Rotate Does not rotate correctly.

Sim.limitedTime = 150
Sim.breakPoints.append(0)
Sim.breakPoints.append(10)
Sim.breakPoints.append(20)
Sim.breakPoints.append(30)
# Sim.breakPoints.append(40)
Sim.breakPoints.append(70) # should be close to mach 1
Sim.breakPoints.append(220)
Sim.breakPoints.append(260)
# Sim.breakPoints.append(266)
Sim.breakPoints.append(300)

Sim.AddCommand(1, Falcon9, "throttle", 100)

Sim.AddCommand(10, Falcon9, "rotate", 0, 0, 2)
# Sim.AddCommand(10, Falcon9, "throttle", 50)

Sim.AddCommand(20, Falcon9, "rotate", 0, 0, 8)
# Sim.AddCommand(20, Falcon9, "throttle", 70)

# Sim.AddCommand(40, Falcon9, "throttle", 90)
for i in range(0, 8):
	Sim.AddCommand(20+i*10, Falcon9, "rotate", 0, 0, 10)

Sim.Run(lambda sim:print("%0.2f, %0.2f"%(sim.t, (sim.rocket.location.Size()-sim.planet.radius)/1000)) if int(sim.t*100)%100==0 else None)

# rocket = Sim.rocket
# orbit = Sim.orbit

# print(rocket.heading, rocket.angle)
# print(Sim.orbit)

### TODO: report flow log to csv
Sim.Report()
# print(Sim.reportDict.keys())
# for i in range(int(Sim.startRecording*100+1), int(Sim.t*100)):
# 	print(Sim.reportDict[i/100])
# Sim.orbit.ReportOrbit()
