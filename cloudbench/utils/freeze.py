#coding:utf-8
FROZEN_TAG = "__frozen__"


def freeze_dict(obj):
    if isinstance(obj, dict):
        dict_items = list(obj.items())
        dict_items.append((FROZEN_TAG, True))
        return tuple([(k, freeze_dict(v)) for k, v in dict_items])
    return obj


def unfreeze_dict(obj):
    if isinstance(obj, tuple):
        if (FROZEN_TAG, True) in obj:
            out = dict((k, unfreeze_dict(v)) for k, v in obj)
            del out[FROZEN_TAG]
            return out
    return obj
