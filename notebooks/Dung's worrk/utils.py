import numpy as np
import pandas as pd
import os
from tabata import Opset
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold

'''
    Changelog 19/1: 
        1. Modified the detect_phase() function:
            *Changed the selection of taxi phase to taking two set of index which is on two side of the "cruise_pos"
            "cruise_pos" choose the first position where the aircraft has highest altitude,
            tackling the problem that appears when a flight spends almost half of its journey on taxi
        2. Add a function extend():
            *This function take a position and an array as an Arguments, an extend to both side, and stop 
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
    
'''
def detect_phase(df, threshold):
    '''
        Extracting rules:
        df['M [Mach]'] == 0 => taxi
        df['ALT [ft]] == threshold * max altitude => cruise (because using alt is more stable than using Mach)
        other = climb/descend
        ----------------
        Arguments
        ----------------
            df: flight dataframe
            threshold: threshold for extracting cruising phase
        ----------------
        Return
        ----------------
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
        print('Record is incomplete')
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

def get_consumption(ac, phase: str = 'all', threshold: int = 0.05):
    '''
        ----------------
        Arguments: 
        ----------------
            ac: .h5 files of flight recordings
            phase: str - one of 'all','taxi','taxi1', 'taxi2', 'climb','cruise','descend'
            threshold: threshold for extracting cruising phase 
        ----------------
        Return:
        ----------------
            Fuel consumption of specified phase
    '''

    dat = []
    for i, df in enumerate(ac):

        if len(df.columns)>0 and "ALT [ft]" in df.columns:
            
            alt = df["ALT [ft]"]
            Alt_max = max(alt)

            if Alt_max > 20000: # Maxmimum altitude can indicates if a recording is meaningful or not
                
                ## selecting phase index
                phases = detect_phase(df, threshold) # phases = taxi1_idx, climb_idx, cruise_idx, descend_idx, taxi2_idx

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
                elif phase == 'whole_flight':
                    idx = np.arange(0,len(df))  
                else:
                    raise RuntimeError("'phase' must be one of {taxi, taxi1, taxi2, climb, cruise, descend, whole_flight}")
                    
                df_phase = df.iloc[idx] 

                total_weight_engine1 = df_phase['Q_1 [lb/h]'].sum()/(3600*2.205) #(to kg) #consumption is the integral (sum) of consumption rate
                total_weight_engine2 = df_phase['Q_2 [lb/h]'].sum()/(3600*2.205) #(to kg)
                total_weight = total_weight_engine1 + total_weight_engine2
                
                volume1 = total_weight_engine1 /0.73 
                volume2 = total_weight_engine2 /0.73 
                phase_duration = len(df_phase)/3600 # in hour     

                average_egt = np.mean(df_phase['EGT_1 [deg C]']) + np.mean(df_phase['EGT_2 [deg C]'])
                TAT_max = df['TAT [deg C]'].max()
                TAT_min = df['TAT [deg C]'].min() 
                T_oil_range_1 =  df_phase['T_OIL_1 [deg C]'].max() - df_phase['T_OIL_1 [deg C]'].min()
                T_oil_range_2 =  df_phase['T_OIL_2 [deg C]'].max() - df_phase['T_OIL_2 [deg C]'].min()
                Mach_max = df["M [Mach]"].max()
                static_pressure = np.mean(df['PS3_1 [psia]'])

                try:
                    slope = (df_phase['ALT [ft]'].max() - df_phase['ALT [ft]'].min())/len(df_phase)
                except: 
                    slope = 0

                dat+= [[ac.storename, 'Left', i, phase_duration, Alt_max, Mach_max, slope, average_egt, static_pressure, TAT_max, TAT_min, T_oil_range_1, volume1, total_weight]]
                dat+= [[ac.storename, 'Right', i, phase_duration, Alt_max, Mach_max, slope, average_egt, static_pressure, TAT_max, TAT_min, T_oil_range_2, volume2, total_weight]]
    dataframe = pd.DataFrame(dat, columns = ['AC', 'ENG', 'Flight', 'Leg', 'Alt_max', 'M_max', 'Alt_slope', 'Avg_EGT', 'PS3',
                                             'TAT_max', 'TAT_min', 'T_oil_range', 'Volume', 'Weight'])
    
    return dataframe

class process_h5():
    """
    Un modèle réalisant un apprentissage sur une série de données et proposant une fonction de 
        Paramètres: 
            ac, acs: One aircraft flights or a liste of aircraft flights.
            phases: list of phases (None for all phases)
            altitude_threshold: threshold for extracting cruising phase 
            width: un paramètre correspondant à la largeur d'un filtrage pour le calcul de l'erreur relative 
        Méthodes:
            __init__(altitude_threshold) : creation du modèle.
            fit(acs, phases) : apprentissage.
            predict(ac) : calcul de la consommation estimée.
            score(ac, width) : estimation de l'erreur relative moyenne pour un avion.
    """
    
    def __init__(self, data_path = './data'):
        '''
        -------------
        Arguments
        -------------
        data_path: path to the aircraft *.h5 data
        '''
        self.data_path = data_path 

    def read_h5(self, name = 'all'):
        '''
        + Reading the database by Opset() class
            - Each .h5 files contains a number of flight info recordings of an aircraft
        + register the following attributes:
            - self.aircrafts: all aircrafts names
            - self.opsets: all aircrafts Opset data
        -------------
        Arguments
        -------------
            name: str: read all *.h5 files in data_path if name == 'all', else read specified name
        '''
        if name == 'all':
            self.opsets= {}
            self.aircrafts = os.listdir(self.data_path)
            for name in self.aircrafts:
                ac = Opset(os.path.join(self.data_path, name))
                self.opsets[name] = ac 
        else: 
            self.aircrafts = [name]
            self.opsets= {name: Opset(os.path.join(self.data_path, self.aircrafts[0]))}

    def construct_dataset(self, phases: str, ac: str = 'all', threshold: float = 0.05):
        '''
        Construct a dataframe for total consumption analysis
        -------------
        Arguments
        -------------
            phase: str: Phases to analysis. Must be one or a list of 'taxi', 'climb', 'cruise' or 'descend' or 'whole_flight'
            ac: str: Aircraft to analysis. Analyse all aircraft if ac == 'all', else analyse the given name.
            threshold: float: threshold for extracting cruising phase 
            
        '''
        if isinstance(phases, str):
            self.phases = [phases]  
        else:
            self.phases = phases

        all_ = []
        for ac in self.aircrafts:
            ac_data = self.opsets[ac]
            for p in self.phases:
                all_.append(get_consumption(ac_data, phase=p, threshold=threshold))

        dataframe = pd.concat([d for d in all_], axis=0, ignore_index=True)
        '''
        Notice: Here I only consider left engine data because the data for left and right engines are quite similar.
                We can consider the Right engine later, too.
        '''
        df = dataframe[dataframe['ENG'] == 'Left'].drop(columns = ['Flight', 'AC', 'ENG', 'Volume'])
        df.index = np.arange(len(df))

        self.df = df 
        return df

    def plot_var_distribution(self):
        '''
        Plot the distribution of the indicators given in self.df
            
        '''
        plt.figure(figsize=(15,5))
        i = 0 
        for col in self.df.columns:
            i+=1
            plt.subplot(2,5,i)
            plt.hist(self.df[col],bins = 30)
            plt.title(col)
        plt.subplots_adjust(hspace=0.5)
        plt.show()

    def preprocess(self, df):
        '''
        Handle nans, zeros and scale
            
        '''
        df.dropna(inplace = True) # drop na values
        df = df[df['Weight'] != 0] # drop weight = 0
        scaler = MinMaxScaler()
        scaler.fit(df.drop(columns = ['Weight']))
        df_transformed = scaler.transform(df.drop(columns = ['Weight']))
        df_transformed = np.concatenate([df_transformed, df[['Weight']].to_numpy()] ,axis=1) # Merge in numpy to ensure correct concatenation
        df_transformed = pd.DataFrame(df_transformed)
        df_transformed.columns = df.columns
        return df_transformed


class RelativeIqr():
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

def cross_validate_classifier(models: list, df_input, target):
    i=0
    for clf in models:
        i+=1
        print(f'Params set{i}')
        n_splits = 10
        fold = StratifiedKFold(n_splits=n_splits)
        splits = fold.split(df_input,target)
        kfold_acc = []
        kfold_b_acc = []
        kfold_f1 = []
        for train_idx, test_idx in splits:
            X_train, X_test, y_train, y_test = df_input.iloc[train_idx,:], df_input.iloc[test_idx,:], target.iloc[train_idx], target.iloc[test_idx]
            clf.fit(X_train,y_train)
            pred = clf.predict(X_test)
            acc = accuracy_score(y_test,pred)
            b_acc = balanced_accuracy_score(y_test,pred)
            f1 = f1_score(y_test,pred,average='weighted')
            kfold_acc.append(acc)
            kfold_b_acc.append(b_acc)
            kfold_f1.append(f1)

        mean_acc = np.round(np.mean(kfold_acc),3)
        mean_b_acc = np.round(np.mean(kfold_b_acc),3)
        mean_f1 = np.round(np.mean(kfold_f1),3)

        std_acc = np.round(np.std(kfold_acc),3)
        std_b_acc = np.round(np.std(kfold_b_acc),3)
        std_f1 = np.round(np.std(kfold_f1),3)

        print(f'{n_splits} - fold Accuracy: {mean_acc} +- {std_acc}, Balanced accuracy: {mean_b_acc} +- {std_b_acc}, f1: {mean_f1} +- {std_f1}' )