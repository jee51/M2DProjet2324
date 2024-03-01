import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats



'''
    Changelog 19/01: 
        1. Modified the detect_phase() function:
            *Changed the selection of taxi phase to taking two set of index which is on two side of the "cruise_pos"
            "cruise_pos" choose the first position where the aircraft has highest altitude,
            tackling the problem that appears when a flight spends almost half of its journey on taxi
        2. Add a function extend():
            *This function take a position and an array as an input, an extend to both side, and stop 
            when meet a sudden change in the array. I designed it to make a better extraction of the 
            cruise phase, but the performance is not (yet?) significant. 
            *The idea is simple: extend to both side with a fixed step, and when meet a big drop (increase),
            reduce the step size, and check the next 3 time-frame to see if it is actually a drop, or a noise 
            during travelling. Stop when the drop (increase) is confirmed.
        3. Modify the get_consumption() to add several new variables:
            + TAT_max/min: Max/min Total Air Temp
            + T_Oil_Range: The range between the lowest and highest oil temp of each engine
            + Avg_EGT: Average entrance temp
            + Alt_slope: The slope of the altitude when climbing.

    Changelog 25/01:
        Modified the get_consumption() function to:
            + return the aircrafts name as "AC01, AC02,, ..."
            + rename the variable "Duration" as "Leg_phase"
            + add the variable "Leg_flight": duration of the flight
            + add the variable "phase", referring to the phase considered

    Changelog 09/02:
            + Modified the get_consumption() function to add variables: "TLA_deg", "NAIV_bool"
            + Assign the right values to variables 

    
'''
def detect_phase(df, threshold):
    '''
        Extracting rules:
        df['M [Mach]'] == 0 => taxi
        df['ALT [ft]] == threshold * max altitude => cruise (because using alt is more stable than using Mach)
        other = climb/descend

        Input: 
            df: flight dataframe
            look: 
            threshold: threshold for extracting cruising phase
        Output:
            Fuel consumption of specified phase

    '''
    #Get taxi idx
    #There are 2 taxi phases
    mc = df['M [Mach]']
    cruise_pos = df['ALT [ft]'].idxmax() 
    #Last time I took from the middle of the recording resulting in wrong extraction 
    # of some flights that has very long first taxi phase
    idx = mc [ mc == 0 ].index # both phases indices
    idx1 = idx[idx < cruise_pos] #one taxi phase before cruise
    idx2 = idx[idx > cruise_pos] #another one after cruise
    
    if len(idx1) == 0 or len(idx2) == 0: #If the record is incomplete
        # print('Record is incomplete')
        return False
    else:
        taxi1_idx = min(idx1), max(idx1)
        taxi2_idx = min(idx2), max(idx2)
    
    #Get cruise idx
    # cruise_idx = extend(cruise_pos,df['ALT [ft]'], look, threshold)
    a = df['ALT [ft]']
    idx = a [ ( a > max(a)*(1 - threshold) ) ].index
    cruise_idx = min(idx), max(idx)

    #Get climb idx
    climb_idx = taxi1_idx[1], cruise_idx[0]
    #Get descend idx
    descend_idx = cruise_idx[1], taxi2_idx[0]

    return taxi1_idx, climb_idx, cruise_idx, descend_idx, taxi2_idx 


def get_consumption(ac, phase: str = None, threshold: int = 0.05):
    '''
        Input: 
            ac: .h5 files of flight recordings
            phase: None (the whole flight) or one of 'taxi','taxi1', 'taxi2', 'climb','cruise','descend'
            altitude_threshold: threshold for extracting cruising phase 
        Output:
            Fuel consumption of specified phase
    '''

    dat = []
    LB2KG = 0.453592  # kg/lb 
    KDENS = 0.73      # kg/l
    for i, df in enumerate(ac):

        if len(df.columns)>0 and "ALT [ft]" in df.columns:
            
            alt = df["ALT [ft]"]
            Alt_max = max(alt)
            

            if Alt_max > 20000: # Maxmimum altitude can indicates if a recording is meaningful or not
                
                ## selecting phase index
                phases = detect_phase(df, threshold) # phases = taxi1_idx, climb_idx, cruise_idx, descend_idx, taxi2_idx

                if phases == False:
                    # print(i)
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

                Q1 = df_phase["Q_1 [lb/h]"].sum()/3600.0 # en lb
                Q2 = df_phase["Q_2 [lb/h]"].sum()/3600.0
                total_weight_engine1 = Q1*LB2KG   # en kg
                total_weight_engine2 = Q2*LB2KG
                total_weight = total_weight_engine1 + total_weight_engine2
                
                volume1 = total_weight_engine1 / KDENS  # en l
                volume2 = total_weight_engine2 / KDENS
                phase_duration = len(df_phase)/3600.0 # in hour     
                average_egt = np.mean(df_phase['EGT_1 [deg C]']) + np.mean(df_phase['EGT_2 [deg C]'])
                TAT_max = df['TAT [deg C]'].max()
                TAT_min = df['TAT [deg C]'].min() 
                T_oil_range_1 =  df_phase['T_OIL_1 [deg C]'].max() - df_phase['T_OIL_1 [deg C]'].min()
                T_oil_range_2 =  df_phase['T_OIL_2 [deg C]'].max() - df_phase['T_OIL_2 [deg C]'].min()
                Mach_max = df['M [Mach]'].max()
                try:
                    slope = (df_phase['ALT [ft]'].max() - df_phase['ALT [ft]'].min())/len(df_phase)
                except: 
                    slope = 0

                #TLA
                tla_1 = df_phase['TLA_1 [deg]'].unique().shape[0]
                tla_2 = df_phase['TLA_2 [deg]'].unique().shape[0]
                # NAI
                naiv_1 = df_phase['NAIV_1 [bool]'].sum()
                naiv_2 = df_phase['NAIV_2 [bool]'].sum()

                Leg = len(df)/3600.0 # En h
                dat+= [['AC'+ac.storename[-5:-3], 'Left', i, phase, Leg, phase_duration, Alt_max, slope, average_egt, TAT_max, TAT_min, T_oil_range_1, Mach_max, tla_1, naiv_1, volume1, total_weight]]
                dat+= [['AC'+ac.storename[-5:-3], 'Right', i, phase, Leg, phase_duration, Alt_max, slope, average_egt, TAT_max, TAT_min, T_oil_range_2, Mach_max, tla_2, naiv_2, volume2, total_weight]]

    dataframe = pd.DataFrame(dat,columns = ['AC', 'ENG', 'Flight', 'Phase', 'Leg_flight_H', 'Leg_phase_H', 'Alt_max_Ft', 'Alt_slope', 'Avg_egt',
                                            'TAT_max', 'TAT_min', 'T_oil_range', 'M_max', 'TLA', 'NAIV', 'Volume_L', 'Weight_Kg'])
    

                
    
    return dataframe


def extend(position, array, look, threshold):
    # This function extend the from the input position to the left and right
    # to find the cruise phase
    left_pos,right_pos = position, position
    # Search left position
    # l = 0
    while True:
        avg_left = np.mean(array[left_pos - look:left_pos])
        relative_dif = np.abs(avg_left - array[left_pos]/array[left_pos])
        if relative_dif < threshold:
            left_pos -= look #translate to the left
        else: #check the next 3 interval to see the trend
            next_five_mean = [np.mean(array[left_pos - (i+1)*look : left_pos - i*look]) for i in range(3)] 
            next_rel_dif = [np.abs(next_five_mean[i] - array[left_pos - i*look]/array[left_pos - i*look]) for i in range(3)]
            if np.mean(next_rel_dif) < threshold:
                left_pos -= look//10
            else:
                # print(l)
                break
        # l+=1
    # r = 0
    # Search right position
    while True:
        avg_right = np.mean(array[right_pos : right_pos+look])
        relative_dif = np.abs(avg_right - array[right_pos]/array[right_pos])
        if relative_dif < threshold:
            right_pos += look #translate to the right
        else: #check the next 3 interval to see the trend
            next_five_mean = [np.mean(array[right_pos + i*look : right_pos + (i+1)*look]) for i in range(3)] 
            next_rel_dif = [np.abs(next_five_mean[i] - array[right_pos + i*look])/array[right_pos + i*look] for i in range(3)]
            if np.mean(next_rel_dif) < threshold:
                right_pos += look//10
            else:
                # print(r)
                break
        # r+=1
    return left_pos, right_pos


def plot_residuals(res, title):
    """
    Plot graphics to analyze residuals

    res : a trained model object from statsmodels
    """

    residus = res.resid
    predicted_values = res.fittedvalues
    
    fig = plt.figure(figsize=(20,6))

    ax1 = fig.add_subplot(1, 3, 1)
    plt.hist(residus, bins=30, edgecolor='black')
    ax1.set_xlabel('Residuals')
    ax1.set_xlabel('Frequence')
    ax1.set_title('Histogram of residuals')

    ax2 = fig.add_subplot(1, 3, 2)
    plt.scatter(predicted_values, residus, s=15)
    ax2.set_xlabel('Predicted values')
    ax2.set_ylabel('Residuals')
    plt.axhline(y=0, color='red', linestyle='--')  # Ajout d'une ligne à zéro pour la référence
    ax2.set_title('Scatter plot of residuals')

    ax3 = fig.add_subplot(1, 3, 3)
    stats.probplot(residus, dist="norm", plot=plt)
    ax3.set_xlabel('Theoretical quantiles')
    ax3.set_ylabel('Residuals quantiles')
    ax3.set_title('QQ-residual plot')

    plt.suptitle(title, y = 1.03, fontsize=15)

    plt.show()
    plt.tight_layout()
    plt.close()


class RelativeIqr:
    """
        Une classe qui calcule les scores relatifs ou
    """
    def __init__(self,y, hy, c=95, p=5):
        """
            Calcul d'un score relatif qui utilise l'écart entre les bornes d'une enveloppe correspondant à un intervalle de confiance. L'enveloppe est calculée pour chaque point par les bornes d'un intervalle de confiance d'erreurs relatives pour des observation proches en valeur absolue. La proximité est donnée en proportion (pourcentage) de valeur nominale de l'observation. Par exemple si l'observation est donnée en litre et varie de 600 à 5000 litres, 10% correspond à (5000-500)/10 soit 450 litres près.

            inputs :
                y  - la valeur réelle de l'observation (p.ex. la consommation).
                hy - la valeur prédite par le modèle.

            paramètre : 
                c - la précision de l'intervalle de confiance pour l'écart relatif calculé (par défaut 95%).
                p  - la précision relative pour le calcul de l'enveloppe (par défaut 5%).
        """

        self.p = p
        self.c = c
        self.y = y
        self.hy = hy

        q = (100-c)/2
        w = (max(hy)-min(hy))*p/100.0

        r = (hy-y)/y
        self.relative_iqr = 100*(np.diff(np.percentile(r,[q, 100-q]))).item()

        up = np.zeros(len(y))
        dn = np.zeros(len(y))

        dy = y-hy
        for i, yy in enumerate(y):
            j = np.argwhere(np.abs(hy-yy)<=w)
            dn[i], up[i] = np.percentile(dy[j],[2.5, 97.5])

        out = np.zeros(len(y))
        out[y>hy+up] =  1
        out[y<hy+dn] = -1

        self.up = up
        self.dn = dn
        self.enveloppe_iqr = 100*np.mean((up-dn)/y)
        self.out = out

    def score(self,enveloppe=True):
        """
            Le score correspondant soit au calcul relatif soit au calcul avec enveloppe.

            Pour le calcul relatif : la largeur de l'intervalle de confiance symétrique sur l'erreur relative. Le résultat est exprimé en pourcentage (entre 0 et 100).

            Pour le calcul avec enveloppe : la largeur de l'intervalle de confiance symétrique sur l'erreur relative. Le résultat est exprimé en pourcentage (entre 0 et 100).
        """
        if enveloppe:
            return self.enveloppe_iqr
        else:
            return self.relative_iqr
    
    def plot(self):
        """
            Cette fonction affiche l'enveloppe calculée pour le calcul du score relative_enveloppe_iqr.
        """
        y = self.y
        hy = self.hy
        up = self.up
        dn = self.dn

        i = np.argsort(hy)

        plt.fill_between(hy[i], hy[i]+up[i], hy[i]+dn[i], color='lightgreen', alpha=0.9)
        plt.plot(hy[i],y[i],'b.', alpha=0.1)
        plt.ylabel('Observed')
        plt.xlabel('Predicted')
        plt.title(f"Relative enveloppe with {self.c:.0f}% confidence and local proximity {self.p:.0f}%.")