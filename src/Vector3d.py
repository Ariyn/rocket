import math
from functools import singledispatch

def MatrixDot(matrix, vector):
	dataMatrix = [vector.x, vector.y, vector.z]
	newMatrix = []
	for i, v in enumerate(matrix):
		# x = sum(map(lambda data:data*dataMatrix[i], v))
		d = 0
		for index, v2 in enumerate(v):
			d += v2 * dataMatrix[index]
		# newMatrix.append(sum(map(lambda data:data*dataMatrix[i], v)))
		newMatrix.append(d)
		# print(i, v, dataMatrix[i], x)
	return Vector3d(newMatrix[0], newMatrix[1], newMatrix[2])
class Vector3d:
	xAxis, yAxis, zAxis = None, None, None
	origin, zero = None, None

	def __init__(self, x, y, z):
		self.x, self.y, self.z = x, y, z

	def __eq__(self, other):
		return self.x==other.x and self.y == other.y and self.z == other.z

	def __pow__(self, other):
		return Vector3d(self.x**other, self.y**other, self.z**other)

	def __mul__(self, other):
		if type(other) == Vector3d:
			return self.x*other.x + self.y*other.y + self.z*other.z
		elif type(other) in [int, float]:
			return Vector3d(self.x*other, self.y*other, self.z*other)

	def __truediv__(self, other):
		return self.__mul__(1/other)

	def __isub__(self, other):
		return self.__sub__(other)

	def __sub__(self, other):
		return self.__add__(-other)

	def __iadd__(self, other):
		return self.__add__(other)

	def __add__(self, other):
		return Vector3d(self.x+other.x, self.y+other.y, self.z+other.z)

	def __neg__(self):
		return Vector3d(-self.x, -self.y, -self.z)

	def __str__(self):
		return "%.3lf\t%.3lf\t%.3lf"%(self.x, self.y, self.z)

	def Size(self):
		return self.VectorSize()

	def VectorSize(self):
		return math.sqrt(self.x**2+self.y**2+self.z**2)

	def Normal(self):
		return self.Normalize()
	def Normalize(self):
		size = self.VectorSize()
		if size != 0:
			return Vector3d(self.x, self.y, self.z) / size
		else:
			return self

	def xRotate(self, q):
		q = math.radians(q)
		sinQ, cosQ = math.sin(q), math.cos(q)
		return Vector3d(self.x, self.y*cosQ-self.z*sinQ, self.y*sinQ+self.z*cosQ)

		# x' = x
		# y' = y*cos q - z*sin q
		# z' = y*sin q + z*cos q

	def yRotate(self, q):
		q = math.radians(q)
		sinQ, cosQ = math.sin(q), math.cos(q)
		return Vector3d(self.z*sinQ+self.x*cosQ, self.y, self.z*cosQ-self.x*sinQ)

		# x' = z*sin q + x*cos q
		# y' = y
		# z' = z*cos q - x*sin q

	def zRotate(self, q):
		q = math.radians(q)
		sinQ, cosQ = math.sin(q), math.cos(q)
		return Vector3d(self.x*cosQ-self.y*sinQ, self.x*sinQ+self.y*cosQ, self.z)

		# x' = x*cos q - y*sin q
		# y' = x*sin q + y*cos q
		# z' = z

	def Rotate(self, q):
		axisVector = Vector3d.zAxis.Outer(self).Normalize()
		if axisVector.Size() == 0:
			angle = 90
		else:
			angle = axisVector.Angle(-Vector3d.xAxis)

		# print(angle, angle%90)
		if 90 < angle:
			angle = (angle%90)

		# print("")
		rotVel = self.zRotate(angle)
		# print(rotVel)
		rotVel = rotVel.xRotate(q)
		# print(rotVel)
		rotVel = rotVel.zRotate(-angle)
		# print(rotVel)

		return rotVel

	def UnitOuter(self, other):
		if self == other:
			return Vector3d(0, 0, 0)

		c = self.Outer(other)
		# print(c, c.Normalize())
		c = c / c.Size()
		return c

	def SignedAngle(self, other):
		sign = math.atan2(self.y, self.x) - math.atan2(other.y, other.x)

		if sign < 0:
			sign, alpha = -1, 360
		else:
			sign, alpha = 1, 0

		return self.Angle(other)*sign+alpha

	def Angle(self, other):
		cosa = (self*other)/(self.VectorSize()*other.VectorSize())
		angle = math.degrees(math.acos(cosa))

		# print(angle, 180-angle)
		# if angle < 180-angle:
		return angle
		# else:
		# 	return 180-angle
		# return min(angle, 180-angle)

	def Outer(self, other):
		x = self.y*other.z - self.z*other.y
		y = self.x*other.z - self.z*other.x
		z = self.x*other.y - self.y*other.x

		# print(x, -y, z)
		return Vector3d(x, -y, z)
		# return [
		# 	["i", "j", "k"],
		# 	[self.x, self.y, self.z],
		# 	[other.x, other.y, other.z]
		# ]

Vector3d.xAxis = Vector3d(1, 0, 0)
Vector3d.yAxis = Vector3d(0, 1, 0)
Vector3d.zAxis = Vector3d(0, 0, 1)
Vector3d.origin = Vector3d(0, 0, 0)
Vector3d.zero = Vector3d(0, 0, 0)
