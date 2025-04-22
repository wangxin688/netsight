from enum import IntEnum, StrEnum

# see reference from https://docs.opennms.com/meridian/2024/operation/deep-dive/topology/enlinkd/layer-3/ospf-discovery.html


class DeviceOperationalStatus(StrEnum):
    ONLINE = "Online"
    OFFLINE = "Offline"
    UNKNOWN = "Unknown"


class LatencyMetricType(StrEnum):
    latency = "latency"
    jitter = "jitter"
    packet_loss = "packet_loss"
    reachability = "reachability"


class DeviceMetricType(StrEnum):
    cpu_usage = "cpu_usage"
    memory_usage = "memory_usage"
    disk_usage = "disk_usage"
    temperature = "temperature"
    power_status = "power_status"
    fan_status = "fan_status"
    uptime = "uptime"


class TrafficMetricType(StrEnum):
    received = "received"
    transmitted = "transmitted"
    received_rate = "received_rate"
    transmitted_rate = "transmitted_rate"
    received_error = "received_error"
    transmitted_error = "transmitted_error"
    received_discard = "received_discard"
    transmitted_discard = "transmitted_discard"
    high_speed = "high_speed"
    duplex_status = "duplex_status"


class WirelessApMetricType(StrEnum):
    channel_eirp = "channel_eirp"
    channel_noise = "channel_noise"
    channel_interference = "interference"
    channel_utilization = "channel_utilization"
    channel_rx_rate = "channel_rx_rate"
    channel_tx_rate = "channel_tx_rate"
    channel_frame_retry = "channel_frame_retry"
    channel_clients = "channel_clients"


# OSPF-MIB
class OspfMetricType(StrEnum): ...


class BgpMetricType(StrEnum):
    peer_admin_status = "peer_admin_status"
    peer_operational_status = "peer_operational_status"
    peer_accepted_prefix = "peer_accepted_prefix"
    per_advertised_prefix = "per_advertised_prefix"


class BgpPeerAdminStatus(IntEnum):
    STOP = 1
    START = 2


class BgpPeerOperationalStatus(IntEnum):
    IDLE = 1
    OPEN_CONNECT = 2
    ACTIVE = 3
    OPEN_SENT = 4
    OPEN_CONFIRM = 5
    ESTABLISHED = 6
