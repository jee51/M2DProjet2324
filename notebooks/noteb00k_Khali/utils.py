import numpy as np
import pandas as pd

def detect_phase(df, altitude_threshold = 0.95):
    '''
        Extracting rules:
        df['M [Mach]'] == 0 => taxi
        df['ALT [ft]] == threshold * max altitude => cruise (because using alt is more stable than using Mach)
        other = climb/descend

        Input: 
            df: flight dataframe
            altitude_threshold: threshold for extracting cruising phase
        Output:
            Couple of start and end indexes for each spécific phase in order of flight sequence: taxi1 (out), climb, cruise, descend, taxi2 (in).
    '''
    #Get taxi idx
    #There are 2 taxi phases
    mc = df['M [Mach]']
    idx = mc [ mc == 0 ].index
    idx1 = idx[idx < len(mc)//2]
    idx2 = idx[idx > len(mc)//2]

    if len(idx1) == 0 or len(idx2) == 0:
        print('Record is incomplete')
        return False
    else:
        taxi1_idx = min(idx1), max(idx1)
        taxi2_idx = min(idx2), max(idx2)

    #Get cruise idx
    a = df['ALT [ft]']
    idx = a [ ( a > max(a)*(altitude_threshold) ) ].index
    cruise_idx = min(idx), max(idx)

    #Get climb idx
    climb_idx = taxi1_idx[1], cruise_idx[0]
    
    #Get descend idx
    descend_idx = cruise_idx[1], taxi2_idx[0]

    return taxi1_idx, climb_idx, cruise_idx, descend_idx, taxi2_idx 

'''
def get_consumption(ac,phase: str = None, altitude_threshold: int = 0.95):
    
        Input: 
            ac: .h5 files of flight recordings
            phase: None (the whole flight) or one of 'taxi','taxi1', 'taxi2', 'climb','cruise','descend'
            altitude_threshold: threshold for extracting cruising phase 
        Output:
            A DataFrame with conumns: ['Aircraft', 'Engine', 'Flight', 'Phase duration', 'Alt_max', 'Mach_max', 'Total consumption', 'Consumption volume']
            Total consumption: the total weight of fuel used by the aircraft.
            Consumption volume: the volume (in liters) of fuel used by this specific engine.
    

    dat = []
    for i, df in enumerate(ac):

        if len(df.columns)>0 and "ALT [ft]" in df.columns:
            
            alt = df["ALT [ft]"]
            Alt_max = max(alt)

            if Alt_max > 20000:
                
                ## selecting phase index
                phases = detect_phase(df, altitude_threshold) # phases = taxi1_idx, climb_idx, cruise_idx, descend_idx, taxi2_idx

                if phases == False:
                    print(i)
                    continue
                else:
                    taxi1_idx, climb_idx, cruise_idx, descend_idx, taxi2_idx = phases

                if phase == 'taxi':
                    idx = np.concatenate([np.arange(taxi1_idx[0],taxi1_idx[1]),
                                          np.arange(taxi2_idx[0],taxi2_idx[1])])
                elif phase == 'taxi1':
                    idx = np.arange(taxi1_idx[0],taxi1_idx[1])
                elif phase == 'taxi2':
                    idx = np.arange(taxi2_idx[0],taxi2_idx[1])
                elif phase == 'climb':
                    idx = np.arange(climb_idx[0],climb_idx[1])
                elif phase == 'cruise':
                    idx = np.arange(cruise_idx[0],cruise_idx[1])
                elif phase == 'descend':
                    idx = np.arange(descend_idx[0],descend_idx[1])    
                else:
                    idx = np.arange(0,len(df))  
                            
                df_phase = df.iloc[idx] 

                consumption_engine1 = df_phase['Q_1 [lb/h]'].sum()/(3600*2.205) #(to kg)
                consumption_engine2 = df_phase['Q_2 [lb/h]'].sum()/(3600*2.205) #(to kg)
                total_consumption = consumption_engine1 + consumption_engine2

                C1 = consumption_engine1/0.73 
                C2 = consumption_engine2/0.73 

                phase_duration = len(df_phase)/3600 # in hour        
                Mach_max = df["M [Mach]"].max()
                
                #temperature huile au decollage 
                dat+= [[ac.storename, 'Left', i, phase_duration, Alt_max, Mach_max, total_consumption, C1]]
                dat+= [[ac.storename, 'Right', i, phase_duration, Alt_max, Mach_max, total_consumption, C2]]

    dataframe = pd.DataFrame(dat,columns = ['Aircraft', 'Engine', 'Flight', 'Phase duration', 
                                            'Alt_max', 'Mach_max', 'Total consumption', 'Consumption volume'])
    
    return dataframe
    '''

def get_consumption(ac,phase: str = None, altitude_threshold: int = 0.95):
    '''
        Input:
            ac: .h5 files of flight recordings
            phase: None (the whole flight) or one of 'taxi','taxi1', 'taxi2', 'climb','cruise','descend'
            altitude_threshold: threshold for extracting cruising phase
        Output:
            A DataFrame with conumns: ['Aircraft', 'Engine', 'Flight', 'Phase duration', 'Alt_max', 'Mach_max', 'Total consumption', 'Consumption volume']
            Total consumption: the total weight of fuel used by the aircraft.
            Consumption volume: the volume (in liters) of fuel used by this specific engine.
    '''
    dat = []
    for i, df in enumerate(ac):
        if len(df.columns)>0 and "ALT [ft]" in df.columns:
            alt = df["ALT [ft]"]
            Alt_max = max(alt)
            if Alt_max > 20000:
                ## selecting phase index
                phases = detect_phase(df, altitude_threshold) # phases = taxi1_idx, climb_idx, cruise_idx, descend_idx, taxi2_idx
                if phases == False:
                    print(i)
                    continue
                else:
                    taxi1_idx, climb_idx, cruise_idx, descend_idx, taxi2_idx = phases
                    
                # temperature huile décollage
                temp_engine1 = df.iloc[taxi1_idx[1]]['T_OIL_1 [deg C]']
                temp_engine2 = df.iloc[taxi1_idx[1]]['T_OIL_2 [deg C]']
                
                if phase == 'taxi':
                    idx = np.concatenate([np.arange(taxi1_idx[0],taxi1_idx[1]),
                                          np.arange(taxi2_idx[0],taxi2_idx[1])])
                elif phase == 'taxi1':
                    idx = np.arange(taxi1_idx[0],taxi1_idx[1])
                elif phase == 'taxi2':
                    idx = np.arange(taxi2_idx[0],taxi2_idx[1])
                elif phase == 'climb':
                    idx = np.arange(climb_idx[0],climb_idx[1])
                elif phase == 'cruise':
                    idx = np.arange(cruise_idx[0],cruise_idx[1])
                elif phase == 'descend':
                    idx = np.arange(descend_idx[0],descend_idx[1])    
                else:
                    idx = np.arange(0,len(df))  
                df_phase = df.iloc[idx]
                consumption_engine1 = df_phase['Q_1 [lb/h]'].sum()/(3600*2.205) #(to kg)
                consumption_engine2 = df_phase['Q_2 [lb/h]'].sum()/(3600*2.205) #(to kg)
                total_consumption = consumption_engine1 + consumption_engine2
                C1 = consumption_engine1/0.73
                C2 = consumption_engine2/0.73
                phase_duration = len(df_phase)/3600 # in hour        
                Mach_max = df["M [Mach]"].max()
                
                #TLA
                tla_1 = df_phase['TLA_1 [deg]'].unique().shape[0]
                tla_2 = df_phase['TLA_2 [deg]'].unique().shape[0]
                # NAI
                naiv_1 = df_phase['NAIV_2 [bool]'].sum()
                naiv_2 = df_phase['NAIV_2 [bool]'].sum()

                dat+= [[ac.storename, 'Left', i, phase_duration, Alt_max,
                        Mach_max, total_consumption, C1 , temp_engine1 ,tla_1 , naiv_1]]
                dat+= [[ac.storename, 'Right', i, phase_duration, Alt_max,
                        Mach_max, total_consumption, C2 , temp_engine2 , tla_2, naiv_2]]

    dataframe = pd.DataFrame(dat,columns = ['Aircraft', 'Engine', 'Flight', 'Phase duration',
                                            'Alt_max', 'Mach_max', 'Total consumption',
                                            'Consumption volume' ,'Temp engine' , 'TLA' , 'NAIV' ])
    return dataframe


