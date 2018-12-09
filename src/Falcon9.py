from .Rocket import Motor, PropellentTank, NewStage, Seperator, Controller, Rocket
from .Vector3d import Vector3d

# in real Falcon 9 FT
# MECO : T+160s
# Speed: 2.287Km/s
# Alt  : 63.4Km

# Sisyphus Falcon-Niner
# MECO : T+160s
# Speed: 1.28Km/s
# Alt : 67.86Km

# Stage #1
# Total Mass = 432669
# Fuel Mass  = 398887
# Empty Mass = 33782

# Stage #2
# Total Mass = 112185
# Fuel Mass  = 108185
# Empty Mass = 4000

# Stage #3 = Payload
# Total Mass = 4200
# Fuel Mass  = 0

# STAGE 3

sbs = Motor("Solid Booster System", 593, 195, 4.5)
sbpt = PropellentTank("PBAN Tank", "PBAN", 20.5*1000)
sbpt.AddChild(sbs)
sbs.SetConsumpRatio(sbpt, 1)

bs = Seperator("Booster Seperator", 100)
bs.AddChild(sbpt)

sbs2 = Motor("Solid Booster System", 593, 195, 4.5)
sbpt2 = PropellentTank("PBAN Tank", "PBAN", 20.5*1000)
sbpt2.AddChild(sbs2)
sbs2.SetConsumpRatio(sbpt2, 1)

bs2 = Seperator("Booster Seperator", 100)
bs2.AddChild(sbpt2)


p1 = PropellentTank("LOX Tank", "LOX", 398887/3.56*2.56)
p2 = PropellentTank("RP-1 Tank", "RP-1", 398887/3.56)

ss = Seperator("Stage 1 Seperator", 100)

motors = [Motor("Merlin 1D", 760, 320, 630) for i in range(0,9)]
for i in motors:
	p1.AddChild(i)
	i.SetConsumpRatio(p1, 2.56, p2, 1)
p2.AddChild(p1)

p2.AddChild(bs)
p2.AddChild(bs2)

ss.AddChild(p2)

# STAGE 2
mV = Motor("Merlin 1D Veccum", 934, 342, 630)
p3 = PropellentTank("LOX Tank", "LOX", 108185/3.56*2.56)
p4 = PropellentTank("RP-1 Tank", "RP-1", 108185/3.56)
mV.SetConsumpRatio(p3, 2.56, p4, 1)

mV.AddChild(ss)
p3.AddChild(mV)
p4.AddChild(p3)

ss2 = Seperator("Stage 2 Seperator", 100)
ss2.AddChild(p4)

mD = Motor("Draco", 0.4, 300, 700)
p5 = PropellentTank("NTO Tank", "NTO", 3310/3.16*2.16)
p6 = PropellentTank("MMH Tank", "MMH", 3310/3.16)
mD.SetConsumpRatio(p5, 2.16, p6, 1)
c = Controller("Dragon Ship", 100)
c.SetRotationSpeed(1)

mD.AddChild(ss2)
p5.AddChild(mD)
p6.AddChild(p5)
c.AddChild(p6)

ns1 = NewStage()
for i in motors:
	ns1.AddCommand(i, "ignition")
ns1.SetTimer(0)

ns2 = NewStage()
ns2.AddCommand(bs, "seperation")
ns2.AddCommand(bs2, "seperation")
ns2.SetTimer(160)

ns3 = NewStage()
ns3.AddCommand(ss, "seperation")
ns3.isActivated = True

r = Rocket("Sisyphus Falcon-Niner")
r.area = (3.7/2)**2*3.141592*0.5/1000
r.dragEfficient = 0.25

r.AddStage2(ns1)
r.AddStage2(ns2)
r.AddStage2(ns3)

r.SetRootPart(c)

Falcon9 = r
