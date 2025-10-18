from .base import BaseModel, TimestampMixin
from app.extensions import db
from app.models.user import User
#from app.models.inventory import MovimientoInventario
#from .client import Cliente
#from .pet import Mascota
#from .medical import (
#    Veterinario, 
#    HistoriaClinica, 
#    Consulta,
#    SeguimientoPaciente, 
#    TipoServicio, 
#    ServicioConsulta
#)
#from .vaccination import VacunaCatalogo, Vacunacion
#from .inventory import CategoriaProducto, Producto, MovimientoInventario
#from .appointment import Cita
#from .billing import Factura, DetalleFactura
#from .alert import AlertaSistema

__all__ = [
    'BaseModel', 'TimestampMixin',
    'User'
]