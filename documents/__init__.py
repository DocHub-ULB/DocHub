from django.db.models.signals import pre_delete, pre_save, post_save
import signals
from models import Document
# TODO : be sure that use *pre*_save is ok
pre_save.connect(signals.pre_document_save, sender=Document)
post_save.connect(signals.post_document_save, sender=Document)
