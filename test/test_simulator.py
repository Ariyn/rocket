import unittest

from src.Simulator import Sim

class SimulatorUnittest(unittest.TestCase):
	def test_airDensity(self):
		for alt in range(50):
			density = Sim.airDensity2(alt)
			print(density)
