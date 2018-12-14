# mbox-agent

Latest version is v2.4

## Deploy guide

### installation

mbox-agent follows python's pip installation step. You could use pip3 to install it.

```bash
$> sudo pip3 install mbox-agent-2.4.tar.gz
```

Now you finish the mbox-agent installation

### How to configure mbox-agent executed when power up ?

```bash
$> sudo systemctl enable mbox-agent.service
```

### How to configure mbox-agent not to executed when power up ?

```bash
$> sudo systemctl disable mbox-agent.service
```

### How to start/stop mbox-agent ?

```bash
$> sudo systemctl start mbox-agent.service
```

```bash
$> sudo systemctl stop mbox-agent.service
```

### How to change heartbeat interval ?

Modify `/etc/mbox-agent/config.ini`, `[default]` -> `heartbeat`'s value. default is `300` mili seconds.

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
