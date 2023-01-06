from pydevmgr_core import register as _register

def register(*args, namespace="vlt", **kwargs):
    """ class register wit default namespace 'vlt' """
    return _register(*args, namespace=namespace, **kwargs) 
