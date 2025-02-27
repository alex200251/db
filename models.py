# coding: utf-8
from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Cliente(Base):
    __tablename__ = 'clientes'

    id_cliente = Column(Integer, primary_key=True, server_default=text("nextval('clientes_id_cliente_seq'::regclass)"))
    nombre = Column(String(100), nullable=False)
    correo = Column(String(150), nullable=False, unique=True)
    telefono = Column(String(20))
    fecha_registro = Column(DateTime, server_default=text("now()"))


class Empleado(Base):
    __tablename__ = 'empleados'
    __table_args__ = (
        CheckConstraint("(rol)::text = ANY (ARRAY[('Mesero'::character varying)::text, ('Coordinador'::character varying)::text, ('Chef'::character varying)::text, ('Músico'::character varying)::text])"),
    )

    id_empleado = Column(Integer, primary_key=True, server_default=text("nextval('empleados_id_empleado_seq'::regclass)"))
    nombre = Column(String(100), nullable=False)
    rol = Column(String(50))
    disponibilidad = Column(Boolean, server_default=text("true"))


class EstadosReservacion(Base):
    __tablename__ = 'estados_reservacion'

    estado = Column(String(20), primary_key=True)


class Evento(Base):
    __tablename__ = 'eventos'
    __table_args__ = (
        CheckConstraint("(tipo_evento)::text = ANY (ARRAY[('Boda'::character varying)::text, ('Conferencia'::character varying)::text, ('Reunión Corporativa'::character varying)::text, ('Cena Privada'::character varying)::text])"),
    )

    id_evento = Column(Integer, primary_key=True, server_default=text("nextval('eventos_id_evento_seq'::regclass)"))
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text)
    tipo_evento = Column(String(50))
    fecha_creacion = Column(DateTime, server_default=text("now()"))


class Salone(Base):
    __tablename__ = 'salones'

    id_salon = Column(Integer, primary_key=True, server_default=text("nextval('salones_id_salon_seq'::regclass)"))
    nombre = Column(String(100), nullable=False, unique=True)
    capacidad = Column(Integer, nullable=False)


class Servicio(Base):
    __tablename__ = 'servicios'

    id_servicio = Column(Integer, primary_key=True, server_default=text("nextval('servicios_id_servicio_seq'::regclass)"))
    nombre = Column(String(100), nullable=False)
    costo = Column(Numeric(10, 2), nullable=False)


class TipoCambio(Base):
    __tablename__ = 'tipo_cambio'
    __table_args__ = (
        CheckConstraint("(moneda_destino)::text = ANY (ARRAY[('USD'::character varying)::text, ('EUR'::character varying)::text, ('MXN'::character varying)::text])"),
        CheckConstraint("(moneda_origen)::text = ANY (ARRAY[('USD'::character varying)::text, ('EUR'::character varying)::text, ('MXN'::character varying)::text])")
    )

    id = Column(Integer, primary_key=True, server_default=text("nextval('tipo_cambio_id_seq'::regclass)"))
    moneda_origen = Column(String(10))
    moneda_destino = Column(String(10))
    tasa = Column(Numeric(10, 4), nullable=False)
    fecha_actualizacion = Column(DateTime, server_default=text("now()"))


class EventoEmpleado(Base):
    __tablename__ = 'evento_empleados'
    __table_args__ = (
        CheckConstraint('hora_fin > hora_inicio'),
    )

    id_evento = Column(ForeignKey('eventos.id_evento', ondelete='CASCADE'), primary_key=True, nullable=False)
    id_empleado = Column(ForeignKey('empleados.id_empleado', ondelete='CASCADE'), primary_key=True, nullable=False)
    hora_inicio = Column(DateTime, nullable=False)
    hora_fin = Column(DateTime, nullable=False)

    empleado = relationship('Empleado')
    evento = relationship('Evento')


class HistorialEvento(Base):
    __tablename__ = 'historial_eventos'

    id_historial = Column(Integer, primary_key=True, server_default=text("nextval('historial_eventos_id_historial_seq'::regclass)"))
    id_evento = Column(ForeignKey('eventos.id_evento', ondelete='CASCADE'))
    nombre_anterior = Column(String(150))
    descripcion_anterior = Column(Text)
    fecha_modificacion = Column(DateTime, server_default=text("now()"))

    evento = relationship('Evento')


class Reservacione(Base):
    __tablename__ = 'reservaciones'
    __table_args__ = (
        CheckConstraint('fecha_evento > fecha_solicitud'),
        Index('idx_reservacion_unica', 'id_salon', 'fecha_evento', unique=True)
    )

    id_reservacion = Column(Integer, primary_key=True, server_default=text("nextval('reservaciones_id_reservacion_seq'::regclass)"))
    id_cliente = Column(ForeignKey('clientes.id_cliente', ondelete='CASCADE'))
    id_evento = Column(ForeignKey('eventos.id_evento', ondelete='CASCADE'))
    id_salon = Column(ForeignKey('salones.id_salon', ondelete='CASCADE'))
    fecha_solicitud = Column(DateTime, server_default=text("now()"))
    fecha_evento = Column(DateTime, nullable=False)
    fecha_cancelacion = Column(DateTime)
    estado = Column(ForeignKey('estados_reservacion.estado'))

    estados_reservacion = relationship('EstadosReservacion')
    cliente = relationship('Cliente')
    evento = relationship('Evento')
    salone = relationship('Salone')


class Facturacion(Base):
    __tablename__ = 'facturacion'
    __table_args__ = (
        CheckConstraint("(moneda)::text = ANY (ARRAY[('MXN'::character varying)::text, ('USD'::character varying)::text, ('EUR'::character varying)::text])"),
    )

    id_factura = Column(Integer, primary_key=True, server_default=text("nextval('facturacion_id_factura_seq'::regclass)"))
    id_reservacion = Column(ForeignKey('reservaciones.id_reservacion', ondelete='CASCADE'))
    monto_total = Column(Numeric(12, 2), nullable=False)
    moneda = Column(String(10))
    fecha_pago = Column(DateTime, server_default=text("now()"))

    reservacione = relationship('Reservacione')


class ReservacionServicio(Base):
    __tablename__ = 'reservacion_servicios'
    __table_args__ = (
        CheckConstraint('cantidad > 0'),
    )

    id_reservacion = Column(ForeignKey('reservaciones.id_reservacion', ondelete='CASCADE'), primary_key=True, nullable=False)
    id_servicio = Column(ForeignKey('servicios.id_servicio', ondelete='CASCADE'), primary_key=True, nullable=False)
    cantidad = Column(Integer, nullable=False)

    reservacione = relationship('Reservacione')
    servicio = relationship('Servicio')
