import math
from .Vector3d import Vector3d

class Planet:
	def __init__(self, **kwarg):
		self.location = Vector3d(0, 0, 0)

		if "GM" in kwarg:
			self.GM = kwarg["GM"]*1000

		if "radius" in kwarg:
			self.radius = self.Radius = kwarg["radius"]*1000

		if "gravityAccel" in kwarg:
			self.gravityAccel = kwarg["gravityAccel"]

		if "atmosphere" in kwarg:
			self.atmosphere = kwarg["atmosphere"]*1000

	def Gravity(self, alt):
		return self.gravityAccel * (self.radius / (self.radius+alt))**2

	def GetPlanetCircle(self):
		y = lambda theta:math.sin(math.radians(theta)) * self.radius
		x = lambda theta:math.cos(math.radians(theta)) * self.radius

		return [Vector3d(x(i), y(i), 0) for i in range(0, 360)]

	def Snapshot(self):
		return {
			"location":self.location
		}


Earth = Planet(GM=398600441800, radius = 6378, gravityAccel = 9.8, atmosphere = 120)
# for i in Earth.GetPlanetCircle():
# 	print("%.2lf\t%.2lf"%(i.x/1000, i.y/1000))
# exit(0)
