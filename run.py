from amphora.client import AmphoraDataRepositoryClient, Credentials
from microprediction import MicroWriter
import time
import os   

credentials = Credentials(username=os.getenv('username'), password=os.getenv('password'))
client = AmphoraDataRepositoryClient(credentials) 

SA_id = '89c2e30d-78c8-46ef-b591-140edd84ddb6'

mw = MicroWriter(write_key="bdfd44affd28e6c5b45329d6d4df7729")

amphora = client.get_amphora(SA_id)
signals = amphora.get_signals()
df = signals.pull().to_pandas()
price = df['price']
print(price[-1])
mw.set(name='South_Australia_Electricity_Price.json',value=price[-1])
