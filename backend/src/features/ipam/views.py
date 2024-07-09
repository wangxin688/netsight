from sqladmin import ModelView

from src.features.ipam import models


class BlockView(ModelView, model=models.Block):
    category = "IPAM"
    name = "IP Block"
    name_plural = "IP Blocks"
    column_list = [
        models.Block.name,
        models.Block.block,
        models.Block.size,
        models.Block.range,
        models.Block.is_private,
        models.Block.description,
    ]
    column_searchable_list = [models.Block.name]
    column_filters = [
        models.Block.block,
        models.Block.is_private,
    ]
    icon = "codepen"


class PrefixView(ModelView, model=models.Prefix):
    category = "IPAM"
    name = "Prefix"
    name_plural = "Prefixes"


class ASNView(ModelView, model=models.ASN):
    category = "IPAM"
    name = "ASN"
    name_plural = "ASNs"


class VLANView(ModelView, model=models.VLAN):
    category = "IPAM"
    name = "VLAN"
    name_plural = "VLANS"
