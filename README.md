# DataLogger 

Latest version is v2.4

## Deploy guide

### installation

DataLogger follows python's pip installation step. You could use pip3 to install it.

```bash
$> sudo pip3 install DataLogger-2.4.tar.gz
```

Now you finish the BoxAgent installation

### How to configure BoxAgent executed when power up ?

```bash
$> sudo systemctl enable datalogger.service
```

### How to configure BoxAgent not to executed when power up ?

```bash
$> sudo systemctl disable datalogger.service
```

### How to start/stop BoxAgent ?

```bash
$> sudo systemctl start datalogger.service
```

```bash
$> sudo systemctl stop datalogger.service
```

### How to change heartbeat interval ?

Modify `/etc/boxagent/config.ini`, `[default]` -> `heartbeat`'s value. default is `300` mili seconds.

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
