# EPIF proxy benchmarks
This repository contains an automated benchmark setup for EPIF proxy candidates.

The requirements for the setup are (assuming Ubuntu 20.04): 

- Docker 19.03+
- Python 3.7+
- `make` (part of `build-essential`)

### Getting started

To start the default benchmarks, simply run the following command in the root directory:

```shell
$ make
```

The benchmark results will be stored in a file call `results.xlsx`, also in the root directory.

### Applications
The client applications that are supported are:

- [httping](https://github.com/flok99/httping)
- [wrk](https://github.com/wg/wrk)
- [iperf3](https://github.com/esnet/iperf)

### Configuration
It's possible to make custom benchmark configurations.

...
