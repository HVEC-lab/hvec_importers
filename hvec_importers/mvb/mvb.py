# -*- coding: utf-8 -*-
"""
Package to download data from the Meetnet Vlaamse Banken API (Flemish Banks 
Monitoring network).
The Flemish Banks monitoring network consists of many measurement locations 
providing hydro-meteorological time-series. Measurement locations are situated 
on the Belgian Continental Shelf area and the Belgian coast.

To download data, an account is required which can be freely requested at
https://meetnetvlaamsebanken.be/

The package contains 5 methods:
    ping: to ping the API and test for successfull login status.
    login: to log-in to the API.
    catalog: to fetch the catalog of measurement locations and parameters.
    table: visual indication of available locations and parameters.
    get_data: to download timeseries.
    
Typically you first need to import meetnetvlaamsebanken.py, then login, 
optionally fetch the catalog to determine Loction+Parameter ID's and finally 
perform one or more get_data requests.

Example:
    import meetnetvlaamsebanken as mvb
    token = mvb.login('<username>','<password>')
    t,v = mvb.get_data(token,'BVHGHA','2020-01-01','2022-02-01')
    
Created on Thu Aug 22 12:52:02 2019

@author: LWM Roest
@email: bart.roest@kuleuven.be
@email: l.w.m.roest@tudelft.nl
"""

#First test version for python MeetnetVlaamseBanken toolbox.
#The following packages are required:
import numpy as np
import requests
import json
import matplotlib.pyplot as plt
#from datetime import datetime

#Default values:
#apiurl = "https://api.meetnetvlaamsebanken.be/"


#Routine for ping request
def ping(token="") :
    """Sends ping request to meetnet vlaamse banken API.
    
    ping returns the login status of the provided token. Tokens expire after 
    3600s. A new login is then required.
    """
    
    pingpath = "https://api.meetnetvlaamsebanken.be/V2/ping/"
#     if not exist(token):
#         token= " "
    headers = {"Authorization": "Bearer "+token}
    pingresponse = requests.get(pingpath, headers=headers, verify=True)
    print(pingresponse.text)
    pingstatus = json.loads(pingresponse.text)
    return pingstatus

#Routine to login to the API
def login(username,password):
    """Log-in to the API with supplied credentials.
    
    mvb.login logs in into the API of Meetnet Vlaamse Banken (Flemish Banks
    Monitoring Network API). The login returns a token, which must be sent with
    every further request.

    After login, data can be requested by mvb.get_data().
    The catalog of available data can be reqested with mvb.catalog().

    The token is valid for 3600s, after that you must login again.
    
    An account can be requested freely from: https://meetnetvlaamsebanken.be/

    Syntax:
        token = mvb.login('username','password')

    Input:
        username: 'string'
            Username for meetnetvlaamsebanken.be.
        password: 'string'
            Password for meetnetvlaamsebanken.be.

    Output:
        token: 'string'
            String containing the accesstoken. Must be supplied to other functions.

    Example:
        token = mvbLogin('name@company.org','P4ssw0rd')
        
    """
    
    loginpath = "https://api.meetnetvlaamsebanken.be/Token/"
#    postdata = {"grant_type": "password","username": input("username: "),
#                "password": input("Password: ")}
    postdata = {"grant_type": "password","username": username,
                "password": password}
    loginresponse = requests.post(loginpath, data=postdata, verify=True)
    jdata=(json.loads(loginresponse.text))
    token=jdata["access_token"]        
    return token

#Routine to fetch the catalog of data
def catalog(token):
    """Get the catalog of available stations and parameters."""
    catpath = "https://api.meetnetvlaamsebanken.be/V2/Catalog/"
    headers = {"authorization": "Bearer "+token}
    catresponse = requests.get(catpath, headers=headers, verify=True)
    ctl=json.loads(catresponse.content)
    return ctl

#Routine to fetch the catalog of data
def table(token,language='EN'):
    """Plot a table with valid LocationID+ParameterID combinations.
    
    mvb.table shows an overview with combinations of parameters and measurement
    locations, for which data is available. Further, a list with the full names
    of these locations is presented. The order of the list is the same as the 
    order of the codes. Optionally the language in which the full names are 
    presented can be changed to Dutch or English (default).
    
    Combinations with available data can be used to request data with 
    mvb.get_data, e.g. location A2 boei: 'A2B' with parameter Golfhoogte - 
    Boeien: 'GHA' --> 'A2BGHA'.
    
    Syntax:
        dataTable = mvb.table(token);
    Input:
        token: <weboptions object> Weboptions object containing the accesstoken. 
            Generate this token via mvb.login(). If no token is given or it is
            invalid, the user is prompted for credentials.
        language: string of preferred language: 'NL' or 'EN', officially 'nl-BE'
           or 'en-GB'.
    Output:
    	datatable: mask indicating data availability for location/parameter
        combinations.
    Example:
        mvb.table(token)
    """
    ctl = catalog(token)
    langIdx = 1
    for n, culture in enumerate(ctl['Locations'][0]['Name']):
        if language in culture['Culture']:
            langIdx = n
            
    #Get LocationID's and ParameterID's
    Locations = [loc['ID'] for loc in ctl['Locations']]
    Parameters = [par['ID'] for par in ctl['Parameters']]
    AvailableData = [AD['ID'] for AD in ctl['AvailableData']]
    
    #Determine intersection // Valid combinations in the catalog
    dataTable = np.zeros((len(Locations), len(Parameters)),dtype=int)
    for m, loc in enumerate(Locations):
        for n, par in enumerate(Parameters):
            if loc+par in AvailableData:
                dataTable[m,n]=1
    
    #Plot array of combinations in a nice figure.
    plt.figure()
    plt.pcolor(dataTable)
    plt.xlabel("Parameters")
    plt.xticks(np.arange(0.5,len(Parameters)),Parameters,rotation=270)
    plt.ylabel("Locations")
    plt.yticks(np.arange(0.5,len(Locations)),Locations)
    
    return dataTable

#Routine to fetch data
def get_data(token,stationparameter,tstart,tstop):
    """Get data from the API for the requested station and time-span.
    
    mvb.get_data retreives timeseries from the API of Meetnet Vlaamse Banken
    (Flemish Banks Monitoring Network API). Only one parameter can be
    retreived per call. The data is returned as two vectors: time and value. 
    Meetnet Vlaamse Banken (Flemish Banks Monitoring Network API) only
    accepts requests for timeseries <=365 days. This script runs several
    subsequent GET requests to obtain a longer time series.

    A login token is required, which can be obtained with MVBLOGIN. A login
    can be requested freely from https://meetnetvlaamsebanken.be/

    Syntax:
        time, value = mvbget_data(token, location+parameter, starttime, endtime)

    Input:
        token: 'string'
            Accesstoken for the API. Generate this token via mvb.login. If no 
            token is given or it is invalid, the user is prompted for 
            credentials.
        stationparameter: 'string'
             MeasurementID string, choose one from the catalog list:
             ctl['AvailableData'] The catalog can be obtained via  mvb.catalog.
        start: 'string'
            Start time string in format: 'yyyy-mm-dd HH:MM:SS' (the time part 
            is optional).
        end: 'string'
            End time string, same format as start.

    Output:
        time: column vector containing time in datenum. 
        value: column vector containing measured value. For units see the 
            catalog via mvb.catalog.

    Example:
        t,v = mvb.get_data('id','BVHGH1','start','2010-01-01','end','2017-03-05','vector',true,'token',token);
    
    
    
    """
    
    # Test login status
    pingstatus = ping(token)
    if pingstatus["Customer"] is None:
        print("Your login token is invalid or expired, please use mvb.login() "
              "to obtain a new token.\n")
        return None, None
    
    # Set default values
    getpath = "https://api.meetnetvlaamsebanken.be/V2/getData/"
    headers = {"authorization": "Bearer "+token}
    
    # Vector of start values. Max range per request is 365.00 days.
    # For longer time spans, multiple requests are issued.
    t_start=np.arange(np.datetime64(tstart), np.datetime64(tstop), 
                      np.timedelta64(365,"D"))
    
    v=np.array([])
    t=np.array([], dtype="datetime64[s]")
    
    for i in range(len(t_start)):
        if i is len(t_start)-1:
            t_stop = np.datetime64(tstop)
        else:
            t_stop = t_start[i+1]
        print(f"Retreiving data for ID: {stationparameter} from "
              + np.datetime_as_string(t_start[i]) +" to "
              + np.datetime_as_string(t_stop) +"\n")
                
        postdata= {"StartTime": np.datetime_as_string(t_start[i]), 
                   "EndTime": np.datetime_as_string(t_stop), 
                   "IDs": stationparameter}
        getresponse = requests.post(getpath, headers=headers, data=postdata, 
                                    verify=True)
        data=json.loads(getresponse.content)
        
        #print(len(data["Values"]))

        if data["Values"] is None: 
            # When ID is not found, data.Values will be empty
            print("Warning: empty result, ID {stationparameter} not found! \n")
            continue # Station not found, terminate execution.
            
        elif data["Values"][0]["Values"] is None: 
            # When ID is found, but no data is available in the time interval, 
            # the values are empty.
            print("ID {stationparameter} was found, but there is no data in "
                  "this time interval.\n");
            continue # continue to next request.
        
        else:
            nn=len(data["Values"][0]["Values"])
            vtemp=np.zeros(nn)
            ttemp=np.zeros(nn,dtype="datetime64[s]")
        
            for n in range(nn):
                vtemp[n]=float(data["Values"][0]["Values"][n]["Value"])
                #t[n]=datetime.strptime(dd["Values"][0]["Values"][n]["Timestamp"],"%Y-%m-%dT%H:%M:%S%z")
                #t[n]=datetime.fromisoformat(dd["Values"][0]["Values"][n]["Timestamp"])
                ttemp[n]=np.datetime64(data["Values"][0]["Values"][n]["Timestamp"][:-6])

            v=np.append(v, vtemp)
            t=np.append(t, ttemp)
    
    #Return only unique values! Repeated values are omitted.
    (t, idx)=np.unique(t, return_index=True)
    v=v[idx]

    return t, v #, data

#EOF