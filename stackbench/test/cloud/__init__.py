#coding:utf-8
def boto_importable():
    try:
        import boto
    except ImportError:
        return False
    return True