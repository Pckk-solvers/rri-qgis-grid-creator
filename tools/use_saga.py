from qgis.core import QgsApplication
from qgis import processing
for alg in QgsApplication.processingRegistry().algorithms():
    if alg.provider().id() == 'sagang':
        print(alg.id(), '->', alg.displayName())
