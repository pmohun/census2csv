
# coding: utf-8

# In[1]:


#! python3
# census2csv

# This script is used to scrape and consolidate demographic, population, and housing data 
# from the United States census website at: https://www.ffiec.gov/census/default.aspx


# In[2]:


import csv
import os
import sys
import requests
from lxml import html
from bs4 import BeautifulSoup
from tkinter import filedialog
from nested_dict import nested_dict
import pandas as pd


# In[ ]:


# import specific county codes for parsing

geo_info = ([36047,36061,6075,11001,6037,17031,25025,36081,6081,25021,36005,6111,36085,36119,
            24033,53025,6059,34017,25017,6071,24031,6029,36059,42007,6065,6083,50003,6085,17197])

# standardize for use in parsing
state = []
county = []
for geo in geo_info:
    geo = str(geo)
    if len(geo) > 7:
        geo = geo[:-1].replace(".","") # remove the last digit, and remove decimals
    if len(geo) < 5:
        geo = '0' + geo # for states less than 10, add a prefix 0 to fit the naming convention
    state.append(geo[:2])
    county.append(geo[2:])

# define columns for tables
columns = []
demographic_columns = ['Tract Code','Tract Income Level','Distressed (Y/N)','Tract Median Fam Income','MSA Median Fam Income','2017 Median Fam Income','2015 Median Fam Income','Tract Population','Tract Minority %','Minority Pop','Owner Occupied Units','1-4 Fam Units','state','county']
population_columns = ['Tract Code','Tract Population','Tract Minority %','Number of Families','Number Households','Non Hispanic White Pop','tract_minority_pop','american_indian_pop','asian_islander_pop','black_population','hisplanic_population','mixed_population','state','county']
housing_columns = ['Tract Code','Total Housing Units','1-4 Family Units','Median House Age','Inside City?','Owner Occupied Units','Vacant Units','Owner Occupied 1-4 Fam Units','Renter Occupied','state','county']
columns.append(demographic_columns)
columns.append(population_columns)
columns.append(housing_columns)

report = ['demographic','population','housing'] # type of data to pull from census site


# In[ ]:


def get_Page(url):
    # This function is used to pull the max page number from each counties report on the FFIEC website
    # Example of url for this function is: https://www.ffiec.gov/census/report.aspx?year=2017&county=019&tract=ALL&state=06&report=demographic
    html_response = requests.get(url).text.encode('utf-8') # request html (hot garbage)
    soup = BeautifulSoup(html_response, 'html.parser')
    pages = soup.find_all("span", class_="main-body") # page number sits in this class
    pages = str(pages[4].string) # specific to this site, lists page n of n
    try:
        page = int(pages[-2:]) # hoping this is a common format
    except Exception:
        page = 1
    return page

def consolidate_pages(state):
    pages = []
    for i in range(len(state)):
            # This uses the demographic report to pull the max page number, although any type of report should give the same result
            print('Pulling page numbers from the govt. census website . . .')
            base_url = 'https://www.ffiec.gov/census/report.aspx?year=2017&state=' + state[i] + '&msa=&county=' + county[i] + '&tract=ALL&report=demographic'
            try:
                page = get_Page(base_url) # iterate through each state/county pair and pull the max page number
            except Exception: # if there is only one page, this exception will be thrown
                page = 1
            page = str(page)
            pages.append(page)
    return pages

pages = consolidate_pages(state) # define number of pages


# In[ ]:


pages


# In[ ]:


report = ['demographic','population','housing']
baseurl = 'https://www.ffiec.gov/census/report.aspx?year=2017&county=019&tract=ALL&state=06&report=demographic'

for j in range(len(report)): 
    column_df = columns[j] # use the correct headers for each type of census report
    df = pd.DataFrame(columns = columns[j]) # initialize dataframe to hold consolidated reports
    for i in range(len(state)):
        print((i/((len(state)*len(report))))) # progress bar so I don't get impatient
        url = 'https://www.ffiec.gov/census/report.aspx?year=2017&state=' + state[i] + '&msa=&county=' + county[i] + '&tract=ALL&report=' + report[j]+ '&page=' + pages[i]
        html = requests.get(url).content
        df_list = pd.read_html(html)
        df_list = df_list[-1] # transpose to meet df structure
        df_list['state'] = state[i]
        df_list['county'] = county[i]
        df_list = df_list.iloc[1:,:] # remove first row to prevent duplicate column headers
        df_list.columns = column_df
        df = df.append(df_list) # add to data frame
        df.to_csv('censusInfo_' + report[j] + '.csv', index = False)

