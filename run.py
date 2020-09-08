from amphora.client import AmphoraDataRepositoryClient, Credentials
from microprediction import MicroWriter, MicroReader
import time
import os
from datetime import datetime, timedelta
import amphora_api_client as a10a
import numpy as np
import itertools
import statsmodels.api as sm
from statsmodels.tsa.vector_ar.var_model import VAR

############################################################
# Useful function
def get_median(x,y):    
    p=0.5
    N = len(x)
    x_oi = 0
    y_oi = 100000
    for n in range(N):
        if abs(y[n] - p) < y_oi:
            y_oi = abs(y[n] - p)
            x_oi = x[n]
            
    print(x_oi)
    print(y_oi)   
    return x_oi

##############################################################
# parameters and details
credentials = Credentials(username=os.getenv('username'), password=os.getenv('password'))
client = AmphoraDataRepositoryClient(credentials) 

Electricity_Amphora_id = '89c2e30d-78c8-46ef-b591-140edd84ddb6'
Weather_Amphora_id = '2866d34f-fe2b-4c07-acdd-28fe2d6d9194'
Forecast_amphora_id = '78831a6b-de49-454e-9e5c-7c757478e783'
name = 'South_Australia_Electricity_Price.json'

#############################################################
# Publish raw data on microprediction
mw = MicroWriter(write_key="bdfd44affd28e6c5b45329d6d4df7729")
time_range = a10a.DateTimeRange(_from = datetime.utcnow() + timedelta(hours=-1) , to= datetime.utcnow() )
electricity_amphora = client.get_amphora(Electricity_Amphora_id)
electricity_signals = electricity_amphora.get_signals()
df = electricity_signals.pull(date_time_range=time_range).to_pandas()
price = df['price']
mw.set(name=name,value=price[-1])

##########################################################
# Create a prediction and publish on microprediction
# length = mw.num_predictions
# data_time_range = a10a.DateTimeRange(_from = datetime.utcnow() + timedelta(hours=-length/2) , to= datetime.utcnow() )
# pdf = electricity_signals.pull(date_time_range=data_time_range).to_pandas()
# price = pdf['price']
# prices_of_interest = price[-length-1:-1]

# elec_prices_diff = np.zeros(length-1)
# for t in range(1,length):
#    elec_prices_diff[t-1] = prices_of_interest[t] - prices_of_interest[t-1]
# std_val = np.std(elec_prices_diff[abs(elec_prices_diff)<30])

# weather_amphora = client.get_amphora(Weather_Amphora_id)
# weather_signals = weather_amphora.get_signals()
# wdf = weather_signals.pull(date_time_range=data_time_range).to_pandas()
# data_of_interest = wdf[0:length]

# training_data = np.transpose(np.array([prices_of_interest, data_of_interest['pressure'], data_of_interest['airTemp']]))

# model = VAR(training_data)
# model_fit = model.fit()

# yhat = model_fit.forecast(model_fit.y, steps=1)

# dist = np.random.laplace(yhat[0,0], std_val/np.sqrt(2), length)
# res = mw.submit(name=name, values=dist, delay=None, verbose=None)


################################################################
# Publish best predictions on Amphora
# mr = MicroReader()
# x_values = np.arange(price[-1]-40, price[-1]+40, 0.5).tolist()
# cdf = mr.get_cdf(name=name, values = x_values)
#median = get_median(cdf['x'], cdf['y'])

#forecast_amphora = client.get_amphora(Forecast_amphora_id)
#time = datetime.utcnow()
#signal = [dict(t = time, medianValue = median)]
#forecast_amphora.push_signals_dict_array(signal) 

