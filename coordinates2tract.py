
# coding: utf-8

# In[ ]:


#! python3


# In[33]:


import json
import requests
import sys
import pandas as pd


# In[25]:


path = 'data.csv'
data = pd.read_csv(path,header = 0)


# In[28]:


def censusTract(latitude, longitude):
    # takes latitude and longitude coordinates with 5 significant figures
    url = 'http://data.fcc.gov/api/block/find?format=json&latitude=' + latitude + '&longitude=' + longitude + '&showall=true'
    response = requests.get(url).content
    data = json.loads(response)
    tract = data['Block']['FIPS'][0:11]
    return tract


# In[ ]:


latitudedS = data['latitude']
longitudedS = data['longitude']
tract = []
for i in range(len(data)):
    sys.stdout.write('\rPercentage complete: ' + str((i/len(data))*100) + '%')
    latitude = str(latitudedS.iloc[i])
    longitude = str(longitudedS.loc[i])
    tract[i] = tract.append(censusTract(latitude,longitude))

