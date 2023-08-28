"""
personal, un sistema de gestión de personas

    Copyright (C) 2023 Ángel Luis García García

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os

from sqlalchemy import Column, Integer, Text, ForeignKey, \
     CheckConstraint, create_engine, BLOB, and_
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

NOMBRE_BD = "personal.db"
dir_actual = os.path.dirname(os.path.abspath(__file__))
RUTA_BD = os.path.join(*[dir_actual])
FICHERO_BD = f'sqlite:///{os.path.join(*[RUTA_BD, NOMBRE_BD])}'

# Se define el modelo que representa la estructura de tus tablas en la base de
# datos. Para ello se utiliza la funcionalidad de declarative_base de 
# SQLAlchemy. 

Base = declarative_base()

class Persona(Base):
    
    __tablename__ = 'persona'
    
    id_ = Column(Integer, primary_key=True, autoincrement=True)
    nif = Column(Text(collation='NOCASE'), unique=True, nullable=False)
    nombre = Column(Text(collation='NOCASE'), nullable=False)
    ap1 = Column(Text(collation='NOCASE'), nullable=False)
    ap2 = Column(Text(collation='NOCASE'))
    fnac = Column(Text, nullable=False)
    relacionado_con = Column(Integer, ForeignKey('persona.id_'), nullable=True)
    tipo_relacion_id = Column(Integer, ForeignKey('tipo_relacion.id_'),\
                              nullable=True)
    observ = Column(Text(collation='NOCASE'))
    foto = Column(BLOB)
    sexo = Column(Text, nullable=False)
    
    # Restricciones de columnas.
    
    __table_args__ = (CheckConstraint("length(nif) = 9", name="check_nif"), \
                      CheckConstraint("sexo in ('Hombre', 'Mujer')", \
                                      name="check_sexo"))
    
    # Relaciones.
    
    per_relaciones = relationship("Persona", remote_side=[id_], 
                                  back_populates="per_relacionado_con")
    per_relacionado_con = relationship("Persona", 
                                       remote_side=[relacionado_con], 
                                       back_populates="per_relaciones") 
    per_telefonos = relationship("Telefono", back_populates="tel_persona",
                                 cascade='all, delete-orphan')
    per_mails = relationship("Mail", back_populates="mails_persona",
                             cascade='all, delete-orphan')
    per_direcciones = relationship("Direccion", back_populates="dir_persona",
                                   cascade='all, delete-orphan')
    per_tipo_relacion = relationship("TipoRelacion", \
                                     back_populates="t_rel_persona")    
    
    # Representación del objeto.
    
    def __repr__(self):
        return f"Persona(id_={self.id_}, nombre='{self.nombre}', \
        ap1='{self.ap1}', ap2='{self.ap2}', nif='{self.nif}')"

class Telefono(Base):
    
    __tablename__ = 'telefono'
    
    id_ = Column(Integer, primary_key=True, autoincrement=True)
    persona_id = Column(Integer, ForeignKey('persona.id_'), nullable=False)
    numero = Column(Text(collation='NOCASE'), nullable=False)
    preferencia = Column(Integer, nullable=False)
    observ = Column(Text(collation='NOCASE'))
    
    # Restricciones de columnas.
    
    __table_args__ = (
           CheckConstraint("preferencia in (0,1)", \
                           name="check_preferencia"), )    

    # Relaciones

    tel_persona = relationship("Persona", back_populates="per_telefonos")

    # Representación del objeto.
    
    def __repr__(self):
        return f"Telefono(id_={self.id_}, numero='{self.numero}', \
        preferencia={self.preferencia})"

class Mail(Base):
    
    __tablename__ = 'mail'
    
    id_ = Column(Integer, primary_key=True, autoincrement=True)
    persona_id = Column(Integer, ForeignKey('persona.id_'), nullable=False)
    mail = Column(Text(collation='NOCASE'), nullable=False)
    preferencia = Column(Integer, nullable=False)
    observ = Column(Text(collation='NOCASE'))

    # Restricciones de columnas.
    
    __table_args__ = (
           CheckConstraint("preferencia in (0,1)", \
                           name="check_preferencia"), )
    
    # Relaciones
    
    mails_persona = relationship("Persona", back_populates="per_mails")

    # Representación del objeto.
    
    def __repr__(self):
        return f"Mail(id_={self.id_}, mail='{self.mail}', \
        preferencia={self.preferencia})"

class Direccion(Base):

    __tablename__ = 'direccion'

    id_ = Column(Integer, primary_key=True, autoincrement=True)
    persona_id = Column(Integer, ForeignKey('persona.id_'), nullable=False)
    direccion = Column(Text(collation='NOCASE'), nullable=False)
    cp_id = Column(Integer, ForeignKey('codigo_postal.id_'), nullable=False)
    preferencia = Column(Integer, nullable=False)
    observ = Column(Text(collation='NOCASE'))

    __table_args__ = (CheckConstraint("preferencia in (0,1)", \
                                      name="check_preferencia"), )
    
    # Relaciones
    
    dir_persona = relationship("Persona", back_populates="per_direcciones")
    dir_cp = relationship("CodigoPostal", back_populates="cp_direcciones")

    # Representación del objeto.

    def __repr__(self):
        return f"Direccion(id_={self.id_}, direccion='{self.direccion}', \
        preferencia={self.preferencia})"

class CodigoPostal(Base):
    
    __tablename__ = 'codigo_postal'
    
    id_ = Column(Integer, primary_key=True, autoincrement=True)
    cp = Column(Text, unique=True, nullable=False)
    localidad = Column(Text(collation='NOCASE'), nullable=False)
    provincia = Column(Text(collation='NOCASE'), nullable=False)

    # Restricciones de columnas.
    
    __table_args__ = (
        CheckConstraint("length(cp) = 5", name="check_cp"),
    )
    
    # Relaciones
    
    cp_direcciones = relationship("Direccion", back_populates="dir_cp")
    
    # Representación del objeto.

    def __repr__(self):
        return f"CodigoPostal(id_={self.id_}, cp='{self.cp}', \
        localidad='{self.localidad}', provincia='{self.provincia}')"


class TipoRelacion(Base):
    
    __tablename__ = 'tipo_relacion'
    
    id_ = Column(Integer, primary_key=True, autoincrement=True)
    relacion = Column(Text(collation='NOCASE'), unique=True, nullable=False)

    # Relaciones
    
    t_rel_persona = relationship("Persona", back_populates="per_tipo_relacion")
    
    # Representación del objeto.

    def __repr__(self):
        return f"TipoRelacion(id_={self.id_}, relacion='{self.relacion}')"

# Se crea una clase dedicada a la gestión de la base de datos, como un gestor 
# de conexiones. Esto te permitirá encapsular la configuración de la base de 
# datos y la creación de la sesión en una sola clase y utilizarla fácilmente 
# en el resto del aplicativo.

class DBManager:

    def __init__(self, db_uri = FICHERO_BD):
        self.engine = create_engine(db_uri, echo=True)
        self.sesion = sessionmaker(bind=self.engine)

    def obtener_sesion(self):
        return self.sesion()

    # ################
    # TIPO DE RELACIÓN
    # ################

    def alta_tipo_relacion(self, relacion):
        
        try:
            
            sesion = self.obtener_sesion()
            nuevo_tipo_relacion = TipoRelacion(relacion=relacion)
            sesion.add(nuevo_tipo_relacion)
            sesion.commit()
            id_ = nuevo_tipo_relacion.id_
            sesion.close()
            
            ret = True, id_
            
        except SQLAlchemyError as e:
            
            ret = False, e
            
        return ret
    
    def baja_tipo_relacion(self, id_):
        
        try:
            
            sesion = self.obtener_sesion()
            tipo_relacion = sesion.query(TipoRelacion).filter_by(id_=id_).first()
            sesion.delete(tipo_relacion)
            sesion.commit()
            sesion.close()
            
            ret = True, None
            
        except SQLAlchemyError as e:
            
            ret = False, e
            
        return ret
    
    def modificar_tipo_relacion(self, id_, nueva_relacion):
        
        try:
        
            sesion = self.obtener_sesion()
            tipo_relacion = sesion.query(TipoRelacion).filter_by(id_=id_).first()
            tipo_relacion.relacion = nueva_relacion
            sesion.commit()
            sesion.close()
            
            ret = True, id_
            
        except SQLAlchemyError as e:
            
            ret = False, e
            
        return ret    

    def obtener_todos_tipos_relacion(self):
        """Devuelve todos los tipos de relación de la base de datos"""
        
        try:
        
            sesion = self.obtener_sesion()
            tipos_relacion = sesion.query(TipoRelacion).all()
            sesion.close()
    
            ret = True, tipos_relacion
            
        except SQLAlchemyError as e:
            
            ret = False, e
            
        return ret

    # ########
    # TELÉFONO
    # ########
    
    def alta_telefono(self, persona_id, numero, preferencia, observ=None):
        
        try:
        
            sesion = self.obtener_sesion()
            nuevo_telefono = Telefono(persona_id=persona_id, numero=numero,
                                      preferencia=preferencia, observ=observ)
            sesion.add(nuevo_telefono)
            sesion.commit()
            id_ = nuevo_telefono.id_
            sesion.close()
            
            ret = True, id_
            
        except SQLAlchemyError as e:
           
            ret = False, e

        return ret

    def baja_telefono(self, telefono_id):
        
        try:
            
            sesion = self.obtener_sesion()
            telefono = sesion.query(Telefono).filter_by(id_=telefono_id).first()
            sesion.delete(telefono)
            sesion.commit()
            sesion.close()
            
            ret = True, None
            
        except SQLAlchemyError as e:
            
            ret = False, e

        return ret

    def modificar_telefono(self, telefono_id, nuevo_numero, nueva_preferencia,
                           nueva_observ=None):
        
        try:
            
            sesion = self.obtener_sesion()
            telefono = sesion.query(Telefono).filter_by(id_=telefono_id).first()
            telefono.numero = nuevo_numero
            telefono.preferencia = nueva_preferencia
            telefono.observ = nueva_observ
            sesion.commit()
            sesion.close()
            
            ret = True, telefono_id
            
        except SQLAlchemyError as e:
            
            ret = False, e

        return ret

    def modificar_preferencia_tlfno(self, tlfno_id, persona_id):

        try:
            
            # Se quita la preferencia a todos los teléfonos de la persona, 
            # excepto del mail pasado como parámetro.
            
            sesion = self.obtener_sesion()
            valor_nuevo = {'preferencia': 0}
            condicion = and_(Telefono.persona_id==persona_id,
                             Telefono.id_ != tlfno_id)
            
            sesion.query(Telefono).filter(condicion).update(valor_nuevo)
            sesion.commit()
            sesion.close()

            ret = True, None

        except SQLAlchemyError as e:

            ret = False, e

        return ret

    def obtener_telefonos_por_persona_id(self, persona_id):
        
        try:

            sesion = self.obtener_sesion()
            telefonos = sesion.query(Telefono).\
                filter_by(persona_id=persona_id).all()
            sesion.close()

            ret = True, telefonos
        
        except SQLAlchemyError as e:
            
            ret = False, e

        return ret
    
    # ####
    # MAIL
    # ####

    def alta_mail(self, persona_id, mail, preferencia, observ=None):
        
        try:
            sesion = self.obtener_sesion()
            nuevo_mail = Mail(persona_id=persona_id, mail=mail,
                              preferencia=preferencia, observ=observ)
            sesion.add(nuevo_mail)
            sesion.commit()
            id_ = nuevo_mail.id_
            sesion.close()
            
            ret = True, id_
            
        except SQLAlchemyError as e:
            
            ret = False, e

        return ret

    def baja_mail(self, mail_id):
        
        try:
            sesion = self.obtener_sesion()
            mail = sesion.query(Mail).filter_by(id_=mail_id).first()
            sesion.delete(mail)
            sesion.commit()

            sesion.close()
        
            ret = True, None
            
        except SQLAlchemyError as e:
            
            ret = False, e
            
        return ret

    def modificar_mail(self, mail_id, nuevo_mail, nueva_preferencia,
                       nueva_observ=None):
        
        try:
            
            sesion = self.obtener_sesion()
            mail = sesion.query(Mail).filter_by(id_=mail_id).first()
            mail.mail = nuevo_mail
            mail.preferencia = nueva_preferencia
            mail.observ = nueva_observ
            sesion.commit()

            sesion.close()
            
            ret = True, mail_id
            
        except SQLAlchemyError as e:
            
            ret = False, e

        return ret

    def modificar_preferencia_mail(self, mail_id, persona_id):

        try:
            
            # Se quita la preferencia a todos los mails de la persona, excepto
            # del mail pasado como parámetro.
            
            sesion = self.obtener_sesion()
            
            valor_nuevo = {'preferencia': 0}
            condicion = and_(Mail.persona_id==persona_id, Mail.id_ != mail_id)
            
            sesion.query(Mail).filter(condicion).update(valor_nuevo)
            sesion.commit()
            sesion.close()

            ret = True, None

        except SQLAlchemyError as e:

            ret = False, e

        return ret

    def obtener_mails_por_persona_id(self, persona_id):
        try:
            sesion = self.obtener_sesion()

            # Obtiene todos los registros de mails asociados a una persona por su ID
            mails = sesion.query(Mail).filter_by(persona_id=persona_id).all()

            sesion.close()

            ret = True, mails
    
        except SQLAlchemyError as e:
            
            ret = False, e

        return ret
    
    # #########
    # DIRECCION
    # #########
    
    def alta_direccion(self, persona_id, direccion, cp_id, preferencia,
                       observ=None):
        
        try:
            
            sesion = self.obtener_sesion()
            nueva_direccion = Direccion(persona_id=persona_id,
                                        direccion=direccion,
                                        cp_id=cp_id, preferencia=preferencia,
                                        observ=observ)
            sesion.add(nueva_direccion)
            sesion.commit()
            id_ = nueva_direccion.id_
            sesion.close()
            
            ret = True, id_
            
        except SQLAlchemyError as e:
            
            ret = False, e
            
        return ret

    def baja_direccion(self, direccion_id):
        
        try:
            sesion = self.obtener_sesion()
            direccion = sesion.query(Direccion).filter_by(id_=direccion_id).first()
            sesion.delete(direccion)
            sesion.commit()
            sesion.close()
            
            ret = True, None
            
        except SQLAlchemyError as e:
            
            ret = False, e
            
        return ret

    def modificar_direccion(self, id_, nueva_direccion, nuevo_cp_id,
                            nueva_preferencia, nueva_observ=None):

        try:

            sesion = self.obtener_sesion()
            direccion = sesion.query(Direccion).filter_by(id_=id_).first()
            direccion.direccion = nueva_direccion
            direccion.cp_id = nuevo_cp_id
            direccion.preferencia = nueva_preferencia
            direccion.observ = nueva_observ
            sesion.commit()
            sesion.close()
            
            ret = True, id_
        
        except SQLAlchemyError as e:
          
            ret = False, e
            
        return ret

    def obtener_direcciones_por_persona_id(self, persona_id):
        
        try:
            
            sesion = self.obtener_sesion()
            direcciones = sesion.query(Direccion).\
                filter_by(persona_id=persona_id).all()
            # sesion.close()

            ret = True, direcciones, sesion
            
        except SQLAlchemyError as e:

            ret = False, e

        return ret
    
    def modificar_preferencia_direccion(self, direccion_id, persona_id):

        try:
            
            # Se quita la preferencia a todas las direcciones de la persona, 
            # excepto de la dirección pasada como parámetro.
            
            sesion = self.obtener_sesion()
            
            valor_nuevo = {'preferencia': 0}
            condicion = and_(Direccion.persona_id==persona_id, \
                             Direccion.id_ != direccion_id)
            
            sesion.query(Direccion).filter(condicion).update(valor_nuevo)
            sesion.commit()
            sesion.close()

            ret = True, None

        except SQLAlchemyError as e:

            ret = False, e

        return ret
    
    # #############
    # CÓDIGO POSTAL
    # #############
    
    def alta_codigo_postal(self, cp, localidad, provincia):
        
        try:
            
            nuevo_cp = CodigoPostal(cp=cp, localidad=localidad,
                                    provincia=provincia)
            sesion = self.obtener_sesion()
            sesion.add(nuevo_cp)
            sesion.commit()
            id_ = nuevo_cp.id_
            sesion.close()
            
            ret = True, id_
            
        except SQLAlchemyError as e:
            
            ret = False, e
            
        return ret

    def modificar_codigo_postal(self, cp_id, nuevo_cp, nueva_localidad,
                                nueva_provincia):
        
        try:
            
            sesion = self.obtener_sesion()
            cp = sesion.query(CodigoPostal).filter_by(id_=cp_id).first()
            cp.cp = nuevo_cp
            cp.localidad = nueva_localidad
            cp.provincia = nueva_provincia
            sesion.commit()
            sesion.close()
            
            ret = True, cp_id
            
        except SQLAlchemyError as e:
            
            ret = False, e
            
        return ret

    def obtener_codigo_postal_por_id(self, cp_id):
        
        try:
            
            sesion = self.obtener_sesion()
            cp = sesion.query(CodigoPostal).filter_by(id_=cp_id).first()
            sesion.close()

            ret = True, cp
            
        except SQLAlchemyError as e:
            
            ret = False, e

        return ret
    
    def obtener_codigo_postal_por_cp(self, cp):

        try:
            
            sesion = self.obtener_sesion()
            cp = sesion.query(CodigoPostal).filter_by(cp=cp).first()
            sesion.close()

            ret = True, cp

        except SQLAlchemyError as e:

            ret = False, e

        return ret
    
   # #######
   # PERSONA
   # #######
   
    def alta_persona(self, nif, nombre, ap1, ap2, fnac, foto=None, sexo=None):
        """Da de alta una persona en la base de datos. Devuelve (True, id_)
        si no hay errores, y (False, <descripción del error>) en caso contrario.
        """

        try:
 
            nueva_persona = Persona(nif=nif, nombre=nombre, ap1=ap1, ap2=ap2,\
                                    fnac=fnac, foto=foto, sexo=sexo)
            sesion = self.obtener_sesion()
            sesion.add(nueva_persona)
            sesion.commit()
            id_ = nueva_persona.id_ 
            sesion.close()
            
            ret = True, id_
 
        except SQLAlchemyError as e:
            
            ret = False,  f"Error al dar de alta la persona: {e}"

        return ret

    def baja_persona(self, persona_id):
        """Elimina la persona con identificador persona_id"""
        
        try:
            
            sesion = self.obtener_sesion()
            persona = sesion.query(Persona).filter_by(id_=persona_id).first()
            sesion.delete(persona)
            sesion.commit()
            sesion.close()
            
            ret = True, None
        
        except SQLAlchemyError as e:
            
            ret = False, e

        return ret

    def modificar_persona(self, persona_id, nuevo_nif, nuevo_nombre, nuevo_ap1,
                          nuevo_ap2, nueva_fnac, nueva_foto=None, 
                          nuevo_sexo=None, nueva_observ = None,
                          tipo_relacion_id = None, relacionado_con_id = None):
 
        try:
 
            sesion = self.obtener_sesion()
            persona = sesion.query(Persona).filter_by(id_=persona_id).first()
            persona.nif = nuevo_nif
            persona.nombre = nuevo_nombre
            persona.ap1 = nuevo_ap1
            persona.ap2 = nuevo_ap2
            persona.fnac = nueva_fnac
            persona.relacionado_con = relacionado_con_id
            persona.tipo_relacion_id = tipo_relacion_id
            persona.observ = nueva_observ
            persona.foto = nueva_foto
            persona.sexo = nuevo_sexo
            sesion.commit()
            id_ = persona.id_
            sesion.close()
            
            ret = True, id_
        
        except SQLAlchemyError as e:
            
            ret = False, e

        return ret

    def obtener_todas_personas(self):
        """Devuelve todas las personas del sistema, en la tupla (True, personas)
        si no hay problemas, y (False, error) si ha habido un error.
        """

        try:

            sesion = self.obtener_sesion()
            personas = sesion.query(Persona).all()
            sesion.close()

            ret = True, personas
            
        except SQLAlchemyError as e:
            
            ret = False, e

        return ret

    def obtener_persona_por_id(self, persona_id):
        
        try:
            sesion = self.obtener_sesion()
            persona = sesion.query(Persona).filter_by(id_=persona_id).first()
            sesion.close()

            ret = True, persona
            
        except SQLAlchemyError as e:
            
            ret = False, e
            
        return ret
            
