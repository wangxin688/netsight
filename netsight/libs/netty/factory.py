from typing import Protocol, TypeVar

from netmiko import BaseConnection, ConnectHandler, ConnectionException

SessionT = TypeVar("SessionT")


class NettyFactory(Protocol):
    def get_hostname(self) -> str: ...

    def get_manufacturer(self) -> str: ...

    def get_serial_number(self) -> str: ...

    def get_software_version(self) -> str: ...

    def get_device_type(self) -> str: ...

    def get_modules(self) -> list[str]: ...

    def get_stacks(self) -> list[str]: ...

    def get_interfaces(self) -> list[str]: ...

    def get_lldp_neighbors(self) -> list[str]: ...

    def get_arp_table(self) -> list[str]: ...

    def get_mac_table(self) -> list[str]: ...

    def get_ospf_neighbors(self) -> list[str]: ...

    def get_bgp_neighbors(self) -> list[str]: ...

    def get_ntp_servers(self) -> list[str]: ...

    def get_interfaces_ip(self) -> str: ...

    def get_interfaces_vlans(self) -> list[str]: ...

    def get_routing_table(self) -> list[str]: ...


class NettySshFactory(NettyFactory):
    session: BaseConnection | None = None

    def __init__(
        self,
        ip_address: str,
        port: int,
        username: str,
        password: str,
        platform: str,
        secret: str | None = None,
        timeout: int = 15,
    ) -> None:
        self.ip_address = ip_address
        self.port = port
        self.username = username
        self.password = password
        self.secret = secret
        self.timeout = timeout
        self.device_type = platform

    def __enter__(self) -> None:
        if self.session is not None:
            return
        try:
            session = ConnectHandler(
                device_type=self.device_type,
                host=self.ip_address,
                username=self.username,
                password=self.password,
                secret=self.secret,
                port=self.port,
                timeout=self.timeout,
            )
        except ConnectionException as e:
            raise ValueError("Unable to connect to device.") from e  # replace with custom exception
        self.session = session
        return

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: ANN001
        """Close the session if it's open"""
        if self.session is None:
            return
        self.session.disconnect()
        self.session = None
        return

    def ping(self) -> None: ...

    def traceroute(self) -> None: ...

    def get_running_config(self) -> None: ...

    def get_startup_config(self) -> None: ...


class NettySnmpFactory(NettyFactory): ...
