from amphora.client import AmphoraDataRepositoryClient, Credentials
from microprediction import MicroWriter
import time
import os
from datetime import datetime, timedelta
import amphora_api_client as a10a
import numpy as np
import itertools
import statsmodels.api as sm

credentials = Credentials(username=os.getenv('username'), password=os.getenv('password'))
client = AmphoraDataRepositoryClient(credentials) 

Amphora_id = '89c2e30d-78c8-46ef-b591-140edd84ddb6'
name = 'South_Australia_Electricity_Price.json'

# Upload data
mw = MicroWriter(write_key="bdfd44affd28e6c5b45329d6d4df7729")
time_range = a10a.DateTimeRange(_from = datetime.utcnow() + timedelta(hours=-1) , to= datetime.utcnow() )
amphora = client.get_amphora(Amphora_id)
signals = amphora.get_signals()
df = signals.pull(date_time_range=time_range).to_pandas()
price = df['price']
mw.set(name=name,value=price[-1])

# Do prediction for next value
length = mw.num_predictions
prev_data = mw.get_lagged_values(name=name)
prev_data = np.array(prev_data[0:101])
current_val = prev_data[0]

model_fit = sm.load('predictive_model.pickle')
std_val = 8.1 # estimated previously

yhat = model_fit.forecast(model_fit.y, steps=1)
dist = np.random.laplace(yhat[0,0], std_val/np.sqrt(2), length)
res = mw.submit(name=name, values=dist, delay=None, verbose=None)
