# -*- coding: utf-8 -*-
"""BigData_merge_update.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15wuWYMeiiqU89iv0My-vY5rXVfvBhACF
"""

'''!apt-get install openjdk-8-jdk-headless -qq > /dev/null
!wget -q https://downloads.apache.org/spark/spark-3.0.1/spark-3.0.1-bin-hadoop2.7.tgz
!tar -xvf spark-3.0.1-bin-hadoop2.7.tgz
!pip install -q findspark'''

#pip install pyspark

#pip install findspark

'''import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
os.environ["SPARK_HOME"] = "/content/spark-3.0.1-bin-hadoop2.7"
import findspark
findspark.init()
'''

from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession,SQLContext
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime
import numpy as np             #for numerical computations like log,exp,sqrt etc
import pandas as pd   
import plotly.graph_objects as go
import matplotlib.ticker as mtick
import matplotlib.pyplot as plt
from pyspark.sql.types import IntegerType
import seaborn as sns
import re
from textblob import TextBlob
conf = SparkConf().setMaster("local").setAppName("Weather analysis")  
from sklearn.metrics import mean_squared_error      #for reading & storing data, pre-processing
pd.set_option('display.float_format', lambda x: '%.5f' % x)

sc = SparkContext(conf = conf)
spark = SparkSession(sc)

sqlContext = SQLContext(sc)

#Reading the dataset
df = spark.read.option("header",'true').csv("hdfs:/Final/Input/city_temperature.csv",inferSchema=True)

print(df.dtypes)

#Convert the data into a pandas dataframe 
df=df.toPandas()

#Choosing only the rows with India from the dataframe
data_India  = df[ (df['Country'] == 'India') & (df['Year'] < 2020)]

#plot for 4 cities and comparison of their temparatures
India_plot=data_India.groupby(['City','Year'])['AvgTemperature'].mean().reset_index()
India_plot.pivot('Year','City','AvgTemperature').plot()
plt.gcf().set_size_inches(14,6)
fig1= plt.savefig("/home/vaishnavi/Desktop/Final/Screenshots")
plt.show()

#creating variable 'season'
def season(df):
    if df in [12,1,2] :
        return 'Winter'
    elif  df in [3,4,5]:
        return 'Summer'
    elif df in [6,7,8]:
        return 'Monsoon'
    elif df in [9,10,11]:
        return 'Autumn'
    else:
        return 'NA'

pd.options.mode.chained_assignment = None  # default='warn'
data_India['Season'] = data_India['Month'].apply(season)

data_India['AvgTemperature']=data_India['AvgTemperature'].astype('float64')
data_India[['Month' , 'Day' , 'Year']]=data_India[['Month' , 'Day' , 'Year']].astype('int64')

#Seasons in Delhi
data_Delhi = data_India[data_India['City'] == 'Delhi']

#Plot the seasons
Delhi_plot=data_Delhi.groupby(['Season','Year'])['AvgTemperature'].mean().reset_index()
Delhi_plot.pivot('Year','Season','AvgTemperature').plot()
plt.gcf().set_size_inches(14,6)
fig2= plt.savefig("/home/vaishnavi/Desktop/Final/Screenshots")
plt.show()


#Average temparature monthly in India
plt.figure(figsize= (15,10))
sns.pointplot(x='Month', y='AvgTemperature', data=data_India);
plt.title('Average Temperature India - Monthly Trend',fontsize=20);

Average_Temperture_in_every_region = df.groupby("Region")["AvgTemperature"].mean().sort_values()[-1::-1]
Average_Temperture_in_every_region = Average_Temperture_in_every_region.rename({"South/Central America & Carribean":"South America","Australia/South Pacific":"Australia"})
Average_Temperture_in_every_region

fig3= plt.figure(figsize = (15,8))
plt.bar(Average_Temperture_in_every_region.index,Average_Temperture_in_every_region.values)
plt.xticks(rotation = 10,size = 15)
plt.yticks(size = 15)
plt.ylabel("Average_Temperture",size = 15)
plt.title("Average Temperture in every region",size = 20)
fig3=plt.savefig("/home/vaishnavi/Desktop/Final/Screenshots")
plt.show()

#dropping the State column as it has many null values
df.drop('State',axis='columns', inplace=True)

#Keeping only rows for Delhi
delhi = df[df["City"] == "Delhi"]
delhi.reset_index(inplace = True)
delhi.drop('index', axis = 1, inplace=True)
print(delhi.describe())

#Replacing outliers with mean
from sklearn.impute import SimpleImputer
imputer = SimpleImputer()
delhi["AvgTemperature"].replace(-99, np.mean(delhi["AvgTemperature"]), inplace = True)
delhi["AvgTemperature"] = pd.DataFrame(imputer.fit_transform(delhi.loc[:, "AvgTemperature":]))

#Converting to datetime format
delhi['Date'] = pd.to_datetime(delhi[['Year','Month','Day']])
delhi = delhi.drop(['Region', 'Country', 'City','Month','Day'], axis = 1)
print(delhi.head())

#Visualisation
fig4= plt.plot(delhi["Date"], delhi["AvgTemperature"])
fig4=plt.savefig("/home/vaishnavi/Desktop/Final/Screenshots")
plt.show()


#Defining training and testing data
training_set = delhi[delhi["Year"] <= 2015]
test_set = delhi[delhi["Year"] > 2015]

#acf and pacf plots
from statsmodels.graphics.tsaplots import plot_acf
acf=plot_acf(delhi["AvgTemperature"], lags = 9000)
from statsmodels.graphics.tsaplots import plot_pacf
pacf=plot_pacf(delhi["AvgTemperature"], lags = 10)
fig5=plt.savefig("/home/vaishnavi/Desktop/Final/Screenshots")
plt.show()


#MA model
from statsmodels.tsa.arima_model import ARMA
model_MA = ARMA(training_set["AvgTemperature"],order=(0,2))
model_fit_MA = model_MA.fit()
predictions_MA = model_fit_MA.predict(test_set.index[0],test_set.index[-1])

fig5=plt.figure(figsize=(15,5))
plt.ylabel("Temperature",fontsize=20)
plt.plot(test_set["AvgTemperature"],label="Original Data")
plt.plot(predictions_MA,label="Predictions")
fig6=plt.savefig("/home/vaishnavi/Desktop/Final/Screenshots")
plt.show()
#plt.legend()

#RMSE for MA model
mse = mean_squared_error(predictions_MA,test_set["AvgTemperature"])
print(mse**0.5)

#!pip install statsmodels --upgrade

#AR model
from statsmodels.tsa.ar_model import AutoReg
model_AR = AutoReg(training_set["AvgTemperature"], lags = 1000)
model_fit_AR = model_AR.fit()
predictions_AR = model_fit_AR.predict(training_set.shape[0], training_set.shape[0] + test_set.shape[0] - 1)
import seaborn as sns
fig6= plt.figure(figsize=(15,5))
plt.ylabel("Temperature (F)", fontsize = 20)
plt.plot(test_set["AvgTemperature"], label = "Original Data")
plt.plot(predictions_AR, label = "Predictions")
fig7=plt.savefig("/home/vaishnavi/Desktop/Final/Screenshots")
plt.show()
#plt.legend()

rmse = mean_squared_error(predictions_AR,test_set["AvgTemperature"])
print(rmse**0.5)