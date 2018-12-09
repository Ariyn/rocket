## Rocket Simulator

you can simulate rockets.

## usuage
first import rocket modules. you can also create your own module. if so, you need to override some specific methods.
```python
from .Rocket import Motor, PropellentTank, NewStage, Seperator, Controller, Rocket
```

then create Module's instances, connect each others.
for example, solid booster will contain both motor and propellentTank.
```python
sbs = Motor("Solid Booster System", 593, 195, 4.5)
sbpt = PropellentTank("PBAN Tank", "PBAN", 20.5*1000)
sbpt.AddChild(sbs)
sbs.SetConsumpRatio(sbpt, 1)
```
sbs, which is Solid Booster System will consume propellent from sbpt 1 per second.
(by the way, I know it's unit is little confusing. this chaotic unit system will be replaced to more obvious unit system.)

next create controller. in this case, Controller will be unmanned-remote controller.
```python
controller = Controller("Remote Controller", 100)
controller.AddChild(sbpt)
```

and create stage.
```python
stage1 = NewStage()
stage1.AddCommand(sbs, "ignition")
stage1.SetTimer(0)
```
stage1 will be executed in T+0. during execution, stage will run added commands. in here, sbs will be ignited.

then create rocket
```python
rocket = Rocket("Sisyphus Falcon-Niner")
rocket.AddStage2(stage1)
rocket.SetRootPart(controller)
```

ok. creating rocket is done. let's add some reporting point and fly.
```python
from Simulator import Sim
from Rocket import rocket

Sim.limitedTime = 150
Sim.SetRocket(rocket)

for i in range(0, Sim.limitedTime, 10):
	Sim.breakPoints.append(i)
Sim.Run()
Sim.report()
```
