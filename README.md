# How to crowdsource better insights with Microprediction and Amphora Data.

Crowdsourcing is an effective way to get better predictions and forecasts. Crowdsourcing can be more effective an robust as a variety of methods are used and there is naturally no key-man risk. Microprediction is a leading crowdsourcing prediction website. We will show you how you can combine Amphora Data and Microprediction to get better insights.

We will show you how you can create a data set to be predicted using data obtained from Amphora. We will help you create and publish your own prediction. Finally we will show you how to pull the best forecasts from Microprediction and integrate with the rest of your data in Amphora. We will use the South Australian electricity price forecast for this tutorial but you can use any live time-series.

## Background

* If you haven't already, you need to create an Amphora Data account. You can do so here. 
* You also need an ID for Microprediction. They don't use traditional accounts, but instead use Memorable Unique Identifiers (MUID). Get started here.
* You need the latest packages from Microprediction and Amphora.
* You need access to a live time-series to be predicted. We will be getting our source data from the Australian Electricity Market Operator. 
    
## Method

### Publish data stream on Microprediction
Publishing data is very easy. You first need to create a `MicroWriter` object, then set a name and value
```py
mw = MicroWriter(write_key = my_muid)
mw.set(name=name,value=value)
```
Here the write key is your MUID. Name is a string and value is some number you have got from Amphora.

Our full code for pulling data from our South Australia Electricity Price Amphora and creating a data stream to predict is below
```py
from amphora.client import AmphoraDataRepositoryClient, Credentials
from microprediction import MicroWriter
import time
import os
from datetime import datetime, timedelta
import amphora_api_client as a10a

credentials = Credentials(username=os.getenv('username'), password=os.getenv('password'))
client = AmphoraDataRepositoryClient(credentials) 

Amphora_id = '89c2e30d-78c8-46ef-b591-140edd84ddb6'
name = 'South_Australia_Electricity_Price.json'

mw = MicroWriter(write_key="bdfd44affd28e6c5b45329d6d4df7729")
time_range = a10a.DateTimeRange(_from = datetime.utcnow() + timedelta(hours=-1) , to= datetime.utcnow() )
amphora = client.get_amphora(Amphora_id)
signals = amphora.get_signals()
df = signals.pull(date_time_range=time_range).to_pandas()
price = df['price']
mw.set(name=name,value=price[-1])
```

We can use Amphora Data and Microprediction to crowdsource better insights from data

    Create data for prediction on Microprediction using Amphora Data data
    Create your own prediction as a starting point
    Pull best prediction from Microprediction on Amphora Data


