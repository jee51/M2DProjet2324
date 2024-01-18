# <center>A baseline model for turbojet engine fuel consumption</center>

<center>Julia Carbo<sup>1</sup>, Dinh Quang Dung<sup>1</sup>, Achile Ngeuessiek<sup>1</sup>, Khalifa Michel Ouattara<sup>1</sup>, Jérôme Lacaille<sup>1,2</sup></center>

<center><sup>1</sup> <em>Université Sorbonne Paris Nord</em></center>
<center><sup>2</sup> <em>Safran Aircraft Engines</em></center>

## Abstract

The aviation industry has joined forces within the Air Transport Action Group (ATAG) to converge on zero-carbon operations by 2050. One of the key factors in the generation of carbon dioxide is fuel combustion. This will certainly involve replacing fossil fuels with hydrogen or sustainable aviation fuels (SAF). But for several years now, engine manufacturers have been successfully reducing fuel consumption with the help of increasingly advanced technologies, such as the use of ceramic components (CMC) for hot parts, additive manufacturing of complex parts, and carbon fibers to lighten blades and carter. The LEAP, Safran's latest turbojet engine for medium-range aircraft, consumes 15% less fuel than the previous CFM56 engines powering the Boeing 737 and most Airbus A320 series. Current consumption is known to be around 2 liters per 100 kilometers per passenger.

Designing more efficient engines is not the only way to reduce fuel consumption. A very important factor is the way the aircraft is flown.
Engineers are working on physical and numerical models to identify the most critical phases of flight, and suggest good piloting practices and more suitable routes.
These models are complicated because it is important to be able to interpret each result in order to infer new rules. This work does not present one of these models, but proposes a rough numerical baseline on which it will be possible to base the qualification of more complex technical solutions.

## Introducing the problem

We have 3 data sets, each corresponding to an aircraft of the same type. Each set contains around 1000 successive flights, with measurements made on both engines.
Flights are therefore stored in tables with the number of seconds elapsed since the ECU was powered up as the time index, and a series of measurements made during the flight as the columns.
During each flight, aircraft data is recorded, as well as measurements made on each of the two engines. 
Some measurements are taken at different positions in the engine, called stations, like pressures and temperatures. Station 1 is the air intake and station 5 is the exhaust nozzle.