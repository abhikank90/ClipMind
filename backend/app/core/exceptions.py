class ClipMindException(Exception):
    pass

class VideoNotFoundException(ClipMindException):
    pass

class VideoProcessingException(ClipMindException):
    pass

class InvalidVideoFormatException(ClipMindException):
    pass

class SearchException(ClipMindException):
    pass

class CompilationException(ClipMindException):
    pass
