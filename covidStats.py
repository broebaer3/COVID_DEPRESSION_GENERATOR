import numpy as np
import matplotlib.pyplot as plt
import pandas as pandas
import os
import datetime

#-----User Inputs-----
# statesInterest = ['New York','Pennsylvania','New Jersey','Maryland','Alabama','Louisiana','Colorado','California','Washington','Illinois']; #a selection of states
statesInterest =['USA']; #combine every state
# statesInterest =['All']; #every state [New York City is treated as its own state to the CDC]
# statesInterest =['Illinois']; #single state
#All does all states, USA combines all into USA
weekCutoff = 23; #cut off at week 15 b/c out of data basically

FLG_compareToHistorical = 1; #0 compares uncounted to current year estimation based on an average from 1/7/2020 to 3/1/2020
    #1 compares uncounted to the historical average [good for very populated states/entire USA]
FLG_yearsForHistorical = [2019,2019]; #range of years to average together. Possible range is 2014 to 2019 due to 2014 is as far back as CDC data is and 2019 is right before now
    #[2019,2019] would only show 2019 with no averaging, [2018,2018] would only show 2018 with no averaging, etc.
#-----End User Inputs-----

#Plotting prep
weeks = np.arange(1,53); #make a consistent week range (lookin at you week 53)
weeksPlot = weeks/52*12; #convert to months, some days may be lost but that's a risk I'm willing to take (they'd be folded into other weeks in actuality)

#By using this site
#https://wonder.cdc.gov/ucd-icd10.html
#and it was painful, each are the totals for 2014-2018 over Jan-May [don't know how to automate this for other states, I click the state and dates and download a text file and read it with my eyes]
deaths_influenzaPneumonia_FL = np.mean(np.array([1231,1338,1352,1408,1707])); #2014/2015/2016/2017/2018
deaths_influenzaPneumonia_KY = np.mean(np.array([473,484,437,497,585])); #2014/2015/2016/2017/2018

#==================================Import the data==================================  
#from https://data.cdc.gov/NCHS/Provisional-COVID-19-Death-Counts-by-Week-Ending-D/r8kw-7aab
data_currentNameAlt = 'Provisional_COVID-19_Death_Counts_by_Week_Ending_Date_and_State.csv'
#from https://data.cdc.gov/NCHS/Weekly-Counts-of-Deaths-by-State-and-Select-Causes/3yf8-kanr
data_historicalName = 'Weekly_Counts_of_Deaths_by_State_and_Select_Causes__2014-2018.csv';
#from https://data.cdc.gov/NCHS/Weekly-Counts-of-Deaths-by-State-and-Select-Causes/muzy-jte6
data_currentName = 'Weekly_Counts_of_Deaths_by_State_and_Select_Causes__2019-2020.csv';
#from https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series
data_covidName = 'time_series_covid19_deaths_US.csv';
if( os.path.isfile(data_covidName) == False  ): #this can be gotten easily, I won't automate the CDC one cause it's not easy peasy
    from urllib.request import urlretrieve; #import to be able to download
    urlretrieve('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv', data_covidName); #download if needed
#END IF
if( os.path.isfile(data_currentName) == False  ): #this can be gotten easily, I won't automate the CDC one cause it's not easy peasy
    from urllib.request import urlretrieve; #import to be able to download
    urlretrieve('https://data.cdc.gov/api/views/muzy-jte6/rows.csv?accessType=DOWNLOAD&bom=true&format=true', data_currentName); #download if needed
#END IF
if( os.path.isfile(data_historicalName) == False  ): #this can be gotten easily, I won't automate the CDC one cause it's not easy peasy
    from urllib.request import urlretrieve; #import to be able to download
    urlretrieve('https://data.cdc.gov/api/views/3yf8-kanr/rows.csv?accessType=DOWNLOAD&bom=true&format=true', data_historicalName); #download if needed
#END IF
if( os.path.isfile(data_currentNameAlt) == False  ): #this can be gotten easily, I won't automate the CDC one cause it's not easy peasy
    from urllib.request import urlretrieve; #import to be able to download
    urlretrieve('https://data.cdc.gov/api/views/r8kw-7aab/rows.csv?accessType=DOWNLOAD&bom=true&format=true', data_currentNameAlt); #download if needed
#END IF

#import and prep historical data
data_historical = pandas.read_csv(data_historicalName);
states_historical = data_historical['Jurisdiction of Occurrence'].to_numpy();
statesUnique_historical = np.unique(states_historical);
years_historical = data_historical['MMWR Year'].to_numpy();
weeks_historical = data_historical['MMWR Week'].to_numpy();
deaths_historical = data_historical['All  Cause'].to_numpy(); #NOTE THE DOUBLE SPACE!!
deaths_historical_influenzaPneumonia = data_historical['Influenza and pneumonia (J10-J18)'].to_numpy();
#All Cause comes in with commas so it's treated as an object not a number
if( deaths_historical.dtype == 'O' ):
    deaths_historical_object = np.copy(deaths_historical); #copy it over
    deaths_historical = np.int64(np.zeros(deaths_historical_object.shape)); #prep it
    for i in range(0,deaths_historical.size):
        if( pandas.isnull(deaths_historical_object[i]) ): #detect an empty (shows up as a pandas nan weird thing)
            deaths_historical_object[i] = '0'; #make it a string 0
        #END IF
        deaths_historical[i] = np.int64(deaths_historical_object[i].replace(',','')); #make it an integer
    #END FOR i
#END IF
if( deaths_historical_influenzaPneumonia.dtype == 'O' ):
    deaths_historical_object = np.copy(deaths_historical_influenzaPneumonia); #copy it over
    deaths_historical_influenzaPneumonia = np.int64(np.zeros(deaths_historical_object.shape)); #prep it
    for i in range(0,deaths_historical_influenzaPneumonia.size):
        if( pandas.isnull(deaths_historical_object[i]) ): #detect an empty (shows up as a pandas nan weird thing)
            deaths_historical_object[i] = '0'; #make it a string 0
        #END IF
        deaths_historical_influenzaPneumonia[i] = np.int64(deaths_historical_object[i].replace(',','')); #make it an integer
    #END FOR i
#END IF
FLG_combineUSA = 0; #prep flag
#Make sure the states requested are real states
if( (statesInterest[0] == 'All') | (statesInterest[0] == 'USA') ):
    if(statesInterest[0] == 'USA'):
        FLG_combineUSA = 1; #turn flag on
    #END IF
    statesInterest = statesUnique_historical; #set this as the states (it's all the states)
else:
    statesInterest = np.array(statesInterest,dtype=object); #make into a numpy array
    for i in range(0,len(statesInterest)): #run through the state of interest
        testo = np.sum(statesInterest[i] == statesUnique_historical); #count how many are found
        if( testo == 0 ):
            print('The state of interest \"'+str(statesInterest[i])+'\" is NOT a state, unfortunately.\nQuitting, go fix that.srry [spelling?]'); #report mission failure
            sys.exit(); #quit but sys won't be imported so it's double fun
        #END IF
    #END FOR i
#END IF

#import and prep current data
data_current = pandas.read_csv(data_currentName);
states_current = data_current['Jurisdiction of Occurrence'].to_numpy();
#statesUnique_current = np.unique(states_current);
years_current = data_current['MMWR Year'].to_numpy();
weeks_current = data_current['MMWR Week'].to_numpy();
deaths_current = data_current['All Cause'].to_numpy(); #no double space here
deaths_current_influenzaPneumonia = data_current['Influenza and pneumonia (J10-J18)'].to_numpy();
#All Cause comes in with commas so it's treated as an object not a number
if( deaths_current.dtype == 'O' ):
    deaths_current_object = np.copy(deaths_current); #copy it over
    deaths_current = np.int64(np.zeros(deaths_current_object.shape)); #prep it
    for i in range(0,deaths_current.size):
        if( pandas.isnull(deaths_current_object[i]) ): #detect an empty (shows up as a pandas nan weird thing)
            deaths_current_object[i] = '0'; #make it a string 0
        #END IF
        deaths_current[i] = np.int64(deaths_current_object[i].replace(',','')); #make it an integer
    #END FOR i
#END IF
if( deaths_current_influenzaPneumonia.dtype == 'O' ):
    deaths_current_object = np.copy(deaths_current_influenzaPneumonia); #copy it over
    deaths_current_influenzaPneumonia = np.int64(np.zeros(deaths_current_object.shape)); #prep it
    for i in range(0,deaths_current_influenzaPneumonia.size):
        if( pandas.isnull(deaths_current_object[i]) ): #detect an empty (shows up as a pandas nan weird thing)
            deaths_current_object[i] = '0'; #make it a string 0
        #END IF
        deaths_current_influenzaPneumonia[i] = np.int64(deaths_current_object[i].replace(',','')); #make it an integer
    #END FOR i
#END IF
yearOfInterest = years_current.max(); #get the year of interest, which is the latest year
#-----Leap Year Detection-----
if np.mod(yearOfInterest,4) == 0: #leap year
    #-----Leap Year Skipped Detected - next will be 2100-----
    if (np.mod(yearOfInterest,100) == 0) and (np.mod(yearOfInterest,400) != 0):
        yearOfInterest_dayNum = 365; #days
    else:
    #-----Leap Year Confirmed (2000,2004,2008,2012,2016,2020...)-----
        yearOfInterest_dayNum = 366; #days
    #END IF
#-----No leap year detected-----
else: #no leap year if this
    yearOfInterest_dayNum = 365; #days
#END IF
k = years_current < yearOfInterest; #get prev years that are in the current year data
states_historical = np.concatenate( [states_historical,states_current[k]] ); #put it on the historical data
states_current = np.delete(states_current,np.where(k)); #delete the data from current
years_historical = np.concatenate( [years_historical,years_current[k]] ); #put it on the historical data
years_current = np.delete(years_current,np.where(k)); #delete the data from current
weeks_historical = np.concatenate( [weeks_historical,weeks_current[k]] ); #put it on the historical data
weeks_current = np.delete(weeks_current,np.where(k)); #delete the data from current
deaths_historical = np.concatenate( [deaths_historical,deaths_current[k]] ); #put it on the historical data
deaths_current = np.delete(deaths_current,np.where(k)); #delete the data from current
deaths_historical_influenzaPneumonia = np.concatenate( [deaths_historical_influenzaPneumonia,deaths_current_influenzaPneumonia[k]] ); #put it on the historical data
deaths_current_influenzaPneumonia = np.delete(deaths_current_influenzaPneumonia,np.where(k)); #delete the data from current


#import and prep current data alternate CDC numbers for COVID-19/Pneumonia/Influenza
data_currentAlt = pandas.read_csv(data_currentNameAlt);
deaths_currentAlt_pneumonia = data_currentAlt['Pneumonia Deaths'].to_numpy(); #no double space here
deaths_currentAlt_influenza = data_currentAlt['Influenza Deaths'].to_numpy(); #no double space here
deaths_currentAlt_pneumoniaANDcovid = data_currentAlt['Pneumonia and COVID-19 Deaths'].to_numpy(); #no double space here
date_currentAlt_longform = data_currentAlt['Start week'].to_numpy(); #no double space here
states_currentAlt = data_currentAlt['State'].to_numpy(); #no double space here
if( deaths_currentAlt_pneumonia.dtype == 'O' ):
    deaths_current_object = np.copy(deaths_currentAlt_pneumonia); #copy it over
    deaths_currentAlt_pneumonia = np.int64(np.zeros(deaths_current_object.shape)); #prep it
    for i in range(0,deaths_currentAlt_pneumonia.size):
        if( pandas.isnull(deaths_current_object[i]) ): #detect an empty (shows up as a pandas nan weird thing)
            deaths_current_object[i] = '0'; #make it a string 0
        #END IF
        deaths_currentAlt_pneumonia[i] = np.int64(deaths_current_object[i].replace(',','')); #make it an integer
    #END FOR i
#END IF
if( deaths_currentAlt_influenza.dtype == 'O' ):
    deaths_current_object = np.copy(deaths_currentAlt_influenza); #copy it over
    deaths_currentAlt_influenza = np.int64(np.zeros(deaths_current_object.shape)); #prep it
    for i in range(0,deaths_currentAlt_influenza.size):
        if( pandas.isnull(deaths_current_object[i]) ): #detect an empty (shows up as a pandas nan weird thing)
            deaths_current_object[i] = '0'; #make it a string 0
        #END IF
        deaths_currentAlt_influenza[i] = np.int64(deaths_current_object[i].replace(',','')); #make it an integer
    #END FOR i
#END IF
if( deaths_currentAlt_pneumoniaANDcovid.dtype == 'O' ):
    deaths_current_object = np.copy(deaths_currentAlt_pneumoniaANDcovid); #copy it over
    deaths_currentAlt_pneumoniaANDcovid = np.int64(np.zeros(deaths_current_object.shape)); #prep it
    for i in range(0,deaths_currentAlt_pneumoniaANDcovid.size):
        if( pandas.isnull(deaths_current_object[i]) ): #detect an empty (shows up as a pandas nan weird thing)
            deaths_current_object[i] = '0'; #make it a string 0
        #END IF
        deaths_currentAlt_pneumoniaANDcovid[i] = np.int64(deaths_current_object[i].replace(',','')); #make it an integer
    #END FOR i
#END IF
deaths_currentAlt_pneumonia[np.isnan(deaths_currentAlt_pneumonia)] = 0; #remove NaNs cause they cause summing issues
deaths_currentAlt_influenza[np.isnan(deaths_currentAlt_influenza)] = 0; #remove NaNs cause they cause summing issues
deaths_currentAlt_pneumoniaANDcovid[np.isnan(deaths_currentAlt_pneumoniaANDcovid)] = 0; #remove NaNs cause they cause summing issues
#get dates into decimal
def year_fraction(date): #from MattyBOI https://stackoverflow.com/questions/6451655/how-to-convert-python-datetime-dates-to-decimal-float-years
    start = datetime.date(date.year, 1, 1).toordinal();
    year_length = datetime.date(date.year+1, 1, 1).toordinal() - start;
    return date.year + float(date.toordinal() - start) / year_length
#END DEF
date_currentAlt = np.zeros([date_currentAlt_longform.size]); #prep
for i in range(0,date_currentAlt_longform.size):
    date_currentAlt[i] = (year_fraction(datetime.datetime.strptime(date_currentAlt_longform[i],'%m/%d/%Y'))-yearOfInterest)*12; #convert to a fraction of the month
#END FOR i


#import and prep covid data
data_covid = pandas.read_csv(data_covidName);
data_covidColumns = data_covid.columns; #get the column names
data_covidColumnsDates = data_covidColumns[12:]; #get the column dates
states_covid = data_covid['Province_State'].to_numpy();
# def year_fraction(date): #from MattyBOI https://stackoverflow.com/questions/6451655/how-to-convert-python-datetime-dates-to-decimal-float-years
#     start = datetime.date(date.year, 1, 1).toordinal();
#     year_length = datetime.date(date.year+1, 1, 1).toordinal() - start;
#     return date.year + float(date.toordinal() - start) / year_length
# #END DEF
data_covidDates = np.zeros([data_covidColumnsDates.size]); #prep
for i in range(0,data_covidColumnsDates.size):
    data_covidDates[i] = (year_fraction(datetime.datetime.strptime(data_covidColumnsDates[i],'%m/%d/%y'))-yearOfInterest)*12; #convert to a fraction of the month
#END FOR i

#==================================Fix New York==================================
#New York is reported seperately by the CDC - New York and New York City are seperate
#I'm not sure where the line is drawn for New York City boundaries - so it's easier to jam it back into NY
if( (np.any('New York' == statesInterest) == True) & (np.any('New York City' == statesInterest) == False) ):
    k = states_historical == 'New York City';
    kk = states_historical == 'New York';
    deaths_historical[kk] = deaths_historical[kk] + deaths_historical[k]; #add the deaths to New York
    deaths_historical_influenzaPneumonia[kk] = deaths_historical_influenzaPneumonia[kk] + deaths_historical_influenzaPneumonia[k]; #add the deaths to New York
    
    states_historical = np.delete(states_historical,np.where(k==True)[0]); #delete the NYC data
    years_historical = np.delete(years_historical,np.where(k==True)[0]); #delete the NYC data
    weeks_historical = np.delete(weeks_historical,np.where(k==True)[0]); #delete the NYC data
    deaths_historical = np.delete(deaths_historical,np.where(k==True)[0]); #delete the NYC data
    deaths_historical_influenzaPneumonia = np.delete(deaths_historical_influenzaPneumonia,np.where(k==True)[0]); #delete the NYC data
    
    k = states_current == 'New York City';
    kk = states_current == 'New York';
    k2 = np.where(k==True)[0]; #deal with NYC has newer data than NY
    k2 = k2[0:kk.sum()]; #keep only the data that matches NY's data
    deaths_current[kk] = deaths_current[kk] + deaths_current[k2]; #add the deaths to New York
    deaths_current_influenzaPneumonia[kk] = deaths_current_influenzaPneumonia[kk] + deaths_current_influenzaPneumonia[k2]; #add the deaths to New York
    
    states_current = np.delete(states_current,np.where(k==True)[0]); #delete the NYC data
    years_current = np.delete(years_current,np.where(k==True)[0]); #delete the NYC data
    weeks_current = np.delete(weeks_current,np.where(k==True)[0]); #delete the NYC data
    deaths_current = np.delete(deaths_current,np.where(k==True)[0]); #delete the NYC data
    deaths_current_influenzaPneumonia = np.delete(deaths_current_influenzaPneumonia,np.where(k==True)[0]); #delete the NYC data
    
    k = states_currentAlt == 'New York City';
    kk = states_currentAlt == 'New York';
    k2 = np.where(k==True)[0]; #deal with NYC has newer data than NY
    k2 = k2[0:kk.sum()]; #keep only the data that matches NY's data
    deaths_currentAlt_pneumonia[kk] = deaths_currentAlt_pneumonia[kk] + deaths_currentAlt_pneumonia[k2]; #add the deaths to New York
    deaths_currentAlt_influenza[kk] = deaths_currentAlt_influenza[kk] + deaths_currentAlt_influenza[k2]; #add the deaths to New York
    deaths_currentAlt_pneumoniaANDcovid[kk] = deaths_currentAlt_pneumoniaANDcovid[kk] + deaths_currentAlt_pneumoniaANDcovid[k2]; #add the deaths to New York
    
    states_currentAlt = np.delete(states_currentAlt,np.where(k==True)[0]); #delete the NYC data
    date_currentAlt = np.delete(date_currentAlt,np.where(k==True)[0]); #delete the NYC data
    deaths_currentAlt_pneumonia = np.delete(deaths_currentAlt_pneumonia,np.where(k==True)[0]); #delete the NYC data
    deaths_currentAlt_influenza = np.delete(deaths_currentAlt_influenza,np.where(k==True)[0]); #delete the NYC data
    deaths_currentAlt_pneumoniaANDcovid = np.delete(deaths_currentAlt_pneumoniaANDcovid,np.where(k==True)[0]); #delete the NYC data
    
    statesInterest = np.delete(statesInterest,np.where(statesInterest == 'New York City')[0]); #remove the New York City entry
#END IF

#==================================Cull historical years based on user input==================================
k = ~((FLG_yearsForHistorical[0] <= years_historical) & (FLG_yearsForHistorical[-1] >= years_historical)); #get year data to keep
if( np.sum(k) > 0 ):
    states_historical = np.delete(states_historical,np.where(k==True)[0]); #delete the historical years not needed
    years_historical = np.delete(years_historical,np.where(k==True)[0]); #delete the historical years not needed
    weeks_historical = np.delete(weeks_historical,np.where(k==True)[0]); #delete the historical years not needed
    deaths_historical = np.delete(deaths_historical,np.where(k==True)[0]); #delete the historical years not needed
    deaths_historical_influenzaPneumonia = np.delete(deaths_historical_influenzaPneumonia,np.where(k==True)[0]); #delete the historical years not needed
#END IF

#==================================Combine into one country if option is on==================================
if( FLG_combineUSA == 1 ):
    statesUnique_historical = np.unique(states_historical); #get a new one since NYC is gone
    for i in range(0,statesUnique_historical.size):
        k = states_historical == statesUnique_historical[i];
        if( i == 0 ):
            histHolder_deaths_influenzaPneumonia = deaths_historical_influenzaPneumonia[k]; #initialize
            histHolder_deaths = deaths_historical[k]; #initialize
            histHolder_weeks = weeks_historical[k]; #initialize
            histHolder_years = years_historical[k]; #initialize
            histHolder_states = 'USA'; #initialize
        else:
            histHolder_deaths_influenzaPneumonia = histHolder_deaths_influenzaPneumonia + deaths_historical_influenzaPneumonia[k]; #incrementally add
            histHolder_deaths = histHolder_deaths + deaths_historical[k]; #incrementally add
        #END IF
    #END FOR i
    
    deaths_historical_influenzaPneumonia = np.copy(histHolder_deaths_influenzaPneumonia); #replace
    deaths_historical = np.copy(histHolder_deaths); #replace
    years_historical = np.copy(histHolder_years); #replace
    weeks_historical = np.copy(histHolder_weeks); #replace
    states_historical = np.copy(histHolder_states); #replace
    
    for i in range(0,statesUnique_historical.size):
        k = np.where(states_current == statesUnique_historical[i])[0];
        if( i == 0 ):
            histHolder_deaths_influenzaPneumonia = deaths_current_influenzaPneumonia[k]; #initialize
            histHolder_deaths = deaths_current[k]; #initialize
            histHolder_weeks = weeks_current[k]; #initialize
            histHolder_years = years_current[k]; #initialize
            histHolder_states = 'USA'; #initialize
        else:
            if( k.size > histHolder_deaths.size ):
                k = k[0:histHolder_deaths.size]; #cap to size of original initialization (will fail if initial init was bigger than a current state reporting)
                histHolder_deaths = histHolder_deaths + deaths_current[k]; #incrementally add
            elif( k.size < histHolder_deaths.size ):
                histHolder_deaths = histHolder_deaths + np.pad(deaths_current[k],(0,histHolder_deaths.size-k.size)); #incrementally add
            else:
                histHolder_deaths = histHolder_deaths + deaths_current[k]; #incrementally add
            #END IF
            if( k.size > histHolder_deaths_influenzaPneumonia.size ):
                k = k[0:histHolder_deaths_influenzaPneumonia.size]; #cap to size of original initialization (will fail if initial init was bigger than a current state reporting)
                histHolder_deaths_influenzaPneumonia = histHolder_deaths_influenzaPneumonia + deaths_current_influenzaPneumonia[k]; #incrementally add
            elif( k.size < histHolder_deaths_influenzaPneumonia.size ):
                histHolder_deaths_influenzaPneumonia = histHolder_deaths_influenzaPneumonia + np.pad(deaths_current_influenzaPneumonia[k],(0,histHolder_deaths_influenzaPneumonia.size-k.size)); #incrementally add
            else:
                histHolder_deaths_influenzaPneumonia = histHolder_deaths_influenzaPneumonia + deaths_current_influenzaPneumonia[k]; #incrementally add
            #END IF
        #END IF
    #END FOR i
    deaths_current_influenzaPneumonia = np.copy(histHolder_deaths_influenzaPneumonia); #replace
    deaths_current = np.copy(histHolder_deaths); #replace
    years_current = np.copy(histHolder_years); #replace
    weeks_current = np.copy(histHolder_weeks); #replace
    states_current = np.copy(histHolder_states); #replace
    
    for i in range(0,statesUnique_historical.size):
        k = np.where(states_currentAlt == statesUnique_historical[i])[0];
        if( i == 0 ):
            histHolder_deaths_pneumonia = deaths_currentAlt_pneumonia[k]; #initialize
            histHolder_deaths_influenza = deaths_currentAlt_influenza[k]; #initialize
            histHolder_deaths_pneumoniaANDcovid = deaths_currentAlt_pneumoniaANDcovid[k]; #initialize
            histHolder_weeks = date_currentAlt[k]; #initialize
            histHolder_states = 'USA'; #initialize
        else:
            if( k.size > histHolder_deaths_pneumonia.size ):
                k = k[0:histHolder_deaths_pneumonia.size]; #cap to size of original initialization (will fail if initial init was bigger than a current state reporting)
                histHolder_deaths_pneumonia = histHolder_deaths_pneumonia + deaths_currentAlt_pneumonia[k]; #incrementally add
            elif( k.size < histHolder_deaths_pneumonia.size ):
                histHolder_deaths_pneumonia = histHolder_deaths_pneumonia + np.pad(deaths_currentAlt_pneumonia[k],(0,histHolder_deaths_pneumonia.size-k.size)); #incrementally add
            else:
                histHolder_deaths_pneumonia = histHolder_deaths_pneumonia + deaths_currentAlt_pneumonia[k]; #incrementally add
            #END IF
            if( k.size > histHolder_deaths_influenza.size ):
                k = k[0:histHolder_deaths_influenza.size]; #cap to size of original initialization (will fail if initial init was bigger than a current state reporting)
                histHolder_deaths_influenza = histHolder_deaths_influenza + deaths_currentAlt_influenza[k]; #incrementally add
            elif( k.size < histHolder_deaths_influenza.size ):
                histHolder_deaths_influenza = histHolder_deaths_influenza + np.pad(deaths_currentAlt_influenza[k],(0,histHolder_deaths_influenza.size-k.size)); #incrementally add
            else:
                histHolder_deaths_influenza = histHolder_deaths_influenza + deaths_currentAlt_influenza[k]; #incrementally add
            #END IF
            if( k.size > histHolder_deaths_pneumoniaANDcovid.size ):
                k = k[0:histHolder_deaths_pneumoniaANDcovid.size]; #cap to size of original initialization (will fail if initial init was bigger than a current state reporting)
                histHolder_deaths_pneumoniaANDcovid = histHolder_deaths_pneumoniaANDcovid + deaths_currentAlt_pneumoniaANDcovid[k]; #incrementally add
            elif( k.size < histHolder_deaths_pneumoniaANDcovid.size ):
                histHolder_deaths_pneumoniaANDcovid = histHolder_deaths_pneumoniaANDcovid + np.pad(deaths_currentAlt_pneumoniaANDcovid[k],(0,histHolder_deaths_pneumoniaANDcovid.size-k.size)); #incrementally add
            else:
                histHolder_deaths_pneumoniaANDcovid = histHolder_deaths_pneumoniaANDcovid + deaths_currentAlt_pneumoniaANDcovid[k]; #incrementally add
            #END IF
        #END IF
    #END FOR i
    deaths_currentAlt_pneumonia = np.copy(histHolder_deaths_pneumonia); #replace
    deaths_currentAlt_influenza = np.copy(histHolder_deaths_influenza); #replace
    deaths_currentAlt_pneumoniaANDcovid = np.copy(histHolder_deaths_pneumoniaANDcovid); #replace
    date_currentAlt = np.copy(histHolder_weeks); #replace
    states_currentAlt = np.copy(histHolder_states); #replace    
    
    statesInterest = ['USA']; #keep that list lyfe goingoing

    states_covid = np.tile('USA',states_covid.shape); #make all places USA
#END IF


#==================================Crunch the data==================================  
deaths_historicalAvg_influenzaPneumonia = np.zeros([weeks.size,len(statesInterest)]); #preallocate historical data holder
deaths_currentValues_influenzaPneumonia = np.zeros([weeks.size,len(statesInterest)]); #preallocate current data holder
deaths_historicalAvg = np.zeros([weeks.size,len(statesInterest)]); #preallocate historical data holder
deaths_currentValues = np.zeros([weeks.size,len(statesInterest)]); #preallocate current data holder
altSize = np.diff(date_currentAlt) < 0;
if( np.all(~altSize) == True ):
    altSize = date_currentAlt.size; #the excess dates have been removed already and don't need to use diff to find where they repeat
else:
    altSize = np.where(np.diff(date_currentAlt) < 0)[0][0]+1; #use diff to find where it goes negative (restarts the date list)
#END IF
date_currentAltValues = np.zeros([altSize,len(statesInterest)]); #preallocate current data holder
deaths_currentAltValues_pneumonia = np.zeros([altSize,len(statesInterest)]); #preallocate current data holder
deaths_currentAltValues_influenza = np.zeros([altSize,len(statesInterest)]); #preallocate current data holder
deaths_currentAltValues_pneumoniaANDcovid = np.zeros([altSize,len(statesInterest)]); #preallocate current data holder
deaths_currentAltValues_influenzaPneumonia = np.zeros([altSize,len(statesInterest)]); #preallocate current data holder
deaths_covidValues = np.zeros([data_covidColumnsDates.size,len(statesInterest)]); #prealloate covid data holder
deaths_covidValuesOnWeekly = np.zeros([weeks.size,len(statesInterest)]); #prealloate covid data holder
for i in range(0,len(statesInterest)): #run through the state of interest
    #do historical
    k = statesInterest[i] == states_historical; #get where the state we want is
    
    years_historicalCurr = years_historical[k]; #yoink it
    weeks_historicalCurr = weeks_historical[k]; #yoink it
    deaths_historicalCurr = deaths_historical[k]; #yoink it
    deaths_historicalCurr_influenzaPneumonia = deaths_historical_influenzaPneumonia[k]; #yoink it
    
    years_historicalCurrUnique = np.unique(years_historicalCurr); #get unique years
    
    deaths_historicalPrep = np.zeros([weeks.size,years_historicalCurrUnique.size]); #prep holder
    deaths_historicalPrep_influenzaPneumonia = np.zeros([weeks.size,years_historicalCurrUnique.size]); #prep holder
    for j in range(0,years_historicalCurrUnique.size): #run through the historical years
        jk = years_historicalCurrUnique[j] == years_historicalCurr; #get where the current year in current state is
        weeks_historicalCurrCurr = weeks_historicalCurr[jk]; #yoink it
        deaths_historicalCurrCurr = deaths_historicalCurr[jk]; #yoink it
        deaths_historicalCurrCurr_influenzaPneumonia = deaths_historicalCurr_influenzaPneumonia[jk]; #yoink it
        if( weeks_historicalCurrCurr.max() > weeks.max() ): #catch week 53, lazily handle it
            jkl = np.where(weeks_historicalCurrCurr > weeks.max())[0]; #get where it's week 53
            deaths_historicalCurrCurr[jkl.min()-1] = deaths_historicalCurrCurr[jkl.min()-1] + deaths_historicalCurrCurr[jkl]; #combine with previous week 52
            deaths_historicalCurrCurr = np.delete(deaths_historicalCurrCurr,jkl); #remove that extra week
            deaths_historicalCurrCurr_influenzaPneumonia[jkl.min()-1] = deaths_historicalCurrCurr_influenzaPneumonia[jkl.min()-1] + deaths_historicalCurrCurr_influenzaPneumonia[jkl]; #combine with previous week 52
            deaths_historicalCurrCurr_influenzaPneumonia = np.delete(deaths_historicalCurrCurr_influenzaPneumonia,jkl); #remove that extra week
        #END IF
        
        deaths_historicalPrep[:,j] = deaths_historicalCurrCurr; #save it
        deaths_historicalPrep_influenzaPneumonia[:,j] = deaths_historicalCurrCurr_influenzaPneumonia; #save it
    #END FOR j
    deaths_historicalAvg[:,i] = np.mean(deaths_historicalPrep,axis=1); #avg the deaths over the years and save it
    deaths_historicalAvg_influenzaPneumonia[:,i] = np.mean(deaths_historicalPrep_influenzaPneumonia,axis=1); #avg the deaths over the years and save it

    #do current
    k = statesInterest[i] == states_current; #get where the state we want is
    years_currentCurr = years_current[k]; #yoink it
    weeks_currentCurr = weeks_current[k]; #yoink it
    deaths_currentCurr = deaths_current[k]; #yoink it
    deaths_currentCurr_influenzaPneumonia = deaths_current_influenzaPneumonia[k]; #yoink it
        
    jk = yearOfInterest == years_currentCurr; #get where the current year in current state is
    weeks_currentCurrCurr = weeks_currentCurr[jk]; #yoink it
    deaths_currentCurrCurr = deaths_currentCurr[jk]; #yoink it
    deaths_currentCurrCurr_influenzaPneumonia = deaths_currentCurr_influenzaPneumonia[jk]; #yoink it
    if( weeks_currentCurrCurr.max() > weeks.max() ): #catch week 53
        jkl = np.where(weeks_currentCurrCurr > weeks.max())[0]; #get where it's week 53
        deaths_currentCurrCurr[jkl.min()-1] = deaths_currentCurrCurr[jkl.min()-1] + deaths_currentCurrCurr[jkl]; #combine with previous week 52
        deaths_currentCurrCurr = np.delete(deaths_currentCurrCurr,jkl); #remove that extra week
        deaths_currentCurrCurr_influenzaPneumonia[jkl.min()-1] = deaths_currentCurrCurr_influenzaPneumonia[jkl.min()-1] + deaths_currentCurrCurr_influenzaPneumonia[jkl]; #combine with previous week 52
        deaths_currentCurrCurr_influenzaPneumonia = np.delete(deaths_currentCurrCurr_influenzaPneumonia,jkl); #remove that extra week
    #END IF
        
    deaths_currentValues[:,i] = np.pad(deaths_currentCurrCurr,[0,weeks.size-deaths_currentCurrCurr.size],'constant', constant_values=0); #save current deaths
    deaths_currentValues_influenzaPneumonia[:,i] = np.pad(deaths_currentCurrCurr_influenzaPneumonia,[0,weeks.size-deaths_currentCurrCurr_influenzaPneumonia.size],'constant', constant_values=0); #save current deaths

    #do currentAlt
    k = statesInterest[i] == states_currentAlt; #get where the state we want is
    date_currentAltValues[:,i] = date_currentAlt[k]; #yoink it
    deaths_currentAltValues_pneumonia[:,i] = deaths_currentAlt_pneumonia[k]; #save current deaths
    deaths_currentAltValues_influenza[:,i] = deaths_currentAlt_influenza[k]; #save current deaths
    deaths_currentAltValues_pneumoniaANDcovid[:,i] = deaths_currentAlt_pneumoniaANDcovid[k]; #save current deaths
    deaths_currentAltValues_pneumonia[:,i] = deaths_currentAltValues_pneumonia[:,i] - deaths_currentAltValues_pneumoniaANDcovid[:,i]; #only get ONLY pneumonia (not COVID AND pneumonia)
    deaths_currentAltValues_influenzaPneumonia[:,i] = deaths_currentAltValues_pneumonia[:,i] + deaths_currentAltValues_influenza[:,i]; #combine the pneumonia and influenza numbers b/c they can be mis-diagnosed COVID cases
    
    #do covid
    if( statesInterest[i] == 'New York City'): #special for new york city
        counties_covid = data_covid['Admin2'].to_numpy();
        k = ('Bronx' == counties_covid) | ('New York' == counties_covid) | ('Kings' == counties_covid) | ('Richmond' == counties_covid) | ('Queens' == counties_covid); #get where the state we want is
        for j in range(0,data_covidColumnsDates.size): #roll through the dates
            data_covidDateCurr = data_covid[data_covidColumnsDates[j]][k]; #get the data in the state for the date
            deaths_covidValues[j,i] = np.sum(data_covidDateCurr); #add up the deaths in the state (split by counties by default)
        #END FOR j
        #the covid data is cumulative, so I am going to make it non-cumulative
        deaths_covidValues[:,i] = np.concatenate( [np.array((0,)),np.diff(deaths_covidValues[:,i])] ); #good news is that the data starts as 0 usually, so sticking 0 to keep the correct size should work just fine
        
        #for comaprison with CDC weekly numbers
        for j in range(0,weeksPlot.size):
            if( j == 0 ): #first, gotta set between 0 and weeksPlot[j]
                k = (weeksPlot[j] >= data_covidDates) & (0 < data_covidDates); #get dates that fit
            else:
                k = (weeksPlot[j] >= data_covidDates) & (weeksPlot[j-1] < data_covidDates); #get dates that fit
            #END IF
            if( k.sum() == 0 ): #nothing,nowhere.
                deaths_covidValuesOnWeekly[j,i] = np.nan; #record NaN
            else:
                deaths_covidValuesOnWeekly[j,i] = deaths_covidValues[k,i].sum(); #sum up the week and set it as the value for the week
            #END IF
        #END FOR j
    else:
        k = statesInterest[i] == states_covid; #get where the state we want is
        for j in range(0,data_covidColumnsDates.size): #roll through the dates
            data_covidDateCurr = data_covid[data_covidColumnsDates[j]][k]; #get the data in the state for the date
            deaths_covidValues[j,i] = np.sum(data_covidDateCurr); #add up the deaths in the state (split by counties by default)
        #END FOR j
        #the covid data is cumulative, so I am going to make it non-cumulative
        deaths_covidValues[:,i] = np.concatenate( [np.array((0,)),np.diff(deaths_covidValues[:,i])] ); #good news is that the data starts as 0 usually, so sticking 0 to keep the correct size should work just fine
        
        #for comaprison with CDC weekly numbers
        for j in range(0,weeksPlot.size):
            if( j == 0 ): #first, gotta set between 0 and weeksPlot[j]
                k = (weeksPlot[j] >= data_covidDates) & (0 < data_covidDates); #get dates that fit
            else:
                k = (weeksPlot[j] >= data_covidDates) & (weeksPlot[j-1] < data_covidDates); #get dates that fit
            #END IF
            if( k.sum() == 0 ): #nothing,nowhere.
                deaths_covidValuesOnWeekly[j,i] = np.nan; #record NaN
            else:
                deaths_covidValuesOnWeekly[j,i] = deaths_covidValues[k,i].sum(); #sum up the week and set it as the value for the week
            #END IF
        #END FOR j
    #END IF
#END FOR i


#==================================Plot the data==================================     
deaths_covidProbableTotal = 0; #prep it
deaths_covidCountedTotal = 0; #prep it
deaths_excessTotal = 0; #prep it
for i in range(0,len(statesInterest)): #run through the state of interest
    deaths_delta = deaths_currentValues[:,i]-deaths_covidValuesOnWeekly[:,i]; #used often
    
    fig, ax = plt.subplots(nrows=1, ncols=1,figsize=(11,8.5));
#    figManager = plt.get_current_fig_manager(); #req to maximize
#    figManager.window.showMaximized(); #force maximized
    lhist, = ax.plot(weeksPlot,deaths_historicalAvg[:,i],zorder=1,linewidth=2,color='xkcd:cerulean'); #plot
    lcurr, = ax.plot(weeksPlot,deaths_currentValues[:,i],zorder=3,linewidth=2,color='xkcd:pumpkin orange'); #plot
    lcovid, = ax.plot(weeksPlot,deaths_delta,zorder=2,linewidth=2,color='xkcd:brick red'); #plot
    scovid = ax.fill_between(weeksPlot, deaths_currentValues[:,i], deaths_delta, \
        alpha=0.3,color='xkcd:pinkish red',zorder=0);
#    xLim_min = weeksPlot[np.where(np.isnan(deaths_covidValuesOnWeekly[:,i]))[0][np.where(np.diff(np.where(np.isnan(deaths_covidValuesOnWeekly[:,i]))[0]) > 1)[0][0]]+1]; #why did I make this in one shot
    ax.set_xlim([weeksPlot[0],weekCutoff/52*12]); #limit the data b/c low on data
    currAvgCutoffDate = (year_fraction(datetime.datetime.strptime('03/01/20','%m/%d/%y'))-yearOfInterest)*12; #month fraction cutoff date
    currAvg = np.mean(deaths_currentValues[0:np.where(currAvgCutoffDate < weeksPlot)[0][0],i]); #estimate the average current death rate
    lcurrAvg = ax.hlines(currAvg,weeksPlot[0],weekCutoff/52*12,zorder=1,linewidth=2,linestyle='--',color='xkcd:peach'); #plot
    if( FLG_compareToHistorical == 0 ):
        comparisonLine = np.tile(currAvg,52); #use current year's average as the comparison line for the green-shaded undercount estimate
    else:
        comparisonLine = deaths_historicalAvg[:,i]; #use the historical average as the comparison line for the green-shaded undercount estimate
    #END IF
    currAvgComp = (comparisonLine < np.nan_to_num((deaths_delta))) & (np.nan_to_num(deaths_covidValuesOnWeekly[:,i]) > 0); #get zones where shading is needed
    if( currAvgComp.sum() > 0 ):
        k = np.where(currAvgComp)[0]; #track the line up and line down parts
        seperateBits = np.sum(np.diff(k) > 1)+1; #count the disconnects
        kk = []; #prep a list, hiss
        kk_slider = np.concatenate([np.where(np.concatenate([np.array((True,)),np.diff(k) > 1]) == 1)[0],np.array((k.size,))]); #get indicies where a big difference occurs
        for j in range(0,seperateBits):
            kk.append(k[kk_slider[j]:kk_slider[j+1]]); #append it on cause this is the world we live in
        #END FOR j

        covidProbableNum = 0; #prep counter
        for j in range(0,seperateBits): #this is a complicated heuristic loop to catch multiple individual zones of undercounted deaths
            k = kk[j]; #roll through the splits
            m = (weeksPlot[k[0]] - weeksPlot[k[0]-1])/(deaths_delta[k[0]] - deaths_delta[k[0]-1]); #calc slope
            b = weeksPlot[k[0]] - m*deaths_delta[k[0]]; #calc intercept
            xLeft = m*comparisonLine[k[0]]+b; #calc the date when it crossed the avg value
            if( xLeft > weeksPlot[k[0]] ): #catch where the deaths are always above the mean
                xLeft = weeksPlot[k[0]];
            #END IF
            if( xLeft < weeksPlot[k[0]-1] ): #catch where the deaths are always above the mean in another way
                xLeft = weeksPlot[k[0]-1];
            #END IF
            m = (weeksPlot[k[-1]] - weeksPlot[k[-1]+1])/(deaths_delta[k[-1]] - deaths_delta[k[-1]+1]); #calc slope
            b = weeksPlot[k[-1]] - m*deaths_delta[k[-1]]; #calc intercept
            xRight = m*comparisonLine[k[-1]]+b; #calc the date when it crossed the avg value
            if( xRight < weeksPlot[k[-1]] ): #catch where the deaths are always above the mean
                xRight = weeksPlot[k[-1]];
            #END IF
            if( xRight > weeksPlot[k[-1]+1] ): #catch where the deaths are always above the mean in another way
                xRight = weeksPlot[k[-1]+1];
            #END IF
            # scovidProbable = ax.fill_between(np.concatenate((np.array((xLeft,)),weeksPlot[k],np.array((xRight,)))), np.tile(currAvg,k.size+2), np.concatenate((np.array((currAvg,)),deaths_delta[k],np.array((currAvg,)))), \
            scovidProbable = ax.fill_between(np.concatenate((np.array((xLeft,)),weeksPlot[k],np.array((xRight,)))), comparisonLine[k[0]-1:k[-1]+2], np.concatenate((np.array((comparisonLine[k[0]],)),deaths_delta[k],np.array((comparisonLine[k[-1]+1],)))), \
                alpha=0.3,color='xkcd:greenish',zorder=0);
            covidProbableNum = covidProbableNum + np.int64(np.round(np.sum(deaths_delta[k] - comparisonLine[k[0]:k[-1]+1]))); #count the total probably COVID-19 deaths over multiple splits
        #END FOR j
        if( statesInterest[i] == 'New York'):
            # covidProbableNum = 0; #0 out b/c there's lagged counting
            pass
        #END IF
        deaths_covidProbableTotal = deaths_covidProbableTotal + covidProbableNum; #record the total undercounted for all states involved
    #END IF
    kk = np.zeros((52),dtype=bool);
    kk[0:weekCutoff] = 1;
    covidCountedNum = np.int64(np.nansum(deaths_covidValuesOnWeekly[kk,i]));
    deaths_covidCountedTotal = deaths_covidCountedTotal + covidCountedNum; #record the total counted for all states involved
    k = np.where(np.nan_to_num(deaths_covidValuesOnWeekly[kk,i]) > 0)[0]; #get where COVID-19 deaths are occuring
    excessNum = np.int64(np.round(np.sum(deaths_currentValues[k,i] - np.tile(currAvg,k.size)))); #calculate excess deaths over the mean
    deaths_excessTotal = deaths_excessTotal + excessNum; #reord the total excess deaths for all states involved
    
    #plot influenza/pneumonia deaths
    lfluPneuHist, = ax.plot(weeksPlot,deaths_historicalAvg_influenzaPneumonia[:,i],zorder=1,linewidth=2,color='xkcd:dark lavender'); #plot
    lfluPneu, = ax.plot(weeksPlot,deaths_currentValues_influenzaPneumonia[:,i],zorder=3,linewidth=2,color='xkcd:greenish'); #plot
    
    #plot alternate reported influenza/pneumonia deaths
    lfluPneuAlt, = ax.plot(date_currentAltValues[:,i],deaths_currentAltValues_influenzaPneumonia[:,i],zorder=3,linewidth=2,color='xkcd:dark magenta'); #plot
    
    ax.set_ylabel('Weekly Deaths [Not Cumulative]');
    ax.set_title(statesInterest[i]);
    yLims = np.array(ax.get_ylim()); #get em
    if( np.all(np.nan_to_num(deaths_delta[0:weekCutoff]) >= 0) & (yLims.min() < 0) ):
        ax.set_ylim([0,yLims.max()]); #no negatives if they're not on the plot
    #END IF
    xTicks = ax.get_xticks();
    xTicks[0] = weeksPlot[0]; #set the start
    xTicks[-1] = weekCutoff/52*12; #set the end
    ax.set_xticks(xTicks);
    xLabels = ax.get_xticklabels();
    for j in range(0,len(xLabels)):
        dayNum = np.int64(xTicks[j]/12*yearOfInterest_dayNum); #get the current day number
        dateString = (datetime.datetime(yearOfInterest, 1, 1) + datetime.timedelta(int(dayNum) - 1)).strftime('%m/%d/%y'); #convert to datetime object
        xLabels[j].set_text(dateString); #set the string
    #END FOR j
    ax.set_xticklabels(xLabels);
    ax.xaxis.set_tick_params(rotation=65);
    if( statesInterest[i] == 'Florida' ):
        altString = '|*ALT CDC* Avg. for Jan-May: '+str(int(np.round(deaths_influenzaPneumonia_FL))); #record this string
    elif( statesInterest[i] == 'Kentucky'):
        altString = '|*ALT CDC* Avg. for Jan-May: '+str(int(np.round(deaths_influenzaPneumonia_KY))); #record this string
    else:
        altString = ''; #nothing cause I hard coded above numbers
    #END IF
    if( currAvgComp.sum() == 0 ):
        ax.legend((lhist,lcurr,lcurrAvg,lcovid,scovid,lfluPneuHist,lfluPneu,lfluPneuAlt),( \
            'Historical Average ['+str(years_historical.min())+' to '+str(years_historical.max())+']', \
            str(yearOfInterest)+' Deaths ['+str(excessNum)+' Above Average since 1st COVID-19 Death]', \
            str(yearOfInterest)+' Average Deaths ['+xLabels[0].get_text()+' to 03/01/20]', \
            'Counted COVID-19 Deaths ['+str(covidCountedNum)+' Total]','Due to Counted COVID-19', \
            'Historical Avg. Influenza/Pneumonia ['+str(years_historical.min())+' to '+str(years_historical.max())+ \
            ']\n->Avg. Deaths up to '+xLabels[-1].get_text()[:-3]+' each year: '+str(int(np.round(deaths_historicalAvg_influenzaPneumonia[0:weekCutoff,i].sum())))+altString, \
            str(yearOfInterest)+' Influenza/Pneumonia Deaths [YTD Total: '+str(int(np.round(deaths_currentValues_influenzaPneumonia[0:weekCutoff,i].sum())))+']', \
            str(yearOfInterest)+' Influenza/Pneumonia Deaths *ALT CDC* [From '+date_currentAlt_longform[0]+' Total: '+str(int(np.round(np.nansum(deaths_currentAltValues_influenzaPneumonia[:,i]))))+']' ) );
    else:
        ax.legend((lhist,lcurr,lcurrAvg,lcovid,scovid,scovidProbable,lfluPneuHist,lfluPneu,lfluPneuAlt),( \
            'Historical Average ['+str(years_historical.min())+' to '+str(years_historical.max())+']', \
            str(yearOfInterest)+' Deaths ['+str(excessNum)+' Total]', \
            str(yearOfInterest)+' Average Deaths ['+xLabels[0].get_text()+' to 03/01/20]',\
            'Counted COVID-19 Deaths ['+str(covidCountedNum)+' Total]','Due to Counted COVID-19','Uncounted probable COVID-19 Deaths ['+str(covidProbableNum)+' Total]', \
            'Historical Avg. Influenza/Pneumonia ['+str(years_historical.min())+' to '+str(years_historical.max())+ \
            ']\n->Avg. Deaths up to '+xLabels[-1].get_text()[:-3]+' each year: '+str(int(np.round(deaths_historicalAvg_influenzaPneumonia[0:weekCutoff,i].sum())))+altString, \
            str(yearOfInterest)+' Influenza/Pneumonia Deaths [YTD Total: '+str(int(np.round(deaths_currentValues_influenzaPneumonia[0:weekCutoff,i].sum())))+']', \
            str(yearOfInterest)+' Influenza/Pneumonia Deaths *ALT CDC* [From '+date_currentAlt_longform[0]+' Total: '+str(int(np.round(np.nansum(deaths_currentAltValues_influenzaPneumonia[:,i]))))+']' ) );
     #END IF
#    plt.draw(); #make it so tight_layout can work
#    plt.pause(0.001); #req to make tight_layout work properly (mostly works, how dumb is that tho)
    fig.tight_layout(); #function for a tight layout
    plt.show(block=False); #req to make plot show up for some python IDEs
    
#END FOR i
    
print('Total uncounted probable COVID-19 deaths: '+str(deaths_covidProbableTotal));
print('Total counted COVID-19 deaths: '+str(deaths_covidCountedTotal));
print('Total deaths above average since 1st COVID-19 death: '+str(deaths_excessTotal));
print('Total estimated uncounted COVID-19 deaths from delta of [above avg - counted]: '+str(deaths_excessTotal-deaths_covidCountedTotal));