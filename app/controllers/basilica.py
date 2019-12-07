import basilica
from decouple import config

BASILICA = basilica.Connection(config('BASILICA_KEY'))
