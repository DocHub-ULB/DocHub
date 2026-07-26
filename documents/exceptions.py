class MissingBinary(EnvironmentError):
    def __repr__(self):
        message = self.args[0] if self.args else ""
        return f"MissingBinary: {message}"

    __str__ = __repr__


class DocumentProcessingError(Exception):
    def __init__(self, document, exc=None, message=None):
        super().__init__()
        self.document = document
        self.exc = exc
        self.message = message

    def __repr__(self):
        if not self.message:
            return f"DocumentProcessingError on document {self.document.id}"
        else:
            return f"DocumentProcessingError('{self.message}'') on document {self.document.id}"

    __str__ = __repr__


class UploadError(DocumentProcessingError):
    def __repr__(self):
        return f"UploadError('Document {self.document.id} was not properly uploaded by django.')"


class DownloadError(DocumentProcessingError):
    def __repr__(self):
        return f"UploadError('Downloading doc {self.document.id} from {self.document.original} failed')"


class SkipException(Exception):
    pass


class ExisingChecksum(SkipException):
    pass
