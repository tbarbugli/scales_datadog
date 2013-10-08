__author__ = 'Tommaso Barbugli'
__copyright__ = 'Copyright 2013, Tommaso Barbugli'
__credits__ = []


__license__ = 'BSD'
__version__ = '0.5.6'
__maintainer__ = 'Tommaso Barbugli'
__email__ = 'tbarbugli@gmail.com'
__status__ = 'Production'

try:
    import greplin, dogapi
except ImportError:
    pass # probably importing this at install time
else:
    from datadog import DataDogPeriodicPusher
