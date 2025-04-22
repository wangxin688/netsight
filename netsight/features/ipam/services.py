from netsight.core.repositories import BaseRepository
from netsight.features.ipam import models, schemas


class BlockService(BaseRepository[models.Block, schemas.BlockCreate, schemas.BlockUpdate, schemas.BlockQuery]): ...


class PrefixService(BaseRepository[models.Prefix, schemas.PrefixCreate, schemas.PrefixUpdate, schemas.PrefixQuery]): ...


class ASNService(BaseRepository[models.ASN, schemas.ASNCreate, schemas.ASNUpdate, schemas.ASNQuery]): ...


class IPRangeService(
    BaseRepository[models.IPRange, schemas.IPRangeCreate, schemas.IPRangeUpdate, schemas.IPRangeQuery]
): ...


class IPAddressService(
    BaseRepository[models.IPAddress, schemas.IPAddressCreate, schemas.IPAddressUpdate, schemas.IPAddressQuery]
): ...


class VLANService(BaseRepository[models.VLAN, schemas.VLANCreate, schemas.VLANUpdate, schemas.VLANQuery]): ...


class VRFService(BaseRepository[models.VRF, schemas.VRFCreate, schemas.VRFUpdate, schemas.VRFQuery]): ...


class RouteTargetService(
    BaseRepository[models.RouteTarget, schemas.RouteTargetCreate, schemas.RouteTargetUpdate, schemas.RouteTargetQuery]
): ...


block_service = BlockService(models.Block)
prefix_service = PrefixService(models.Prefix)
asn_service = ASNService(models.ASN)
ip_range_service = IPRangeService(models.IPRange)
ip_address_service = IPAddressService(models.IPAddress)
vlan_service = VLANService(models.VLAN)
vrf_service = VRFService(models.VRF)
route_target_service = RouteTargetService(models.RouteTarget)
