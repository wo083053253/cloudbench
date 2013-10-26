#coding:utf-8


try:
    __import__("boto")
except ImportError:
    boto_importable = False
else:
    boto_importable = True

try:
    __import__("pyrax")
except ImportError:
    pyrax_importable = False
else:
    pyrax_importable = True
