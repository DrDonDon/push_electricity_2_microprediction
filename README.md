# How to crowdsource better insights with Microprediction and Amphora Data

Crowdsourcing is an effective way to get better predictions and forecasts. Crowdsourcing can be more effective and robust; a variety of methods are used and there is naturally no key-man risk. [Microprediction](https://www.microprediction.org/) is a leading crowdsourcing prediction platform. In this walkthrough we will combine [Amphora Data](https://amphoradata.com) and Microprediction to get better insights.

For this tutorial we will use the South Australian electricity price forecast, but you can use any live time-series. We will show you how you can **create a data stream to be predicted using data obtained from Amphora**. We will help you **create and publish your own prediction**. Finally we will show you how to **pull the best forecasts from Microprediction and integrate with the rest of your data in Amphora**.

## Background

We use Amphora Data to manage our data flows and access and share third-party data. We are using Microprediction to share and crowdsource predictions. We assume basic knowledge of python and Amphora Data for this walkthrough. You can get all the details on how to use [Amphora here.](https://www.amphoradata.com/docs/contents/)

* If you haven't already, you need to create an Amphora Data account. [You can do so here](https://identity.amphoradata.com/Register). 
* You also need an ID for Microprediction. They don't use traditional accounts, but instead use Memorable Unique Identifiers (MUID). [Get started here](https://www.microprediction.org/muids.html).
* You need the latest packages from Microprediction and Amphora from pypi.
* You need access to a live time-series to be predicted. We will get source data from the [Australian Electricity Market Operator](https://aemo.com.au/en/energy-systems/electricity/national-electricity-market-nem/data-nem/data-dashboard-nem). 
    
## Method

### Publish data stream on Microprediction
Publishing data is very easy. You first need to create a `MicroWriter` object, then set a `name` and `value`
```py
mw = MicroWriter(write_key = my_muid)
mw.set(name=name,value=value)
```
Here the `write_key` is your MUID. `name` is a string and is the name of your prediction. `value` is some number you have got from Amphora.

Our full code for pulling data from the South Australia Electricity Price Amphora and creating a data stream to predict is below
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
df = signals.pull(date_time_range = time_range).to_pandas()
price = df['price']
mw.set(name = name, value = price[-1])
```
This stream is [available here.](https://www.microprediction.org/stream_dashboard.html?stream=South_Australia_Electricity_Price)

### Create your own prediction

We now want to create our own prediction for the data stream. This helps set the standard for predictions and provides a floor in the quality of predictions you use.

You can predict different timescales with Microprediction. For simplicities sake, we will try to predict the next value.

Microprediction takes in a distibution of predictions, rather than a single value. 

The main code you need is 
```py
mw = MicroWriter(write_key="bdfd44affd28e6c5b45329d6d4df7729")
mw.submit(name = name, values = values, delay = None)
```
Here `name` is the prediction name, `values` is a distribution for the next value, and `delay` corresponds to how long you want to predict in the future.

Our full prediction code, which simply takes the last 225 values to create a nieve distribution, is below. You can obviously create far more sophisticated prediction alogrithms but thats not the objective of this document.
```py
prev_data = mw.get_lagged_values(name=name)
prev_data = np.array(prev_data[0:226])
current_val = prev_data[0]
difs = prev_data[1:226] - prev_data[0:225]
new_vals = current_val + difs
res = mw.submit(name=name,values=new_vals,delay=None, verbose=None)
```
The results of this prediction are [here](https://www.microprediction.org/stream_dashboard.html?stream=South_Australia_Electricity_Price) under the MUID of `Osteal Beetle`.

### Retrieving a distribution of future values

After waiting a little while, the Microprediction community will start contributing lots of predictions.

We now want to get a distribution of future values. First let's pick a horizon. The choices are in the vector:
```py
mw.DELAYS
```
We'll take a 15 minute ahead forecast. This corresponds to the next value for the electricity price stream.
```py
delay15m = 910
```
910 is the number of seconds we want to look ahead (e.g. 15 x 60) plus a 10 second computation delay.

We can retrieve the "community" distribution of electricity price for 15 minutes ahead as follows: 
```py
mr = MicroReader()
cdf = mr.get_cdf(name=name, delay=delay15m)
```    
You'll notice this contains a list of x-values and corresponding values of the cumulative distribution. You can use this distribution to get the mean, median or any other summary statistic you want. 

### Push median prediction from Microprediction to Amphora Data

It can be hard to interpret a point estimate when the distribution of outcomes is wild and varied. You can define the median as 
```py
median_forecast_value = mr.inv_cdf(self, name, delay=delay15m, p=0.5)
```
    
This can be used to create a new time series in Amphora. This can be simply done with 
```py
Signals = [dict(t = datetime_stamp, median_forecast_value = median_forecast_value)] 
amphora.push_signals_dict_array(Signals) 
```    
    
## Future developments

This is a brief first post on how to crowdsource better insights with Amphora Data and Microprediction. Topics we will cover in the future include
* Longer range predictions
* Using z-score's from Microprediction in Amphora
* Soliciting 2d and 3d predictions. 
* Using many data sources to create better predictions

Please reach out over [email](mailto:contact@amphoradata.com) or collaborate on GitHub if you have any queries or requests.
