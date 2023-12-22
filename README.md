# Projet du master 2 des données USPN 2023-2024.

Développement collaboratif du code du projet du Master 2 des données.

Ce travail consiste à modéliser mathématiquement la consommation d'un moteur d'avion. 

On veut pouvoir comparer les moteurs et comparer les missions ou les phases de vols pour essayer de comprendre la consommation.

## Description du dataset.

Pour réaliser ce modèle on va utiliser les données stockées dans le dataset Kaggle [dfdr1000](https://www.kaggle.com/datasets/jrmlac/dfdr1000).

Ces données consistent en trois fichier HDF5 (d'extension .h5) correspondant chacun à un avion et ses 1000 premiers trajet.

Ces fichiers ont étés créés à l'aide de Pandas en utilisant la commandes `HDFStore` ou la méthode `to_hdf` d'un DataFrame. Ils peuvent donc être lus facilement à l'aide de la fonction `read_hdf` de Pandas.

### Composition des fichiers.

Chaque élément d'un de ces fichiers HDF est un vol stocké sous forme de DataFrame. Pour avoir la liste des vols vous pouvez demander la liste des clés au HDFStore

    with pd.HDFStore(storename, mode='r') as store:
        records = store.keys()

ou utiliser le package h5py qui donne des accès plus rapide au fichier HDF5, mais est moins pratique pour la gestion des métadonnées associées à chaque DataFrame Pandas.

Vous avez ausi quelques exemples d'utilisation de ces données dans le package [tabata](https://github.com/jee51/tabata) et son module opset.py.

### Variables capitalisés pendant chaque vol.

Chaque élément d'un des fichiers est donc un vol.

    df = pd.read_hdf(storename,'record_18')

Les vols sont donc stockés dans des DataFrames avec en index temporel le nombre de secondes écoulées depuis l'alimentation du calculateur et comme colonnes une série de mesures faites pendant le vol.

Durant chaque vol on enregistre des données de l'avion et aussi des mesures faites sur chacun des deux moteurs. Pour distinguer ces mesures les suffixes _1 et _2 sont utilisés respectivement pour le moteur gauche et le moteur droit. (On notera _# ci dessous pour ne pas avoir à distinguer les deux moteurs.)

Certaines mesures sont prises à différents endroits du moteur, ces endroits s'appellent des **stations**, c'est le cas des préessions et températures.

* Pi : pressure
* Ti : temperature

L'indice "i" étant la position de la mesure, 0 correspond à l'avant (avant le fan), 5 à l'arrière (après la tuyère), la station 3 correspond à une mesure juste avant la chambre de combustion.

| Variable [unité] | Description |
|:---------|:------------|
| ALT [ft] | Altitude |
| TAT [deg C] | Total Air Température (mesurée par l'avion) |
| M [Mach] | Mach |
| EGT_# [deg C] | Exhaust Gaz Temperature |
| FMV_# [mm] | Fuel Metering Valve |
| HPTACC_# [%] | High Pressure Turbine Automatic Clearance Control
| N1_# [% rpm] | Speed of secondary shaft (fan) |
| N2_# [% rpm] | Speed of primary shaft (core) |
| NAIV_# [bool] | Anti Ice Vanne |
| P0_# [psia] | Pression en entrée |
| PRV_# [bool] | Bleed (taxi) |
| PS3_# [psia] | Static pressure |
| PT2_# [mbar] | Pressure |
| P_OIL_# [psi] | Oil pressure |
| Q_# [lb/h] | Fuel flow |
| T1_# [deg C] | Température au niveau du fan |
| T2_# [deg C] | Température après le booster |
| T3_# [deg C] | Température en sortie du compresseur et avant la chambre de combustion |
| T5_# [deg C] | Température de l'air dans la tuyère |
| TBV_# [%] | Transfer Bleet Valve |
| TCASE_# [deg C] | Case temperature |
| TLA_# [deg] | Level Angle |
| T_OIL_# [deg C] | Oil temperature |
| VBV_# [mm] | Variable Bleed Valve |
| VIB_AN1_# [mils] | Forward Vibration around N1 frequency |
| VIB_AN2_# [ips] | Forward Vibration around N2 frequency |
| VIB_BN1_# [mils] | Gearbox Vibrations around N1 frequency |
| VIB_BN2_# [ips] | Gearbox Vibrations around N2 frequency |
| VSV_# [mm] | Variable Stator Vannes |

## Programme de travail

1. Accéder aux données, les afficher.
2. Construire une table de synthèse avec des indicateurs pertinents par vol.
3. Nettoyer et normaliser les données.
4. Etudier la prédiction de la consommation globale Q_#.
5. Observer l'évolution vol après vol.
6. Chercher des indicateurs influents, diminuer les incertitudes.
7. Travailler sur un modèle local du débit au cours du vol.
8. Comparer les moteurs.
9. Catégoriser les missions.
10. Une fois un modèle construit, rechercher pourquoi certains vols (ou moteurs) consomment plus (ou moins) que la normale.

...
