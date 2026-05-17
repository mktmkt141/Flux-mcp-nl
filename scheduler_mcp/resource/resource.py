import json
from typing import Annotated, Any, Dict, Optional

ResourceStatus = Annotated[
    Dict[str, Any],
    "A detailed report of cluster resource availability from Flux.",
]


def _get_handle(uri: Optional[str] = None):
    import flux

    if uri:
        return flux.Flux(uri)
    return flux.Flux()


def _load_flux_resource_listing(handle):
    import flux.resource

    return flux.resource.list.resource_list(handle).get()


def get_flux_resource_list(
    uri: Annotated[
        Optional[str],
        "The Flux connection URI. Defaults to the local instance.",
    ] = None,
) -> ResourceStatus:
    """
    Retrieve the current free/up resources from a Flux instance.
    """
    handle = _get_handle(uri)
    listing = _load_flux_resource_listing(handle)

    return {
        "free": {
            "cores": listing.free.ncores,
            "gpus": listing.free.ngpus,
            "nodes": listing.free.nnodes,
            "hosts": list(listing.free.nodelist),
            "ranks": list(listing.free.ranks),
            "properties": json.loads(listing.free.get_properties()),
        },
        "up": {
            "cores": listing.up.ncores,
            "gpus": listing.up.ngpus,
            "nodes": listing.up.nnodes,
            "hosts": list(listing.up.nodelist),
            "ranks": list(listing.up.ranks),
            "properties": json.loads(listing.up.get_properties()),
        },
    }
