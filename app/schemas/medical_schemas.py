from marshmallow import Schema, fields, validate

class HistoriaClinicaSchema(Schema):
    historia_id = fields.Int(dump_only=True)
    mascota_id = fields.Int(required=True)
    fecha_creacion = fields.Date(dump_only=True)
    peso_inicial = fields.Decimal(places=2, allow_none=True)
    
    # Reseña
    caracteristicas_especiales = fields.Str(allow_none=True)
    
    # Anamnesis
    queja_principal = fields.Str(allow_none=True)
    tratamientos_previos = fields.Str(allow_none=True)
    enfermedades_anteriores = fields.Str(allow_none=True)
    cirugias_anteriores = fields.Str(allow_none=True)
    tipo_dieta = fields.Str(allow_none=True, validate=validate.OneOf(
        ['Concentrado', 'Barf', 'Casera', 'Mixta', 'Otra']
    ))
    detalle_dieta = fields.Str(allow_none=True)
    medicina_preventiva = fields.Str(allow_none=True)
    
    activa = fields.Bool(missing=True)
    observaciones_generales = fields.Str(allow_none=True)

class ConsultaSchema(Schema):
    consulta_id = fields.Int(dump_only=True)
    historia_id = fields.Int(required=True)
    veterinario_id = fields.Int(required=True)
    fecha_consulta = fields.Date(required=True)
    hora_consulta = fields.Time(required=True)
    motivo_consulta = fields.Str(required=True)
    
    # Inspección
    inspeccion_general = fields.Str(allow_none=True)
    
    # Palpación, Percusión y Auscultación
    temperatura = fields.Decimal(places=2, allow_none=True)
    pulso = fields.Int(allow_none=True)
    respiracion = fields.Int(allow_none=True)
    tiempo_llenado_capilar = fields.Decimal(places=1, allow_none=True)
    hidratacion = fields.Str(allow_none=True)
    peso = fields.Decimal(places=2, allow_none=True)
    ganglios = fields.Str(allow_none=True)
    
    # Sistemas
    sistema_digestivo = fields.Str(allow_none=True)
    sistema_respiratorio = fields.Str(allow_none=True)
    sistema_cardiovascular = fields.Str(allow_none=True)
    sistema_urinario = fields.Str(allow_none=True)
    sistema_genital = fields.Str(allow_none=True)
    sistema_nervioso = fields.Str(allow_none=True)
    sistema_locomotor = fields.Str(allow_none=True)
    piel_anexos = fields.Str(allow_none=True)
    hallazgos = fields.Str(allow_none=True)
    
    # Exámenes
    examenes_solicitados = fields.Str(allow_none=True)
    examenes_autorizados = fields.Str(allow_none=True)
    
    # Diagnóstico y Tratamiento
    diagnostico = fields.Str(required=True)
    pronostico = fields.Str(allow_none=True, validate=validate.OneOf(
        ['Favorable', 'Desfavorable', 'Reservado']
    ))
    tratamiento_ideal = fields.Str(allow_none=True)
    tratamiento_instaurado = fields.Str(allow_none=True)
    cotizacion_tratamiento = fields.Decimal(places=2, allow_none=True)
    
    observaciones = fields.Str(allow_none=True)
    proxima_cita = fields.Date(allow_none=True)
    costo_consulta = fields.Decimal(places=2, missing=0.00)

class SeguimientoSchema(Schema):
    seguimiento_id = fields.Int(dump_only=True)
    consulta_id = fields.Int(required=True)
    fecha_seguimiento = fields.Date(required=True)
    hora_seguimiento = fields.Time(allow_none=True)
    observaciones = fields.Str(required=True)
    responsable = fields.Str(allow_none=True)

class VacunacionSchema(Schema):
    vacunacion_id = fields.Int(dump_only=True)
    mascota_id = fields.Int(required=True)
    veterinario_id = fields.Int(required=True)
    vacuna_id = fields.Int(required=True)
    fecha_aplicacion = fields.Date(required=True)
    fecha_vencimiento = fields.Date(allow_none=True)
    lote = fields.Str(allow_none=True)
    observaciones = fields.Str(allow_none=True)
    costo = fields.Decimal(places=2, allow_none=True)

class VeterinarioSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    apellidos = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    documento_identidad = fields.Str(allow_none=True)
    telefono = fields.Str(allow_none=True)
    email = fields.Email(allow_none=True)
    numero_tarjeta_profesional = fields.Str(required=True)
    especialidad = fields.Str(allow_none=True)
    fecha_ingreso = fields.Date(allow_none=True)
    activo = fields.Bool(missing=True)