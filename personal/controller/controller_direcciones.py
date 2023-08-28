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

from PyQt6 import QtWidgets, QtGui
from PyQt6.QtWidgets import QMessageBox

from personal.model.model import DBManager

from personal.view.view_direcciones_postales import \
     Ui_Dialog_Direcciones_Postales
from personal.view.view import ICO_APLICACION

class Dialog_DireccionesPostales(QtWidgets.QDialog):
    
    def __init__(self, id_ = None, persona_id = None, direccion = None,
                 cp_id = None, preferencia = None, observ = None):
        """Inicializa el diálogo de configuración de direcciones"""
        
        super(Dialog_DireccionesPostales, self).__init__()
        self.ui = Ui_Dialog_Direcciones_Postales()
        self.ui.setupUi(self)

        self.setWindowIcon(QtGui.QIcon(ICO_APLICACION))
        
        self.ret = {'operacion' : None,
                    'id_': id_,
                    'persona_id' : persona_id,
                    'direccion': direccion,
                    'cp_id' : cp_id,
                    'preferencia' : preferencia,
                    'observ' : observ}
        
        if id_ is None:
            self.ui.pushButton_aceptar.setText("Crear")
            self.ui.pushButton_borrar.setEnabled(False)
        else:
            self.ui.pushButton_aceptar.setText("Modificar")
            self.ui.pushButton_borrar.setEnabled(True)
            
            # Rellenamos datos en las cajas de texto.
            self.ui.lineEdit_direccion.setText(str(self.ret['direccion']))
            
            # Recuperamos datos del código postal.
            self.poblar_CP()
            
            if self.ret['preferencia'] == "X":
                self.ui.comboBox_preferencia.setCurrentText("Si")
            else:
                self.ui.comboBox_preferencia.setCurrentText("No")
            self.ui.textEdit_observ.setText(str(self.ret['observ']))
                        
        # Connects para la gestión de códigos postales.
        self.ui.lineEdit_cp.editingFinished.connect(self.OnCP)
        self.ui.lineEdit_cp.textChanged.connect(self.OnCambiarCP)
       
        # Connects de botones.
        self.ui.pushButton_aceptar.clicked.connect(lambda: self.OnTerminar("a"))
        self.ui.pushButton_borrar.clicked.connect(lambda: self.OnTerminar("b"))
        self.ui.pushButton_cancelar.clicked.connect(lambda: \
                                                    self.OnTerminar("c"))

    def OnCambiarCP(self, text):
        """Si se elimina el CP se limpian provincia y localidad"""
        
        if not text:
            self.ui.lineEdit_localidad.clear()
            self.ui.lineEdit_provincia.clear()

    def poblar_CP(self):
        """Puebla datos del código postal"""
        
        bd = DBManager()
        ret = bd.obtener_codigo_postal_por_id(int(self.ret['cp_id']))
        
        if ret[0]:
            
            cp = ret[1].cp
            localidad = ret[1].localidad
            provincia = ret[1].provincia
            
            self.ui.lineEdit_cp.setText(str(cp))
            self.ui.lineEdit_localidad.setText(str(localidad))
            self.ui.lineEdit_provincia.setText(str(provincia))
            
        else:
            
            msg = f"No se ha podido recuperar el CP, provincia y localidad"
    
            self.mostrar_mensaje(f"Error en Código Postal",
                                 mas_info=msg,
                                 detalle = str(ret[1]),
                                 icono="critico")
        
    def OnCP(self):
        """Gestión de códigos postales"""
        
        # Se intenta buscar el CP en la base de datos. Si existe se
        # recupera la localidad y la provincia.
        
        cp = self.ui.lineEdit_cp.text().strip()
        
        bd = DBManager()
        ret = bd.obtener_codigo_postal_por_cp(cp)
        
        if ret[0] and ret[1] is not None:
            
            # Actualizamos cajas de texto e identificador de cp.
            self.ui.lineEdit_cp.setText(str(ret[1].cp))
            self.ui.lineEdit_provincia.setText(str(ret[1].provincia))
            self.ui.lineEdit_localidad.setText(str(ret[1].localidad))
            self.ret['cp_id'] = str(ret[1].id_)
                            
        else:
            # No existe el CP.
            self.ret['cp_id'] = None
            self.ui.lineEdit_provincia.clear()
            self.ui.lineEdit_localidad.clear()
                            
    def mostrar_mensaje(self, texto, mas_info = None, detalle = None, \
                        icono = "pregunta", cancel = False):
        """Muestra un mensaje:
        
          - texto : Es el texto del mensaje a mostrar.
          - mas_info : Es una explicación del texto mostrado.
          - detalle : Es un detalle más específico del mensaje a mostrar.
        
          - icono: pregunta, informacion, peligro, critico.
        """
        
        msg = QMessageBox(text=texto,parent=self)
        msg.setWindowTitle("personal")
        
        if icono == "pregunta": msg.setIcon(QMessageBox.Icon.Question)
        if icono == "informacion": msg.setIcon(QMessageBox.Icon.Information)
        if icono == "peligro": msg.setIcon(QMessageBox.Icon.Warning)
        if icono == "critico": msg.setIcon(QMessageBox.Icon.Critical)
                                     
        if not cancel:
            boton = QMessageBox.StandardButton.Ok
        else:
            boton = \
                QMessageBox.StandardButton.Ok|QMessageBox.StandardButton.Cancel
                
        msg.setStandardButtons(boton)
        msg.setDefaultButton(QMessageBox.StandardButton.Ok)

        if mas_info is not None: msg.setInformativeText(mas_info)
        if detalle is not None: msg.setDetailedText(detalle)

        ret = msg.exec()

        if ret == QMessageBox.StandardButton.Cancel: ret = False
        else: ret = True
                        
        return ret
    
    def __gestionar_cp(self, cp_id, cp, localidad, provincia):
        """Alta / modificación de código postal"""
        
        bd = DBManager()
        
        if cp_id is None:
            # Código postal nuevo.
            r = bd.alta_codigo_postal(cp, localidad, provincia)
        else:
            # Se actualiza por defecto el código postal.
            r = bd.modificar_codigo_postal(int(cp_id), cp, localidad, provincia)
                        
            
        if r[0]:
            self.ret['cp_id'] = r[1]
            
            ret = True
            
        else:
            
            msg = f"El CP debe de tener 5 dígitos y no existir en el " + \
                "en el sistema previamente. La localidad y " + \
                "provincia no pueden estar vacios."
    
            self.mostrar_mensaje(f"Fallo al dar de alta CP {cp}",
                                 mas_info=msg,
                                 detalle = str(r[1]),
                                 icono="critico")                
            
            ret = False
                
        return ret
        
    def OnTerminar(self, operacion):
        """Devuelve True si todo ha ido correcto y False en caso contrario
        (modifica, borrar o cancelar la operación)
        
        operacion:
                  'a' -> Dar de alta o modificar.
                  'b' -> Borrar.
                  'c' -> Cancelar la operación.
        """
        
        seguir = True
        
        if operacion == "c":
            
            # Cancelar.
            
            self.ret['operacion'] = False
        
        else:
            
            bd = DBManager()
                    
            if operacion == "b":
                
                # Borrar.
                
                if self.mostrar_mensaje(texto = "¿Seguro que quieres borrarla?",
                                        cancel=True):
                    
                    r = bd.baja_direccion(self.ret['id_'])
                    aux = "borrar"
                
                else:
                    seguir = False
                    
            if operacion == "a":
                
                # Dar de alta o modificar.
                
                # Datos.
                
                cp_id = self.ret['cp_id']
                cp = self.ui.lineEdit_cp.text().strip()
                localidad = self.ui.lineEdit_localidad.text().strip()
                provincia = self.ui.lineEdit_provincia.text().strip()
                direccion = self.ui.lineEdit_direccion.text().strip()
                preferencia = 1 \
                    if self.ui.comboBox_preferencia.currentText() == "Si" else 0
                observ = self.ui.textEdit_observ.toPlainText().strip()
                
                # Es obligatorio que el CP sea correcto.
                if self.__gestionar_cp(cp_id, cp, localidad, provincia):
                
                    if self.ret['id_'] is None:
                    
                        # Alta.
                    
                        r = bd.alta_direccion(self.ret['persona_id'], direccion,
                                              self.ret['cp_id'], preferencia,
                                              observ)
                        aux = "crear"
                        
                    else:
                        
                        # Modificación.
                        
                        r = bd.modificar_direccion(self.ret['id_'], direccion,
                                                   self.ret['cp_id'],
                                                   preferencia, observ)   
                        aux = "modificar"
                
                else:
                    seguir = False
                    
            if seguir:
            
                if r[0]:
                    
                    if operacion == "a":
                        if preferencia == 1:
                            bd.modificar_preferencia_direccion(r[1],
                                                               self.ret['persona_id'])
                    
                    self.ret['operacion'] = True
                
                else:
            
                    msg = f"No se ha podido {aux} la dirección postal"
            
                    self.mostrar_mensaje(f"Error en {aux}",
                                         mas_info=msg,
                                         detalle = str(r[1]),
                                         icono="critico")
                    
                    seguir = False
                    self.ret['operacion'] = False
                    
        if seguir: self.accept()            