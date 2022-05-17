"""
Tools for analysing Dutch weather data
Hessel Voortman EC

20210218 - New libary - H.G. Voortman

===============================================================================
Copyright (C) 2021, Hessel Voortman EC BV
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights 
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
copies of the Software, and to permit persons to whom the Software is 
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in 
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
HESSEL VOORTMAN EC BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF 
OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
SOFTWARE.

Except as contained in this notice, the name of Hessel Voortman EC BV shall not 
be used in advertising or otherwise to promote the sale, use or other dealings
in this Software without prior written authorization from Hessel Voortman EC BV.
"""
# In[5]
import numpy as np
#import pandas as pd

# In[10] Season statistics
def _hellmann(df): # calculate Hellmann numbers
   
    # Select winter months and determine and add winter year
    df['winter'] = df.loc[df['YYYYMMDD'].dt.month.isin([1,2,3]),
                          'YYYYMMDD'].dt.year
    df.loc[df['YYYYMMDD'].
           dt.month.isin([11,12]),'winter']=df.loc[df['YYYYMMDD'].
                                                   dt.month.isin([11,12]),
                                                   'YYYYMMDD'].dt.year +1
    
    # The Hellmann number is the sum of negative daily mean temperatures. 
    # First we create a column containing "Hellmann's delta" for each day
    df['hellmann'] = -np.minimum(0, df['TG'])
    out=df.groupby('winter').sum()['hellmann']
    
    # Now calculate the Hellmann number
    return out

def _wntr_stat(df): # winter statistics
   
    # Select winter months and determine and add winter year following
    # KNMI conventions
    df['winter']=df.loc[df['YYYYMMDD'].dt.month.isin([1,2]), 
                          'YYYYMMDD'].dt.year
    df.loc[df['YYYYMMDD'].dt.month.
           isin([12]),'winter']=df.loc[df['YYYYMMDD'].
                                          dt.month.isin([12]), 
                                          'YYYYMMDD'].dt.year +1
    
    # Determine winter mean temperature
    out=df[['winter','TG']].groupby('winter').mean()
    
    # Determine winter maximum temperature
    out=out.join(df[['winter','TX']].groupby('winter').max())
    
    # Determine winter minimum temperature
    out=out.join(df[['winter','TN']].groupby('winter').min())
    
    out=out.join(_hellmann(df))
    
    return out

# In[20]: selecting data
def climate(df, yr_lo = 1991, yr_up = 2020): 
    # Select data corresponding to a pre-defined period
    res = df.loc[np.logical_and(df['YYYYMMDD'].dt.
                                year <= yr_up, df['YYYYMMDD'].dt.year>=yr_lo)]
    return res
