__version__ = '0.2'
__name__ = 'pysonoff'
__url__ = 'https://bitbucket.org/angrysoft/pyxiaomi/src/master'
__author__ ='AngrySoft'
__email__ ='sebastian.zwierzchowski@gmail.com'

__all__ = ['DiyPlug', 'Mini', 'PowerState', 'Pulse', 'Discover']

from .devices import *
from .protocol import Discover