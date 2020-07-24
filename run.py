from amphora.client import AmphoraDataRepositoryClient, Credentials
from microprediction import MicroWriter
import time
import os
from datetime import datetime, timedelta
import amphora_api_client as a10a
import numpy as np
import itertools
import statsmodels.api as sm
from statsmodels.tsa.vector_ar.var_model import VAR

credentials = Credentials(username=os.getenv('username'), password=os.getenv('password'))
client = AmphoraDataRepositoryClient(credentials) 

Electricity_Amphora_id = '89c2e30d-78c8-46ef-b591-140edd84ddb6'
Weather_Amphora_id = '916058ba-cb52-40f6-8cf2-c4aafeb4c26e'
name = 'South_Australia_Electricity_Price.json'

# Upload data
mw = MicroWriter(write_key="bdfd44affd28e6c5b45329d6d4df7729")
time_range = a10a.DateTimeRange(_from = datetime.utcnow() + timedelta(hours=-1) , to= datetime.utcnow() )
electricity_amphora = client.get_amphora(Electricity_Amphora_id)
electricity_signals = electricity_amphora.get_signals()
df = electricity_signals.pull(date_time_range=time_range).to_pandas()
price = df['price']
mw.set(name=name,value=price[-1])

print(price)

# Do prediction for next value
length = mw.num_predictions

# pull data to do model
data_time_range = a10a.DateTimeRange(_from = datetime.utcnow() + timedelta(hours=-length/2) , to= datetime.utcnow() )
pdf = electricity_signals.pull(date_time_range=data_time_range).to_pandas()
price = pdf['price']
prices_of_interest = price[0:length]

elec_prices_diff = np.zeros(length-1)
for t in range(1,length):
    elec_prices_diff[t-1] = prices_of_interest[t] - prices_of_interest[t-1]
std_val = np.std(elec_prices_diff[abs(elec_prices_diff)<30])

weather_amphora = client.get_amphora(Weather_Amphora_id)
weather_signals = weather_amphora.get_signals()
wdf = weather_signals.pull(date_time_range=data_time_range).to_pandas()
data_of_interest = wdf[0:length]

training_data = np.transpose(np.array([prices_of_interest, data_of_interest['pressure'], data_of_interest['airTemp']]))

model = VAR(training_data)
model_fit = model.fit()

yhat = model_fit.forecast(model_fit.y, steps=1)

dist = np.random.laplace(yhat[0,0], std_val/np.sqrt(2), length)
res = mw.submit(name=name, values=dist, delay=None, verbose=None)
