from __future__ import unicode_literals

try:
	from local import *
except ImportError:
	try:
		from dev import *
	except ImportError:
		pass

try:
	DEBUG
	TEMPLATE_DEBUG
	DATABASES['default']
	CELERY_BROKER
except NameError:
	raise NameError('Required config values not found. Abort !')