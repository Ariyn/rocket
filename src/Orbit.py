from math import *
from .Vector3d import Vector3d, MatrixDot

class NotCalculated(Exception):
	pass

### ascending , descending node!
class Orbit:
	def __init__(self, p1, v1, planet):
		self.orbitPlane = Vector3d.zAxis
		self.rotatedPlane = None

		self.inclination = 0
		self.ascendingNode = 0
		self.rotateMatrix = None

		self.e = self.eccentricity = 0
		self.eAnomaly = 0
		self.meanAnomaly = 0

		self.planet = planet

		self.apogeeRadius, self.perigeeRadius = None, None
		self.apogeeSpeed, self.perigeeSpeed = None, None

		self.__CreateOrbit__(p1, v1)

	### looks like make many errors when orbit is hyperbolic!!
	def __CreateOrbit__(self, location, velocity, angle=None):
		r1 = self.planet.radius + location.z
		# r1 = location.z
		v1 = velocity.Size()

		if not angle :
			newLoc, vel2 = Orbit.Transform3D(location, velocity, self.planet)
			angle = newLoc.Angle(velocity)

		self.inclination = degrees( asin( vel2.z / vel2.Size() ))
		zenithAngle = angle
		c = self.planet.GM/(r1*(v1**2))*2

		mid = sqrt(c**2+4*(1-c)*(sin(radians(angle))**2))
		p1 = (-c+mid)/2/(1-c)*r1
		p2 = (-c-mid)/2/(1-c)*r1

		p1, p2 = (p1-self.planet.radius)/1000, (p2-self.planet.radius)/1000

		self.apogeeRadius, self.perigeeRadius = (p1, p2) if p2 < p1 else (p2, p1)

		# print(self.apogeeRadius, self.perigeeRadius)
		self.apogeeRadius = self.apogeeRadius*1000 + self.planet.radius
		self.perigeeRadius = self.perigeeRadius*1000 + self.planet.radius

		GM = self.planet.GM
		midTerm = (r1*velocity.Size()**2) / GM
		# midTerm = (r1*velocity.x**2) / (GM)

		zenithAngle = radians(zenithAngle)
		self.e = self.eccentricity = sqrt( (midTerm-1)**2*sin(zenithAngle)**2 + cos(zenithAngle)**2 )
		trueAnomaly = (midTerm*sin(zenithAngle)*cos(zenithAngle))
		self.trueAnomaly = trueAnomaly/( (midTerm)*(sin(zenithAngle)**2) - 1 )

		v = radians(self.trueAnomaly)
		self.eAnomaly = degrees(acos(( self.e + cos(v) ) / ( 1 + self.e * cos(v) )))
		self.meanAnomaly = self.eAnomaly - self.e*sin(radians(self.eAnomaly))

		a = self.perigeeRadius/(1-self.e)
		b = a*sqrt(1-self.e**2)
		self.SetAxis(a = a, b = b)

		period = 2*pi*sqrt(a**3/GM)
		self.period = period

		n = 2*pi/period
		self.orbitTime = self.meanAnomaly / n

		vp = sqrt((self.e+1)*GM/self.apogeeRadius)
		self.perigeeSpeed = vp

		# ap = pe/( (2*GM)/(pe*vp**2)-1 )
		va = sqrt((2*GM)/(self.apogeeRadius/self.perigeeRadius+1)/self.apogeeRadius)
		self.apogeeSpeed = va

		self.Rotate()

		self.apogee = self.Get(180)
		self.perigee = self.Get(0)

		self.TAradius = self.majorAxis * (1-self.e**2) / (1 + self.e*cos(self.trueAnomaly))

		self.progressVector = MatrixDot(self.rotateMatrix, Vector3d.zAxis.Outer(location))

		# print("inclination", self.apogee.z - self.perigee.z)
		# print("apogee, perigee", self.apogee, self.perigee)

	### does not return latitude in range(-90~90)
	### wrong latitude when y goes under minus or over pi*r
	@staticmethod
	def TransformPolar(loc, planet):
		sign = atan2(loc.y,loc.x) - atan2(Vector3d.yAxis.y,Vector3d.yAxis.x)

		if sign < 0:
			sign, alpha = -1, 360
		else:
			sign, alpha = 1, 0

		size = sqrt(loc.x**2 + loc.y**2)
		long, lat = loc.Angle(Vector3d.yAxis)*sign+alpha, degrees(size/planet.radius)

		return long, lat

	@staticmethod
	def Transform3D(loc, vel, planet):
		sign = atan2(loc.y,loc.x) - atan2(Vector3d.yAxis.y,Vector3d.yAxis.x)

		if sign < 0:
			sign, alpha = -1, 360
		else:
			sign, alpha = 1, 0

		size = sqrt(loc.x**2 + loc.y**2)
		long, lat = loc.Angle(Vector3d.yAxis)*sign+alpha, degrees(size/planet.radius)

		newLoc = loc+vel

		newSize = sqrt(newLoc.x**2 + newLoc.y**2)
		newLong, newLat = newLoc.Angle(Vector3d.yAxis), degrees(newSize/planet.radius)
		# print(newLong, newLat)

		r = planet.radius + loc.z
		deg = radians(90)
		newR = newLoc.z+planet.radius

		long, lat = radians(long), radians(lat)
		newLong, newLat = radians(newLong), radians(newLat)
		loc = Vector3d(r*sin(lat)*cos(long+deg), r*sin(lat)*sin(long+deg), r*cos(lat))
		newLoc = Vector3d(newR*sin(newLat)*cos(newLong+deg), newR*sin(newLat)*sin(newLong+deg), newR*cos(newLat))

		return loc, newLoc-loc

	def Rotate(self, inclination=0, ascendingNode=0):
		if not inclination:
			inclination = self.inclination
		if not ascendingNode:
			ascendingNode = self.ascendingNode

		rotatedPlane = Vector3d.zAxis.yRotate(inclination).zRotate(ascendingNode)

		c = (self.orbitPlane*rotatedPlane) / ( self.orbitPlane.Size() * rotatedPlane.Size() )
		axis = self.orbitPlane.UnitOuter(rotatedPlane)

		s = sqrt(1-c*c)
		C = 1-c
		self.rotateMatrix = ([axis.x*axis.x*C+c, axis.x*axis.y*C-axis.z*s, axis.x*axis.z*C+axis.y*s],
				[axis.y*axis.x*C+axis.z*s, axis.y*axis.y*C+c, axis.y*axis.z*C-axis.x*s],
				[axis.z*axis.x*C-axis.y*s, axis.z*axis.y*C+axis.x*s, axis.z*axis.z*C+c])

		self.rotatedPlane = rotatedPlane

	def TestGet(self, vector):
		rotatedPoint = MatrixDot(self.rotateMatrix, vector)

		return rotatedPoint

	def OrbitPeriod(self):
		return 2*pi*sqrt(self.a**3/self.planet.GM)

	def Get(self, trueAnomaly=None):
		if trueAnomaly != None:rotation = trueAnomaly

		v = radians(rotation)
		r = self.a*(1-self.e**2) / (1+self.e*cos(v))
		angle = degrees(atan(self.e*sin(v) / (1+self.e*cos(v))))
		velocity = sqrt(self.planet.GM*(2/r - 1/self.a))

		x = r*cos(v)
		y = r*sin(v)

		# print(r, angle, velocity)
		# print(x, y)

		return MatrixDot(self.rotateMatrix, Vector3d(x, y, 0))

	def GetPositionByTime(self, t):
		t += self.orbitTime
		period = self.OrbitPeriod()
		n = 2*pi/period
		newMeanAnomaly = n*t

		# print(degrees(newMeanAnomaly), newMeanAnomaly)
		newEAnomaly = Orbit.__InverseKepler(self.e, newMeanAnomaly)
		# print("new mean anomaly : %.2lfdef\tnew eccentricity anomaly %.2lf deg"%(degrees(newMeanAnomaly), newEAnomaly))

		## wrong true anomaly!
		## check https://en.wikipedia.org/wiki/True_anomaly
		re = radians(newEAnomaly)
		# v = acos(( cos(re)-self.e ) / ( 1-self.e*cos(re) ))
		v = atan(sqrt((1+self.e)/(1-self.e)) * tan(re/2))*2
		trueAnomaly = (degrees(v)+360) % 360

		# trueAnomaly = atan(sqrt((1+self.e)*tan(radians(newEAnomaly / 2)) / (1-self.e))) * 2
		r = self.a*(1-self.e*cos(re))
		# print("new trueAnomaly %.2lf deg"%trueAnomaly)# print(trueAnomaly)

		positionVector = self.Get(trueAnomaly = trueAnomaly)
		return positionVector
		# return trueAnomaly, r

	def SetEccentricity(self, e):
		self.e = self.eccentricity = e

	def SetTrueAnomaly(self, trueAnomaly):
		trueAnomaly = degrees(atan(trueAnomaly))
		self.trueAnomaly = trueAnomaly

	def SetAxis(self, a=None, b=None):
		if a:
			self.a = self.majorAxis = a
		if b:
			self.b = self.minorAxis = b

	def Report(self):
		print("")
		print("Apogee : %.2lfkm, Perigee : %.2lfkm"%( (self.apogeeRadius-self.planet.radius)/1000, (self.perigeeRadius-self.planet.radius)/1000 ))
		print("Apogee : %.2lf %.2lf %.2lf, Perigee : %.2lf %.2lf %.2lf"%(
			self.apogee.x/1000, self.apogee.y/1000, self.apogee.z/1000,
			self.perigee.x/1000, self.perigee.y/1000, self.perigee.z/1000 ))
		print("ApogeeSpeed : %.2lfkm/s\tPerigeeSpeed : %.2lfkm/s"%(self.apogeeSpeed/1000, self.perigeeSpeed/1000))
		print("true anomaly %.5lf"%self.trueAnomaly)
		print("eccentricity %.5lf"%self.e)
		print("major axis : %.2lfkm, minor axis : %.2lfkm"%(self.a/1000, self.b/1000))
		print("period", self.OrbitPeriod())

	def ReportOrbit(self):
		print("")
		print(int(self.OrbitPeriod()))

		for i in range(0, int(self.OrbitPeriod())):
			# print(i)
			d = self.GetPositionByTime(i)
			print("%.2lf\t%.2lf"%(d.x/1000, d.y/1000))

	def SnapShot(self):
		raise NotImplemented

	## this function does not calculate correct E
	@staticmethod
	def __InverseKepler(e, M):
		E = M
		loopCount=0
		while loopCount < 100:
			# rE = radians(E)
			rE= E
			### radians(E)?
			### or just E?
			dE = (E - e * sin(rE) - M)/(1 - e * cos(rE));
			# print(dE, E)
			E -= dE;
			# print(E)
			if( abs(dE) < 1e-6 ):break
			loopCount += 1
			# print("")
		if 100 <= loopCount:
			raise NotCalculated
		return degrees(E)
	# function E(e,M,n)
 #   E = M
 #   for k = 1 to n
 #       E = M + e*sin E
 #       next k
 #   return E
