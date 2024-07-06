from icmplib import Host, async_multiping, async_ping
from tcppinglib import TCPHost, async_multi_tcpping, async_tcpping


async def ping_alive(address: str) -> bool:
    result = await async_ping(address=address, count=3, interval=0.2, privileged=False)
    return result.is_alive


async def multi_ping_alive(addresses: list[str]) -> dict[str, bool]:
    results: list[Host] = await async_multiping(
        addresses=addresses, count=2, interval=0.2, timeout=2, concurrent_tasks=30, privileged=False
    )
    return {result.address: result.is_alive for result in results}


async def ssh_alive(address: str, port: int = 22) -> bool:
    result = await async_tcpping(address=address, port=port, count=3, interval=0.2)
    return result.is_alive


async def multi_ssh_alive(addresses: list[str], port: int = 22) -> dict[str, bool]:
    results: list[TCPHost] = await async_multi_tcpping(
        addresses=addresses, port=port, count=2, interval=0.2, concurrent_tasks=30
    )
    return {result.ip_address: result.is_alive for result in results}
