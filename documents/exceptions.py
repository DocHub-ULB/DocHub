class MissingBinary(EnvironmentError):
    pass


class DocumentProcessingError(Exception):

    def __init__(self, document, exc=None, message=None):
        super(UploadError, self).__init__()
        self.document = document
        self.exc = exc
        self.message = message

    def __repr__(self):
        if not self.message:
            return "DocumentProcessingError on document {0.id}".format(self.document)
        else:
            return "DocumentProcessingError('{0}'') on document {1.id}".format(self.message, self.document)

    __str__ = __repr__


class UploadError(DocumentProcessingError):

    def __repr__(self):
        return "UploadError('Document {0.id} was not properly uploaded by django.')".format(self.document)


class DownloadError(DocumentProcessingError):

    def __repr__(self):
        return "UploadError('Downloading doc {0.id} from {0.source} failed')".format(self.document)
