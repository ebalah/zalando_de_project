import traceback

class ZalandoException(Exception):

    def __init__(self, msg, exc_error, logger=None) -> None:
        self.exc_msg = msg
        self.exc_error = exc_error
        self._logger = logger
        super().__init__(self.exc_msg)

    def _trace(self):
        return traceback.format_exc()
    
    def dbg(self):
        if self._logger:
            self._logger.warn(self.exc_msg)
        return self
    
    def err(self):
        if self._logger:
            self._logger.error(self._trace(), show_details=False)
        return self
    
    def log(self):
        if self._logger:
            self._logger.warn(self.exc_msg, _rbr=True)
            self._logger.error(self._trace(), show_details=False)
        return self



class UnableToOpenNewTabException(ZalandoException):
    
    def __init__(self, msg, *args, **kwargs) -> None:
        super().__init__("Failed to open the new tab : "
                         + msg, *args, **kwargs)


class UnableToCloseNewTabException(ZalandoException):
    
    def __init__(self, msg, *args, **kwargs) -> None:
        super().__init__("Failed to close the new tab : "
                         + msg, *args, **kwargs)


class ArticleProcessingException(ZalandoException):
    
    def __init__(self, msg, *args, **kwargs) -> None:
        super().__init__("Failed to process the article : "
                         + msg, *args, **kwargs)
        

class ArticlesProcessingException(ZalandoException):
    
    def __init__(self, msg, *args, **kwargs) -> None:
        super().__init__("Failed to process the article : "
                         + msg, *args, **kwargs)
        
        
class UnableToConnectException(ZalandoException):
    
    def __init__(self, msg, *args, **kwargs) -> None:
        super().__init__("Failed to continue processing : "
                         + msg, *args, **kwargs)
        
        
class WindowAlreadyClosedException(ZalandoException):
    
    def __init__(self, msg, *args, **kwargs) -> None:
        super().__init__("Failed to continue processing : "
                         + msg, *args, **kwargs)
        
class KeyboardInterruptException(ZalandoException):
    
    def __init__(self, msg, *args, **kwargs) -> None:
        super().__init__("Failed to continue processing : "
                         + msg, *args, **kwargs)