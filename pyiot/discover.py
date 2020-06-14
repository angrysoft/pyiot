class Discover:
    engines = []
    
    def __init__(self):
        pass
    

class DiscoverSonoff:
    pass

class DiscoverSony:
    pass

class DiscoverYlight:
    pass

Discover.engines.append(DiscoverSonoff())

if __name__ == "__main__":
    d = Discover()
    print(d.engines)