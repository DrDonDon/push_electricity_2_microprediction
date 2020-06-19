from amphora.client import AmphoraDataRepositoryClient, Credentials
from microprediction import MicroWriter
import time
import os
from datetime import datetime, timedelta
import amphora_api_client as a10a

credentials = Credentials(username=os.getenv('username'), password=os.getenv('password'))
client = AmphoraDataRepositoryClient(credentials) 

SA_id = '89c2e30d-78c8-46ef-b591-140edd84ddb6'

mw = MicroWriter(write_key="bdfd44affd28e6c5b45329d6d4df7729")

time_range = a10a.DateTimeRange(_from = datetime.utcnow() + timedelta(hours=-1) , to= datetime.utcnow() )

amphora = client.get_amphora(Amphora_id)
signals = amphora.get_signals()
df = signals.pull(date_time_range=time_range).to_pandas()

price = df['price']

mw.set(name='South_Australia_Electricity_Price.json',value=price[-1])
