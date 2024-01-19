# <center>A baseline model for turbojet engine fuel consumption</center>

<center>Julia Carbo<sup>1</sup>, Dinh Quang Dung<sup>1</sup>, Achile Ngeuessiek<sup>1</sup>, Khalifa Michel Ouattara<sup>1</sup>, Jérôme Lacaille<sup>1,2</sup></center>
<br>
<center><sup>1</sup> <em>Université Sorbonne Paris Nord</em></center>
<center><sup>2</sup> <em>Safran Aircraft Engines</em></center>

## Abstract

The aviation industry has joined forces within the Air Transport Action Group (ATAG) to converge on zero-carbon operations by 2050. One of the key factors in the generation of carbon dioxide is fuel combustion. This will certainly involve replacing fossil fuels with hydrogen or sustainable aviation fuels (SAF). But for several years now, engine manufacturers have been successfully reducing fuel consumption with the help of increasingly advanced technologies, such as the use of ceramic components (CMC) for hot parts, additive manufacturing of complex parts, and carbon fibers to lighten blades and carter. The LEAP, Safran's latest turbojet engine for medium-range aircraft, consumes 15% less fuel than the previous CFM56 engines powering the Boeing 737 and most Airbus A320 series. Current consumption is known to be around 2 liters per 100 kilometers per passenger.

Designing more efficient engines is not the only way to reduce fuel consumption. A very important factor is the way the aircraft is flown.
Engineers are working on physical and numerical models to identify the most critical phases of flight, and suggest good piloting practices and more suitable routes.
These models are complicated because it is important to be able to interpret each result in order to infer new rules. This work does not present one of these models, but proposes a rough numerical baseline on which it will be possible to base the qualification of more complex technical solutions. Once this model has been built, we'll have a hypothesis about the standard behavior of an aircraft, and by observing deviations from this behavior we'll be able to identify particular missions with either excessive or below-normal fuel consumption.

## Introducing the problem

We have 3 data sets, each corresponding to an aircraft of the same type. Each set contains around 1000 successive flights, with measurements made on both engines.
Flights are therefore stored in tables with the number of seconds elapsed since the ECU was powered up as the time index, and a series of measurements made during the flight as the columns.
During each flight, aircraft data is recorded, as well as measurements made on each of the two engines. 
Some measurements are taken at different positions in the engine, called stations, like pressures and temperatures. Station 1 is the air intake and station 5 is the exhaust nozzle. The measurements of particular interest to us for this work are described in the table below.

<em>Table 1. List of a few interest variables.</em>

| Variable [unité] | Description |
|:---------|:------------|
| ALT [ft] | Altitude |
| TAT [deg C] | Total Air Température (measured by the aircraft sensor) |
| M [Mach] | Mach |
| NAIV_# [bool] | Anti Ice Vanne |
| P0_# [psia] | Pression en entrée |
| Q_# [lb/h] | Fuel flow |
| TLA_# [deg] | Level Angle |
| T_OIL_# [deg C] | Oil temperature |

The following figure shows an example of conventional flight.

![One flight in cold conditions](../docs/images/one_flight_in%20rough_conditions.png)

<em>Figure 1. This plot shows a classic civil flight in cold condiions. The red bottom line is the altitude (in feet) of the aircraft and the top blue line corresponds to a booleand that indicates if anti-ice is on.</em>

The flight consists mainly of 5 phases: a driving phase (taxi) at the begining and at the end of the flight, a climb phase, a cruise phase and a descent phase.
In this project we are only interested in flight proper therefore in the three main phases: climb, cruise and descent. 
In Figure 1, a special case of the anti-ice system has been presented which decreases the power of the engine by hot air sampling. This measure is important because it is a factor of augmentation in consumption. This flight uses the anti-ice in takeoff and landing because the two airports had to be in temperature and humidity winter conditions.

## Methodology

We will create a model of prediction of global consumption, control its robustness by a cross validation process and study its precision.Then it will be possible to look at which flights that consume more or month than normal by binaryly quantifying the prediction residues.

### A first elementary model based on the duration of the flight

La première idée, élémentaire, consiste à regarder la consommation en fonction de la durée du vol. C'est une première approximation logique. L'image suivante donne  
### Etude de chaque phase

## Results

## Conclusion

## References