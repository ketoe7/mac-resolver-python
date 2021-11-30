# Resolve MAC Address
> Additional information or tagline

The purpose of this script is to resolve MAC address provided by user to the associated vendor.

## Getting started

To be able to use the application, user need to create an account on [macaddress.io](https://macaddress.io) and get the API key to the service.

The easiest way to run the script is to use the executable docker image.
Firstly it is necessary to build an image by executing the following command
from the root directory of the project:

```shell
docker build -t mac_resolver .
```

This command builds a docker image from the provided [Dockerfile](./Dockerfile).
The image is built based on lite python:3.9-alpine image. It updates the packages,
creates project directory, copy necessary files from the host, install required
python modules and sets an entrypoint to the execution of the python script [mac_resolver.py](./mac_resolver.py).

When docker image is build the following command executes the script:
```shell
docker container run --rm mac_resolver "-m <MAC_ADDRESS> -k <API_KEY_TO_MACADDRESS.IO>"
```
Alternatively it is possible to run application locally by installing python3.9 and 
python modules from [requirements.txt](./requirements.txt).
**NOTICE**: application was tested only on Ubuntu 20.04 and Alpine 3.15 but should work also on other operating systems.

## Features

* the main script of this project, [mac_resolver.py](./mac_resolver.py) can be used as a
standalone program resolving the MAC address. Such functionality can be useful in daily tasks of 
networks engineers.
* It can also be imported as a module.
* Together with Dockerfile it makes it very easy to use without setting proper environment.
* Code respects PEP8 principals and was analyzed with autopep8 utility.
* Code is prepared to be easily extended with new functionalities (that is why the MacResolver class is created)

## Arguments

When used as an executable docker image, without additional arguments, the application displays
its usage along with all supported arguments and description of their purpose:
```
docker container run --rm mac_resolver
usage: mac_resolver.py [-h] -m XX:XX:XX:XX:XX:XX -k API_KEY [-v]

Process query to Mac Address API.

optional arguments:
  -h, --help            show this help message and exit
  -m XX:XX:XX:XX:XX:XX, --mac XX:XX:XX:XX:XX:XX
                        MAC address to be resolved
  -k API_KEY, --api-key API_KEY
                        API key to authenticate your macaddress.io account
  -v, --verbose         Print detailed info, not only vendor company
```

When called directly, user should specify the `-h` of `--help` flag to see the above usage:
```
python mac_resolver.py -h
```

## Useful Links

- macaddress.io - 3rd party tool used to implement the application: https://macaddress.io/
- What is the MAC address?: https://en.wikipedia.org/wiki/MAC_address
