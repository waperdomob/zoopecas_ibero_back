from marshmallow import Schema, fields, validate, validates, ValidationError, post_load

class DetalleFacturaSchema(Schema):
    detalle_id = fields.Int(dump_only=True)
    producto_id = fields.Int(allow_none=True)
    consulta_id = fields.Int(allow_none=True)
    vacunacion_id = fields.Int(allow_none=True)
    tipo_item = fields.Str(required=True, validate=validate.OneOf([
        'Producto', 'Consulta', 'Vacuna', 'Servicio'
    ]))
    descripcion = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    cantidad = fields.Int(required=True, validate=validate.Range(min=1))
    precio_unitario = fields.Decimal(places=2, required=True)
    subtotal = fields.Decimal(places=2, dump_only=True)
    
    @post_load
    def calculate_subtotal(self, data, **kwargs):
        data['subtotal'] = data['cantidad'] * data['precio_unitario']
        return data

class FacturaSchema(Schema):
    factura_id = fields.Int(dump_only=True)
    cliente_id = fields.Int(required=True)
    numero_factura = fields.Str(dump_only=True)
    fecha_factura = fields.Date(required=True)
    metodo_pago = fields.Str(required=True, validate=validate.OneOf([
        'Efectivo', 'Tarjeta', 'Transferencia', 'Otro'
    ]))
    estado = fields.Str(missing='Pendiente', validate=validate.OneOf([
        'Pagada', 'Pendiente', 'Anulada'
    ]))
    observaciones = fields.Str(allow_none=True)
    detalles = fields.List(fields.Nested(DetalleFacturaSchema), required=True)
    
    subtotal = fields.Decimal(places=2, dump_only=True)
    impuestos = fields.Decimal(places=2, dump_only=True)
    total = fields.Decimal(places=2, dump_only=True)

class FacturaUpdateSchema(Schema):
    metodo_pago = fields.Str(validate=validate.OneOf([
        'Efectivo', 'Tarjeta', 'Transferencia', 'Otro'
    ]))
    estado = fields.Str(validate=validate.OneOf([
        'Pagada', 'Pendiente', 'Anulada'
    ]))
    observaciones = fields.Str(allow_none=True)