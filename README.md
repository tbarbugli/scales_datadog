scales_datadog
--------------

A python scales pusher to send data to datadog

This is implemented pretty much as copy of the scales' graphite pusher, data is pushed from a separate thread every 60 seconds.

You can start the pusher adding this code to your project

```python
from scales_datadog import DataDogPeriodicPusher
pusher = DataDogPeriodicPusher(
    api_key='my_datadog_api_key',
    api_application_key='my_datadog_application_key'
)
pusher.allow('*')
pusher.start()
```