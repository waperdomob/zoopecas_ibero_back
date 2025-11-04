from marshmallow import Schema, fields, validate, validates, ValidationError

class CategoriaProductoSchema(Schema):
    categoria_id = fields.Int(dump_only=True)
    nombre_categoria = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    descripcion = fields.Str(allow_none=True)
    activa = fields.Bool(missing=True)

class ProductoSchema(Schema):
    producto_id = fields.Int(dump_only=True)
    categoria_id = fields.Int(allow_none=True)
    codigo_producto = fields.Str(allow_none=True, validate=validate.Length(max=50))
    nombre = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    descripcion = fields.Str(allow_none=True)
    laboratorio = fields.Str(allow_none=True, validate=validate.Length(max=100))
    unidad_medida = fields.Str(allow_none=True, validate=validate.Length(max=50))
    precio_compra = fields.Decimal(places=2, allow_none=True)
    precio_venta = fields.Decimal(places=2, required=True)
    stock_actual = fields.Int(missing=0)
    stock_minimo = fields.Int(missing=0)
    fecha_vencimiento = fields.Date(allow_none=True)
    activo = fields.Bool(missing=True)
    observaciones = fields.Str(allow_none=True)

class ProductoUpdateSchema(Schema):
    categoria_id = fields.Int(allow_none=True)
    codigo_producto = fields.Str(allow_none=True)
    nombre = fields.Str(validate=validate.Length(min=3, max=200))
    descripcion = fields.Str(allow_none=True)
    laboratorio = fields.Str(allow_none=True)
    unidad_medida = fields.Str(allow_none=True)
    precio_compra = fields.Decimal(places=2, allow_none=True)
    precio_venta = fields.Decimal(places=2)
    stock_minimo = fields.Int()
    fecha_vencimiento = fields.Date(allow_none=True)
    activo = fields.Bool()
    observaciones = fields.Str(allow_none=True)

class MovimientoInventarioSchema(Schema):
    movimiento_id = fields.Int(dump_only=True)
    producto_id = fields.Int(required=True)
    tipo_movimiento = fields.Str(required=True, validate=validate.OneOf(['Entrada', 'Salida', 'Ajuste']))
    cantidad = fields.Int(required=True, validate=validate.Range(min=1))
    precio_unitario = fields.Decimal(places=2, allow_none=True)
    motivo = fields.Str(allow_none=True, validate=validate.Length(max=255))
    documento_referencia = fields.Str(allow_none=True, validate=validate.Length(max=100))

