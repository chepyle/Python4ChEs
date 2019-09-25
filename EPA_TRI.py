# -*- coding: utf-8 -*-
"""
Information and function to read from the EPA's Toxic Release Inventory

Used to support the notebook TRI_API.ipynb

This is based off of the project 
https://github.com/kperry2215/pull_data_from_EPA_Envirofacts_API

"""
import hvplot.pandas
import pandas as pd
import io
import requests
from bs4 import BeautifulSoup # parse some xml returned 
from progress.bar import Bar

wm_dict = {'P91':'Waste water treatment',
           'M56':'Energy Recovery',
           'M50':'Incineration/Thermal Treatment',
           'M64':'Other Landfills',
           'M24':'Metals Recovery',
           'M26':'Other Reuse or Recovery',
           'M41':'Solidification/Stabilization - Metals and Metal Category Compounds only',
           'M90':'Other Off-Site Management',
           'M61':'Wastewater Treatment (Excluding POTW)',
           'M93':'Transfer to Waste Broker - Recycling ',
           'M92':'Transfer to Waste Broker - Energy Recovery',
           'M94':'Transfer to Waste Broker - Disposal',
           'M20':'Solvents/Organics Recovery',
           'M99':'Unknown',
           'M54':'Incineration/Insignificant Fuel Value ',
           'M95':'Transfer to Waste Broker - Waste Treatment',
           'M62':'Wastewater Treatment (Excluding POTW) - Metals and Metal Category Compounds only',
           'M79':'Other Land Disposal',
           'M65':'RCRA Subtitle C Landfills',
           'M69':'Other Waste Treatment',
           'M40':'Solidification/Stabilization',
           'M73':'Land Treatment',
           'M10':'Storage Only',
           'M81':'Underground Injection to Class I Wells',
           'M66':'Subtitle C Surface Impoundment',
           'M67':'Other Surface Impoundments',
           'M28':'Acid Regeneration',
           'M82':'Underground Injection to Class II- V Wells',
           'M72':'Landfill/Disposal Surface Impoundment'
          }

def TRI_Query(state=None, county=None,area_code=None, year=None,chunk_size=100000):
    """Query the EPA Toxic Release Inventory Database
    
    This function constructs a query for the EPA Toxic Release Inventory API, with optional arguments for details such as the two-letter state, county name, area code, and year.  More info here: https://www.epa.gov/enviro/envirofacts-data-service-api
    
    """
    
    base_url='https://data.epa.gov/efservice/'
    #Declare the names of the tables that we want to pull    
    table_name1='TRI_FACILITY'
    table_name2='TRI_REPORTING_FORM'
    table_name3 = 'TRI_TRANSFER_QTY'
    
    output_format='CSV'
    query = base_url
    query+=table_name1+'/'
    #Add in the state qualifier, if the desired_state variable is named
    if state:
        query+='state_abbr/=/'+state+'/'
    #Add in the county qualifier, if the desired_county variable is named
    if county:
        query+='county_name/'+county+'/'
    #Add in the area code qualifier, if the desired_area_code variable is named
    if area_code:
        query+='zip_code/'+str(area_code)+'/'
    #Add in the next table name and year qualifier, if the desired_year variable is named
    query += table_name2+'/'
    if year:
        if type(year) is list:
            query+='reporting_year/'+str(year[0])+'/'+str(year[1])+'/'
        else:        
            query+='reporting_year/'+str(year)+'/'
    #add the third table
    query += table_name3+'/'
    count_query = query+'count/'
    
    count_xml = requests.get(count_query).content
    
    nrows= int(BeautifulSoup(count_xml,features="lxml").find('requestrecordcount').contents[0])
    
    #Add in the desired output format to the query
    csv_query = query+ output_format

    
    #Return the completed query
    bar = Bar('Downloading Records:',max=nrows,\
              suffix='%(index)d/%(max)d %(percent).1f%% - %(eta)ds')
    bar.check_tty = False
    s=requests.get(csv_query).content
    dataframe=pd.read_csv(io.StringIO(s.decode('utf-8')), engine='python',
                      encoding='utf-8', error_bad_lines=False)
    bar.next(n = dataframe.shape[0])
    nrows_prev = dataframe.shape[0]

    while dataframe.shape[0] < nrows:
        new_query = query + 'rows/'+str(dataframe.shape[0])+':'\
                        +str(dataframe.shape[0]+chunk_size)+'/'
        csv_query = new_query+ output_format
        s=requests.get(csv_query).content
        dataframe = dataframe.append(pd.read_csv(io.StringIO(s.decode('utf-8')),
                                                 engine='python',encoding='utf-8',
                                                 error_bad_lines=False))
        bar.next(n=dataframe.shape[0]-nrows_prev)
        nrows_prev = dataframe.shape[0]
        
    bar.finish()
    # do the replacement:
    if 'TRI_TRANSFER_QTY.TYPE_OF_WASTE_MANAGEMENT' in dataframe.columns:
        dataframe.replace({'TRI_TRANSFER_QTY.TYPE_OF_WASTE_MANAGEMENT':wm_dict},inplace=True)
    return dataframe

