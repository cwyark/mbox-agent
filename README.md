# BoxAgent 

BoxAgent is a bridge which receive streaming data from serial ports, and serialize/deserialize the streaming data, then log the data into file system.

## run unittest

```bash
$> python setup.py test --addopts='--cov=boxagent'
```

## build a release packages

```bash
$> python setup.py sdist --format=gztar
```
