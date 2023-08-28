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

from personal.view.view_telefonos import Ui_Dialog_Telefonos
from personal.view.view import ICO_APLICACION

class Dialog_Telefonos(QtWidgets.QDialog):
    
    def __init__(self, id_ = None, persona_id = None, numero = None,
                 preferencia = None, observ = None):
        """Inicializa el diálogo de configuración de teléfonos"""
        
        super(Dialog_Telefonos, self).__init__()
        self.ui = Ui_Dialog_Telefonos()
        self.ui.setupUi(self)

        self.setWindowIcon(QtGui.QIcon(ICO_APLICACION))
        
        self.ret = {'operacion' : None,
                    'id_': id_,
                    'persona_id' : persona_id,
                    'tlfno': numero,
                    'preferencia' : preferencia,
                    'observ' : observ}
        
        if id_ is None:
            self.ui.pushButton_aceptar.setText("Crear")
            self.ui.pushButton_borrar.setEnabled(False)
        else:
            self.ui.pushButton_aceptar.setText("Modificar")
            self.ui.pushButton_borrar.setEnabled(True)
            
            # Rellenamos datos en las cajas de texto.
            self.ui.lineEdit_tlfno.setText(str(self.ret['tlfno']))
            if self.ret['preferencia'] == "X":
                self.ui.comboBox_preferencia.setCurrentText("Si")
            else:
                self.ui.comboBox_preferencia.setCurrentText("No")
            self.ui.textEdit_observ.setText(str(self.ret['observ']))
                        
        # Connects de botones.
        self.ui.pushButton_aceptar.clicked.connect(lambda: self.OnTerminar("a"))
        self.ui.pushButton_borrar.clicked.connect(lambda: self.OnTerminar("b"))
        self.ui.pushButton_cancelar.clicked.connect(lambda: \
                                                    self.OnTerminar("c"))

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
                
                if self.mostrar_mensaje(texto = "¿Seguro que quieres borrarlo?",
                                        cancel=True):
                    
                    r = bd.baja_telefono(self.ret['id_'])
                    aux = "borrar"
                
                else:
                    seguir = False
                    
            if operacion == "a":
                
                # Dar de alta o modificar.
                
                # Datos.
                
                tlfno = self.ui.lineEdit_tlfno.text().strip()
                preferencia = 1 \
                    if self.ui.comboBox_preferencia.currentText() == "Si" else 0
                observ = self.ui.textEdit_observ.toPlainText().strip()
                
                if self.ret['id_'] is None:
                
                    # Alta.
                
                    r = bd.alta_telefono(self.ret['persona_id'], tlfno,
                                         preferencia, observ)
                    aux = "crear"
                    
                else:
                    
                    # Modificación.
                    
                    r = bd.modificar_telefono(self.ret['id_'], tlfno,
                                              preferencia, observ)
                    aux = "modificar"
                    
            if seguir:
            
                if r[0]:
                    
                    if operacion == "a":
                        if preferencia == 1:
                            bd.modificar_preferencia_tlfno(r[1],
                                                           self.ret['persona_id'])
                    
                    self.ret['operacion'] = True
                
                else:
            
                    msg = f"No se ha podido {aux} el teléfono"
            
                    self.mostrar_mensaje(f"Error en {aux}",
                                         mas_info=msg,
                                         detalle = str(r[1]),
                                         icono="critico")
                    
                    seguir = False
                    self.ret['operacion'] = False
                    
        if seguir: self.accept()                    