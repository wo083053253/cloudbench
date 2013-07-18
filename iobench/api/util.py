#coding:utf-8

def _normalize_api_path(path):
    if not path.endswith("/"):
        path += "/"
    return path


def path_join(*components):
    assert components, "You can't join no paths!"
    parts = []
    parts.extend((c.strip("/") for c in components[:-1]))
    parts.append(components[-1].lstrip("/"))  # Don't strip a trailing slash!
    return "/".join(parts)