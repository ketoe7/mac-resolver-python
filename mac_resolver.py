#!/usr/bin/env python3
"""MAC Address Resolver.

This script allows the user to resolve given MAC address to the
associated vendor.

This tool accepts the following arguments:
    * -m,--mac     - a MAC address which should be resolved.
    * -k,--api_key - an API key to authenticate 3rd party tool macaddress.io
    * -v,--verbose - makes output more verbose.
    * -h,--help    - display detailed description of syntax and arguments.

This script requires the following modules to be install within the
Python environment you are running this script in:
    * requests

This file can also be imported as a module and contains the following
classes and functions:

    * MacResolver - base class which represents a handler for MAC address
                    resolving.
"""

import logging
import requests
import argparse
import json
import re


class NetworkError(Exception):
    """Raised when resolve method cannot connect with macaddress.io"""
    pass


class HTTPError(Exception):
    """Raised when macaddress.io responds with an HTTP error"""
    pass


class WrongMacFormat(Exception):
    """Raised when MacResolver get wrong Mac address as an parameter"""
    pass


class MacResolver:
    """A class used to represent a handler for MAC address resolving.

    Attributes
    ----------
    MACADDRESS_HOSTNAME : str
        class attribute which stores the hostname of 3rd party tool used to
        resolve the MAC address.
    MACADDRESS_API_URL : str
        class attribute which stores a full url to API of MACADDRESS_HOSTNAME.
    api_key : str
        API key needed for authentication.
    return_json : bool
        if set to True the MacResolver will return a json with resolved company
        in format {"<mac>": "company"} (default is False).

    Methods
    -------
    resolve(mac)
        Query 3rd party tool in order to resolve given MAC address to
        a specific vendor.
    handle_http_errors(status_code)
        Handle possible HTTP errors returned by 3rd party tool.
    """

    MACADDRESS_HOSTNAME = 'macaddress.io'
    MACADDRESS_API_URL = f'https://api.{MACADDRESS_HOSTNAME}/v1'

    def __init__(self, api_key: str) -> None:
        f"""
        Parameters
        ----------
        api_key : str
            API key needed to authenticate {self.MACADDRESS_HOSTNAME}
        """

        self.api_key = api_key

    def resolve(self, mac: str, return_json: bool = False) -> str:
        """Returns the associated vendor with given MAC address.

        If the optional argument `return_json` is to True a json containing
        MAC address and associated vendor is returned.

        Parameters
        ----------
        mac : str
            The MAC address which should be resolved.
        return_json : bool, optional
            if set to True the method will return a json object with resolved
            company in format {"<mac_address>": "company"} (default is False)

        Raises
        ------
        NetworkError
            If request to macaddress.io failed due to the network error.
        HTTPError
            If macaddress.io responses with HTTP error.
        WrongMacFormat
            If 'mac' variable is not in correct format of MAC address.

        Returns
        -------
        vendor : str
            Vendor associated with given MAC address
        """

        # check if format of the given MAC address is correct
        pattern = r'[0-9a-f]{2}([-:.]?)[0-9a-f]{2}(\1[0-9a-f]{2}){4}$'
        if not re.match(pattern, mac.lower()):
            raise WrongMacFormat(
                'Wrong format of MAC address! Provide correct MAC address in '
                'the following format: XX:XX:XX:XX:XX:XX where X represents '
                'the hexadecimal digit'
            )

        headers = {"X-Authentication-Token": self.api_key}
        params = {'search': mac, 'output': 'vendor'}

        try:
            response = requests.get(
                self.MACADDRESS_API_URL,
                headers=headers,
                params=params
            )
        except requests.ConnectionError:
            raise NetworkError(
                f'Connection Error during processing reqest to '
                f'{self.MACADDRESS_API_URL} for mac {mac}. '
            )
        except requests.Timeout:
            raise NetworkError(
                f'Timeout during processing request to '
                f'{self.MACADDRESS_API_URL} for mac {mac}. '
            )
        except Exception:
            raise NetworkError(
                f'Unknown error during processing request to '
                f'{self.MACADDRESS_API_URL} for mac {mac}. '
            )

        if response.ok:
            if return_json:
                return json.dumps({mac: response.text})
            else:
                return response.text
        else:
            reason = self.handle_http_errors(response.status_code)
            raise HTTPError(
                f'Error detected in the response from '
                f'{self.MACADDRESS_API_URL} for MAC address {mac}. '
                f'Status code: {response.status_code}, reason: {reason}'
            )

    @classmethod
    def handle_http_errors(cls, status_code: int) -> str:
        """Returns a message containing a description of the HTTP error
        identified by given status_code.

        Parameters
        ----------
        status_code : int
            Status code of the HTTP response which should be handled.

        Returns
        -------
        msg : str
            Message with description of the HTTP error.
        """

        if status_code == 400:
            # It should not be possible to get this error cause only supported
            # parameters are used by script.
            msg = 'Invalid parameters.'
        elif status_code == 401:
            msg = 'Access restricted. Enter the correct API key.'
        elif status_code == 402:
            msg = f'Access restricted. Check the credits balance on the '
            f'account of  {cls.MACADDRESS_HOSTNAME} associated with provided '
            f'API key ({cls.api_key}).'
        elif status_code == 422:
            # It should not be possible to get this error because MAC address
            # from the user is already validated.
            msg = 'Invalid MAC address was received.'
        elif status_code == 429:
            msg = 'Too many requests. Try your call again later.'
        elif status_code == 500:
            msg = f'Internal server error. Try again or contact '
            f'{cls.MACADDRESS_HOSTNAME}'
        else:
            msg = 'Unknown error.'
        return msg


if __name__ == '__main__':
    logFormatter = logging.Formatter(
        "%(asctime)s [%(levelname)-5.5s]  %(message)s"
    )
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)

    parser = argparse.ArgumentParser(
        description='Process query to Mac Address API.'
    )

    parser.add_argument(
        '-m',
        '--mac',
        dest='mac',
        metavar='XX:XX:XX:XX:XX:XX',
        type=str,
        required=True,
        help='MAC address to be resolved'
    )
    parser.add_argument(
        '-k',
        '--api-key',
        dest='api_key',
        required=True,
        help='API key to authenticate your macaddress.io account'
    )
    parser.add_argument(
        '-v',
        '--verbose',
        dest='verbose',
        action='store_true',
        help='Print detailed info, not only vendor company'
    )

    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.debug('Instantiating instance of the class MacResolver')
    resolver = MacResolver(args.api_key)
    try:
        associated_vendor = resolver.resolve(args.mac)
    except WrongMacFormat as e:
        logger.error(e)
    except NetworkError as e:
        logger.error(e)
    except HTTPError as e:
        logger.error(e)
    else:
        logger.info(
            f'MAC address {args.mac} is associated with vendor '
            f'"{associated_vendor}"'
        )
