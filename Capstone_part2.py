#!/usr/bin/env python
# coding: utf-8

# In[18]:


import requests
import lxml.html as lh
import pandas as pd
url='https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M'
#Create a handle, page, to handle the contents of the website
page = requests.get(url)
#Store the contents of the website under doc
doc = lh.fromstring(page.content)
#Parse data that are stored between <tr>..</tr> of HTML
tr_elements = doc.xpath('//tr')
[len(T) for T in tr_elements[:12]]
tr_elements = doc.xpath('//tr')
#Create empty list
col=[]
i=0
#For each row, store each first element (header) and an empty list
for t in tr_elements[0]:
    i+=1
    name=t.text_content()
    col.append((name,[]))


# In[19]:


#Since out first row is the header, data is stored on the second row onwards
for j in range(1,len(tr_elements)):
    #T is our j'th row
    T=tr_elements[j]
    
    #If row is not of size 10, the //tr data is not from our table 
    if len(T)!=3:
        break
    
    #i is the index of our column
    i=0
    
    #Iterate through each element of the row
    for t in T.iterchildren():
        data=t.text_content() 
        #Check if row is empty
        if i>0:
        #Convert any numerical value to integers
            try:
                data=int(data)
            except:
                pass
        #Append the data to the empty list of the i'th column
        col[i][1].append(data)
        #Increment i for the next column
        i+=1


# In[21]:


Dict={title:column for (title,column) in col}
df=pd.DataFrame(Dict)


# In[22]:


#If Neighborhood is Not assigned but if Borough is assigned then change the Neighborhood name to Borough name
for i in range(len(df)):
    if(df.loc[i,'Neighborhood\n'] == 'Not assigned\n' and df.loc[i,'Borough'] != 'Not assigned'):
        df.loc[i,'Neighborhood\n'] = df.loc[i,'Borough']
df.head(30) 
# If there are multiple entries for one postcode then the neighborhoods to be merged
Postcode = []
for i in range(len(df)):
    Postcode.append(df.loc[i,"Postcode"])
for i in range(1,len(Postcode)):
    x =''
    if(Postcode[i] == Postcode[i-1]):
    
         df.loc[i-1,"Neighborhood\n"] = df.loc[i-1,"Neighborhood\n"] +','+df.loc[i,"Neighborhood\n"]
          
df.drop_duplicates(subset ="Postcode",keep = 'first', inplace = True) 
df.head(20)
#Delete rows that do not have Borough Assigned
df = df[df['Borough'] != "Not assigned"] 


# In[23]:


#Geocoder Library did not work hence used the excel to populate data and have merged the two dataframes
df1 = pd.read_csv(r'C:\Users\debandas\Desktop\Geospatial_Coordinates.csv')


# In[24]:


df1.head()


# In[25]:


merged_df = pd.merge(left=df,right=df1,left_on='Postcode',right_on='Postcode')


# In[26]:


merged_df.head()


# In[27]:


df.head(30)


# In[ ]:




