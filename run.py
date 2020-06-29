from amphora.client import AmphoraDataRepositoryClient, Credentials
from microprediction import MicroWriter
import time
import os
from datetime import datetime, timedelta
import amphora_api_client as a10a
import numpy as np

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
prev_data = mw.get_lagged_values(name=name)
prev_data = np.array(prev_data[0:501])
current_val = prev_data[0]
difs = prev_data[1:501] - prev_data[0:500]
difs_2 = [difs, difs]
difs_f =  list(itertools.chain.from_iterable(difs_2))

new_vals = current_val + difs_f
res = mw.submit(name=name,values=new_vals,delay=None, verbose=None)
