# Establish the common EvolutionOperations instance, called evolver.

from django.conf import settings

module_name = '.'.join(['django_evolution.db',str(settings.DATABASES['default']['ENGINE']).rpartition('.')[2]])
module = __import__(module_name,{},{},[''])

evolver = module.EvolutionOperations()

