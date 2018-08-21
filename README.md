# BoxAgent 

Latest version is v.1

BoxAgent is a bridge software which receive streaming data from serial ports, and serialize/deserialize the streaming data, then log the data into file system in both JSON/SQL format

## Deploy guide

The BoxAgent installer is BoxAgent-1.x.tar.gz. you should use pip3 to install it.

```bash
$> sudo pip3 install BoxAgent-1.x.tar.gz
```

## Development guide

### run unittest

```bash
$> python setup.py test --addopts='--cov=boxagent'
```

### build a release packages

```bash
$> python setup.py sdist --format=gztar
```

### do not capture when test
```bash
$> python setup.py test --addopts "--capture=no"
```
