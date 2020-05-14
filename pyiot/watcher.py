from threading import Thread

class WatcherBaseDriver:
    def watch(self, handeler):
        pass
    
    def stop(self):
        pass  
    

class Watcher:
    def __init__(self, driver=None):
        self._report_handlers = set()
        if isinstance(driver, WatcherBaseDriver):
            Thread(target=driver.watch, args=(self._handler,), daemon=True).start()
            
    def _handler(self, msg: dict) -> None:
        Thread(target=self._handle_events, args=(msg,)).start()
    
    def add_report_handler(self, handler):
        self._report_handlers.add(handler)
    
    def _handle_events(self, event):
        for handler in self._report_handlers:
            handler(event)