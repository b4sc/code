from smtquery.intel.plugins import Probing
from smtquery.intel.manager import Manager



plugins = {
    "Probes" : Probing
}

def makeIntelManager (pluginnames):
    manager = Manager ()
    for p in pluginnames:
        if p in  plugins:
            manager.addPlugin (plugins[p] ())
        else:
            raise f"No plugin named {p}"
    return manager
    
