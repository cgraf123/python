import argparse
from enum import Enum
import logging
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin
from uuid import UUID

import requests


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DEFAULT_HOST = "http://127.0.0.1:5000/api/"


class Command(Enum):
    """Enum for client command line."""

    ADD = "add"
    DELETE = "delete"
    GET_UUID = "get_uuid"
    GET_UUIDS = "get_uuids"
    UPDATE = "update"

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return other == self.value


class Client:
    """API client helper class."""

    host: str

    def __init__(self, host: str):
        """Client constructor."""
        self.host = host

    @staticmethod
    def log_transaction(response: requests.Response):
        """Log requests transaction details."""
        request = response.request
        logger.info(f"request url: {request.url}")
        logger.info(f"request header: {request.headers}")
        logger.info(f"request method: {request.method}")
        logger.info(f"response status: {response.status_code}")
        logger.info(f"response content: {response.content}")

    def add(self, path: Path, uuid: Optional[UUID] = None):
        """Add/Update GeoJSON endpoint handler."""
        url = urljoin(self.host, str(uuid)) if uuid else self.host
        with open(path) as f:
            response = requests.post(url=url, files={"geojson": f})
        self.log_transaction(response)

    def delete(self, uuid: UUID):
        """Delete GeoJSON UUID handler."""
        response = requests.delete(url=urljoin(self.host, str(uuid)))
        self.log_transaction(response)
        pass

    def get_uuid(self, uuid: UUID):
        """Get UUID GeoJSON handler."""
        print(self.host)
        print(uuid)
        print(urljoin(self.host, str(uuid)))
        response = requests.get(url=urljoin(self.host, str(uuid)))
        self.log_transaction(response)

    def get_uuids(self):
        """Get UUIDs handler."""
        response = requests.get(url=self.host)
        self.log_transaction(response)


def main(args: argparse.Namespace):
    """Main entry point handler for command line client."""
    client = Client(args.host)
    if args.command == Command.ADD:
        client.add(Path(args.file))
    elif args.command == Command.UPDATE:
        client.add(Path(args.file), args.uuid)
    elif args.command == Command.DELETE:
        client.delete(args.uuid)
    elif args.command == Command.GET_UUID:
        client.get_uuid(args.uuid)
    elif args.command == Command.GET_UUIDS:
        client.get_uuids()
    else:
        logger.error(f"unhandled command: {args.command}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("API client script", conflict_handler="resolve")
    parser.add_argument("--host", type=str, default=DEFAULT_HOST,
                        help="API host address")
    subparsers = parser.add_subparsers(help="command help", dest="command")
    parser_add = subparsers.add_parser(f"{Command.ADD}", help="add help")
    parser_update = subparsers.add_parser(f"{Command.UPDATE}", help="update help")
    for subparser in (parser_add, parser_update):
        subparser.add_argument("-f", "--file", required=True, help="file to upload")
    parser_delete = subparsers.add_parser(f"{Command.DELETE}", help="delete UUID")
    parser_get_uuid = subparsers.add_parser(f"{Command.GET_UUID}", help="get UUID content")
    for subparser in (parser_update, parser_delete, parser_get_uuid):
        subparser.add_argument("-u", "--uuid", required=True, help="UUID to target")
    parser_get_uuids = subparsers.add_parser(f"{Command.GET_UUIDS}", help="get all UUIDs")
    parsed_args = parser.parse_args()
    main(parsed_args)
