from typing import Annotated, Any, Dict, Optional, Union

SchedulerInfoResult = Annotated[
    Dict[str, Any],
    "Result of asking the Flux scheduler for internal queue or resource metadata.",
]


def _get_handle(uri: Optional[str] = None):
    import flux

    if uri:
        return flux.Flux(uri)
    return flux.Flux()


def flux_sched_qmanager_stats(
    uri: Annotated[
        Optional[str],
        "The Flux connection URI. Defaults to the local instance.",
    ] = None,
) -> SchedulerInfoResult:
    try:
        handle = _get_handle(uri)
        stats = handle.rpc("sched-fluxion-qmanager.stats-get").get()
        return {"success": True, "error": None, "stats": stats}
    except Exception as exc:
        return {"success": False, "error": str(exc), "stats": None}


def flux_sched_resource_info(
    jobid: Annotated[Union[int, str], "The scheduler job identifier to inspect."],
    uri: Annotated[Optional[str], "The Flux connection URI. Defaults to the local instance."] = None,
) -> SchedulerInfoResult:
    try:
        import flux.job

        handle = _get_handle(uri)
        resource_info = handle.rpc(
            "sched-fluxion-resource.info", {"jobid": flux.job.JobID(jobid)}
        ).get()
        return {
            "success": True,
            "error": None,
            "jobid": str(jobid),
            "resource_info": resource_info,
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "jobid": str(jobid),
            "resource_info": None,
        }


def flux_sched_resource_status(
    uri: Annotated[Optional[str], "The Flux connection URI. Defaults to the local instance."] = None,
) -> SchedulerInfoResult:
    try:
        handle = _get_handle(uri)
        resource_status = handle.rpc("sched-fluxion-resource.status").get()
        return {"success": True, "error": None, "resource_status": resource_status}
    except Exception as exc:
        return {"success": False, "error": str(exc), "resource_status": None}


def flux_sched_resource_find(
    criteria: Annotated[str, "A scheduler-side resource query such as 'status=up'."],
    find_format: Annotated[Optional[str], "Optional output format such as 'json'."] = None,
    uri: Annotated[Optional[str], "The Flux connection URI. Defaults to the local instance."] = None,
) -> SchedulerInfoResult:
    try:
        handle = _get_handle(uri)
        payload = {"criteria": criteria}
        if find_format:
            payload["format"] = find_format
        resource_find = handle.rpc("sched-fluxion-resource.find", payload).get()
        return {
            "success": True,
            "error": None,
            "criteria": criteria,
            "find_format": find_format,
            "resource_find": resource_find,
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "criteria": criteria,
            "find_format": find_format,
            "resource_find": None,
        }


def flux_sched_resource_set_property(
    resource_path: Annotated[str, "The path to the resource vertex, e.g. node0.core0."],
    key_val: Annotated[str, "The property string in key=value format."],
    uri: Annotated[Optional[str], "The Flux connection URI. Defaults to the local instance."] = None,
) -> SchedulerInfoResult:
    try:
        handle = _get_handle(uri)
        payload = {"sp_resource_path": resource_path, "sp_keyval": key_val}
        result = handle.rpc("sched-fluxion-resource.set_property", payload).get()
        return {
            "success": True,
            "error": None,
            "resource_path": resource_path,
            "key_val": key_val,
            "result": result,
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "resource_path": resource_path,
            "key_val": key_val,
            "result": None,
        }


def flux_sched_resource_get_property(
    resource_path: Annotated[str, "The path to the resource vertex."],
    key: Annotated[str, "The property key to retrieve."],
    uri: Annotated[Optional[str], "The Flux connection URI. Defaults to the local instance."] = None,
) -> SchedulerInfoResult:
    try:
        handle = _get_handle(uri)
        payload = {"gp_resource_path": resource_path, "gp_key": key}
        result = handle.rpc("sched-fluxion-resource.get_property", payload).get()
        return {
            "success": True,
            "error": None,
            "resource_path": resource_path,
            "key": key,
            "result": result,
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "resource_path": resource_path,
            "key": key,
            "result": None,
        }


def flux_sched_resource_remove_property(
    resource_path: Annotated[str, "The path to the resource vertex."],
    key: Annotated[str, "The property key to remove."],
    uri: Annotated[Optional[str], "The Flux connection URI. Defaults to the local instance."] = None,
) -> SchedulerInfoResult:
    try:
        handle = _get_handle(uri)
        payload = {"resource_path": resource_path, "key": key}
        result = handle.rpc("sched-fluxion-resource.remove_property", payload).get()
        return {
            "success": True,
            "error": None,
            "resource_path": resource_path,
            "key": key,
            "result": result,
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "resource_path": resource_path,
            "key": key,
            "result": None,
        }


def flux_sched_resource_set_status(
    resource_path: Annotated[str, "The path to the resource vertex."],
    status: Annotated[str, "The desired status string such as up or down."],
    uri: Annotated[Optional[str], "The Flux connection URI. Defaults to the local instance."] = None,
) -> SchedulerInfoResult:
    try:
        handle = _get_handle(uri)
        payload = {"resource_path": resource_path, "status": status}
        result = handle.rpc("sched-fluxion-resource.set_status", payload).get()
        return {
            "success": True,
            "error": None,
            "resource_path": resource_path,
            "status": status,
            "result": result,
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "resource_path": resource_path,
            "status": status,
            "result": None,
        }


def flux_sched_resource_stats(
    uri: Annotated[Optional[str], "The Flux connection URI. Defaults to the local instance."] = None,
) -> SchedulerInfoResult:
    try:
        handle = _get_handle(uri)
        stats = handle.rpc("sched-fluxion-resource.stats-get").get()
        return {"success": True, "error": None, "stats": stats}
    except Exception as exc:
        return {"success": False, "error": str(exc), "stats": None}


def flux_sched_resource_stats_clear(
    uri: Annotated[Optional[str], "The Flux connection URI. Defaults to the local instance."] = None,
) -> SchedulerInfoResult:
    try:
        handle = _get_handle(uri)
        result = handle.rpc("sched-fluxion-resource.stats-clear").get()
        return {"success": True, "error": None, "result": result}
    except Exception as exc:
        return {"success": False, "error": str(exc), "result": None}


def flux_sched_resource_params(
    uri: Annotated[Optional[str], "The Flux connection URI. Defaults to the local instance."] = None,
) -> SchedulerInfoResult:
    try:
        handle = _get_handle(uri)
        params = handle.rpc("sched-fluxion-resource.params").get()
        return {"success": True, "error": None, "params": params}
    except Exception as exc:
        return {"success": False, "error": str(exc), "params": None}


def flux_sched_resource_ns_info(
    rank: Annotated[int, "The target rank."],
    type_name: Annotated[str, "The resource type name, e.g. core."],
    identity: Annotated[int, "The raw resource ID."],
    uri: Annotated[Optional[str], "The Flux connection URI. Defaults to the local instance."] = None,
) -> SchedulerInfoResult:
    try:
        handle = _get_handle(uri)
        payload = {"rank": rank, "type-name": type_name, "id": identity}
        result = handle.rpc("sched-fluxion-resource.ns-info", payload).get()
        return {
            "success": True,
            "error": None,
            "rank": rank,
            "type_name": type_name,
            "identity": identity,
            "result": result,
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "rank": rank,
            "type_name": type_name,
            "identity": identity,
            "result": None,
        }
