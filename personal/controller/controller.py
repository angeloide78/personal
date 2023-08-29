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

from datetime import datetime
from io import BytesIO
from PIL import Image

from PyQt6 import QtWidgets, QtGui
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QLabel
from PyQt6.QtCore import Qt, QSize, QDate, QBuffer, QByteArray, QIODeviceBase

from personal.view.view_personal import Ui_MainWindow
from personal.view.view import ICO_ALTA, ICO_BAJA, ICO_GUARDAR, ICO_CANCELAR, \
     ICO_IMPRIMIR, ICO_APLICACION, ICO_ADD, ICO_SGTE, ICO_ANT, ICO_ACERCADE, \
     ICO_INFO

from personal.model.model import DBManager

from personal.controller.controller_direcciones import \
     Dialog_DireccionesPostales
from personal.controller.controller_mails import Dialog_Correos
from personal.controller.controller_telefonos import Dialog_Telefonos
from personal.controller.controller_informes import CrearInforme
from personal.controller.controller_acercade import Dialog_Acercade

class VentanaPrincipal(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        """Inicializa la ventana principal de la aplicación"""
        
        super(VentanaPrincipal, self).__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Cargamos imágenes de la aplicación. En Windows no funciona bien si
        # se define en Qt Designer, por un problema con la ruta relativa.

        self.setWindowIcon(QtGui.QIcon(ICO_APLICACION))
        
        for i in ((self.ui.pushButton_alta_per, ICO_ALTA),
                  (self.ui.pushButton_baja_per, ICO_BAJA),
                  (self.ui.pushButton_cancelar_per, ICO_CANCELAR),
                  (self.ui.pushButton_guardar_per, ICO_GUARDAR),
                  (self.ui.pushButton_imp_per, ICO_IMPRIMIR),
                  (self.ui.pushButton_borrar_relacion, ICO_CANCELAR),
                  (self.ui.pushButton_limpiar_tipo_rel, ICO_CANCELAR),
                  (self.ui.pushButton_borrar_foto, ICO_CANCELAR),
                  (self.ui.pushButton_cargar_foto, ICO_ADD),
                  (self.ui.pushButton_crear_contacto, ICO_ADD),
                  (self.ui.pushButton_siguiente, ICO_SGTE),
                  (self.ui.pushButton_anterior, ICO_ANT),
                  (self.ui.pushButton_crear_tipo_rel, ICO_ADD),
                  (self.ui.pushButton_borrar_tipo_rel, ICO_CANCELAR),
                  (self.ui.pushButton_acerca_de, ICO_INFO)):
        
            i[0].setIcon(QIcon(QPixmap(i[1])))
        
        # No se muestran las cajas con los identificadores de relaciones.
        self.ui.lineEdit_tipo_relacion_id.setVisible(False)
        self.ui.lineEdit_relacionado_con_id.setVisible(False)
        
        # Ocultamos NRP
        self.ui.lineEdit_nrp_per.setVisible(False)
        
        # Estado del registro en edición.
        # Tipos de estado:
        #   en_edicion
        #   alta
        #   relacion
        
        self.__estado = "en_edicion"
        
        # Estado de edición de las celdas de tipo de relación.
        
        self.__modif_celda_tipo_rel = True
        
        # Ruta de la foto.
        
        self.__foto = None
        
        # Por defecto, solo está activada la búsqueda y los botones de
        # operaciones.
        
        # Se desactiva lo demás
        for i in ["contacto", "otros",  "personal"]:
            self.activar_elementos(i, False)
            
        # Se recuperan por defecto todas las personas.
        self.poblar_personas()
        
        # Se cargan los tipos de relaciones entre personas.
        self.poblar_tipo_relaciones()
       
        # Se configuran las tablas de contacto.
        self.conf_contacto("direccion_postal")
        self.conf_contacto("mail")
        self.conf_contacto("tlfno")
        
        # Connect de Acerca de
        self.ui.pushButton_acerca_de.clicked.connect(self.acerca_de)
       
        # Connects de botones de operaciones.
        self.ui.pushButton_alta_per.clicked.connect(self.OnAltaPersona)
        self.ui.pushButton_cancelar_per.clicked.connect(self.OnCancelarPersona)
        self.ui.pushButton_guardar_per.clicked.connect(self.OnGuardarPersona)
        self.ui.pushButton_baja_per.clicked.connect(self.OnBorrarPersona)
        self.ui.pushButton_imp_per.clicked.connect(self.OnImpPersona)
        self.ui.pushButton_cargar_foto.clicked.connect(self.OnFoto)
        self.ui.pushButton_borrar_foto.clicked.connect(self.OnBorrarFoto)
        
        # Connects de búsqueda de personal.
        self.ui.tableWidget_per.clicked.connect(self.OnClickPersona)
        self.ui.lineEdit_buscar_per.textChanged.connect(self.OnBuscar)
        
        # Connects de edición de contactos.
        self.ui.tableWidget_direccion_per.doubleClicked.\
            connect(lambda: self.OnConfiguracion("editar"))
        self.ui.tableWidget_mail_per.doubleClicked.\
            connect(lambda: self.OnConfiguracion("editar"))
        self.ui.tableWidget_tlfno_per.doubleClicked.\
            connect(lambda: self.OnConfiguracion("editar"))
      
        # Connects de creación de contactos.
        self.ui.pushButton_crear_contacto.clicked.connect(self.OnConfiguracion)
        
        # Connects de botones siguiente y anterior para tipos de relaciones.
        self.ui.pushButton_siguiente.clicked.connect(self.OnSgteTiposRelacion)
        self.ui.pushButton_anterior.clicked.connect(self.OnAntTiposRelacion)
        
        # Connects de gestión de tipos tipos de relaciones.
        self.ui.pushButton_crear_tipo_rel.clicked.connect(self.OnCrearTipoRel)
        self.ui.pushButton_borrar_tipo_rel.clicked.connect(self.OnBorrarTipoRel)
        self.ui.tableWidget_tipo_rel.cellChanged.connect(self.OnSalvarTipoRel)
        self.ui.pushButton_limpiar_tipo_rel.clicked.connect(self.OnLimpiarTipoRel)
        self.ui.pushButton_borrar_relacion.clicked.connect(self.OnBorrarRel)
        self.ui.pushButton_rel_per.clicked.connect(self.OnCrearRelacion)
        
    def acerca_de(self):
        """Muestra un diálogo sobre la autoría de la aplicación"""
        
        dialog = Dialog_Acercade(ICO_ACERCADE)
        dialog.exec()
        
    def OnCrearRelacion(self):
        """Crea la relación de una persona con la persona actual"""
        
        self.activar_elementos("relacion", False)
        self.__estado = "relacion"
        
    def OnBorrarRel(self):
        """Elimina la relación de una persona con la persona actual"""
        
        self.ui.lineEdit_relacionado_con_id.setText("")
        self.ui.lineEdit_rel_per.clear()
        
    def OnLimpiarTipoRel(self):
        """Elimina el tipo de relación de la persona"""
        
        self.ui.lineEdit_tipo_relacion_id.setText("")
        self.ui.comboBox_tipo_rel_per.setCurrentIndex(-1)
        # self.poblar_tipo_relaciones()
        
    def OnSalvarTipoRel(self, fila, columna):
        """Guarda el tipo de relación"""
        
        if self.__modif_celda_tipo_rel:
            id_ = self.ui.tableWidget_tipo_rel.item(fila, 0).text()
            tipo = self.ui.tableWidget_tipo_rel.\
                item(fila, 1).text().strip()
            
            bd = DBManager()
            
            if id_ == "":
                # Alta
                ret = bd.alta_tipo_relacion(tipo)
                
            else:
                # Modificación
                ret = bd.modificar_tipo_relacion(id_, tipo)
                
            if ret[0]:
                
                self.ui.pushButton_crear_tipo_rel.setEnabled(True)
                self.poblar_tipo_relaciones()
                self.posicionar_tipo_relacion()
                
            else:
                
                msg = "No se ha podido modificar el tipo de relación"
        
                self.mostrar_mensaje("Fallo al crear/modificar tipos de relación",
                                     mas_info=msg,
                                     detalle = str(ret[1]),
                                     icono="critico")                    
            
    def OnCrearTipoRel(self):
        """Crea un tipo de relación"""

        self.__modif_celda_tipo_rel = False
        
        self.ui.pushButton_crear_tipo_rel.setEnabled(False)
        self.__tipo_rel = False
        
        nfilas = self.ui.tableWidget_tipo_rel.rowCount()
        self.ui.tableWidget_tipo_rel.insertRow(nfilas)
        
        self.ui.tableWidget_tipo_rel.setItem(nfilas, 0, \
                                             QtWidgets.QTableWidgetItem(""))
        elemento = QtWidgets.QTableWidgetItem("")
        self.ui.tableWidget_tipo_rel.setItem(nfilas, 1, elemento)
        
        # Se establece el foco en la celda recién insertada
        self.ui.tableWidget_tipo_rel.setCurrentCell(nfilas, 0)        
        self.ui.tableWidget_tipo_rel.editItem(elemento)
        
        self.__modif_celda_tipo_rel = True
                
    def OnBorrarTipoRel(self):
        """Borra un tipo de relación"""
        
        if not self.ui.pushButton_crear_tipo_rel.isEnabled():
            # Se cancela la creación.
            self.ui.pushButton_crear_tipo_rel.setEnabled(True)
            self.poblar_tipo_relaciones()
            # self.posicionar_tipo_relacion()
            self.__tipo_rel = True
        
        else:
            # Se elimina la fila seleccionada.
            fila = self.ui.tableWidget_tipo_rel.currentRow()
            if fila >= 0:
                id_ = self.ui.tableWidget_tipo_rel.item(fila, 0).text()
                tipo = self.ui.tableWidget_tipo_rel.item(fila, 1).text().strip()
                if id_ == "":
                    pass
                else:
                    
                    msg = f"¿Borrar el tipo de relación {tipo}?" 
                    if self.mostrar_mensaje(texto = msg, cancel=True):
                   
                        bd = DBManager()
                        ret = bd.baja_tipo_relacion(int(id_))
                        
                        if ret[0]:
                            self.poblar_tipo_relaciones()
                            self.posicionar_tipo_relacion()
                        else:
                            msg = "No se ha podido borrar el tipo de relación"
                
                            self.mostrar_mensaje("Fallo al borrar el tipo de relación",
                                                 mas_info=msg,
                                                 detalle = str(ret[1]),
                                                 icono="critico")     
        
    def OnAntTiposRelacion(self):
        """Muestra el combo de selección de tipos de relación"""
        
        self.ui.stackedWidget_tipo_rel.setCurrentIndex(0)

    def OnSgteTiposRelacion(self):
        """Muestra la gestión de configuración de tipos de relación"""

        self.ui.stackedWidget_tipo_rel.setCurrentIndex(1)
    
    def posicionar_tipo_relacion(self):
        """Posiciona en el combo el tipo de relación de la persona actual"""
        
        tipo_relacion_id = self.ui.lineEdit_tipo_relacion_id.text()
        if tipo_relacion_id == "":
            self.ui.comboBox_tipo_rel_per.setCurrentIndex(-1)
            
        else:
            # Se posiciona el tipo de relación que se tenía anteriormente.
            i_aux = -1
            for i in range(self.ui.comboBox_tipo_rel_per.count()):
                if self.ui.\
                   comboBox_tipo_rel_per.itemData(i) == int(tipo_relacion_id):
                    i_aux = i
                    break
            if i_aux != -1:
                self.ui.comboBox_tipo_rel_per.setCurrentIndex(i_aux)
            else:
                # No se encuentra correspondencia dentro del combo, por lo que
                # se ha borrado.
                self.ui.lineEdit_tipo_relacion_id.setText("")
    
    def poblar_tipo_relaciones(self):
        """Puebla los tipos de relaciones en el combo/tabla de configuración"""
        
        self.__modif_celda_tipo_rel = False
        
        bd = DBManager()
    
        ret = bd.obtener_todos_tipos_relacion()
        
        if ret[0]:
            
            self.ui.comboBox_tipo_rel_per.clear()
            
            self.ui.tableWidget_tipo_rel.setRowCount(0)
            self.ui.tableWidget_tipo_rel.setColumnHidden(0, True)
            self.ui.tableWidget_tipo_rel.setColumnWidth(1, 150)
            self.ui.tableWidget_tipo_rel.setRowCount(len(ret[1]))            
            
            fila = -1
            
            for i in ret[1]:
                
                id_ = i.id_
                tipo = i.relacion
                
                # Se puebla el Combo
                self.ui.comboBox_tipo_rel_per.insertItem(0, str(tipo), int(id_))
            
                # Se puebla el TableWidget
                fila += 1
                                
                self.ui\
                    .tableWidget_tipo_rel\
                    .setItem(fila, 0, QtWidgets.QTableWidgetItem(str(id_)))

                self.ui\
                    .tableWidget_tipo_rel\
                    .setItem(fila, 1, QtWidgets.QTableWidgetItem(str(tipo)))
      
        else:
            msg = "No se ha podido recuperar los tipos de relación de personas"
    
            self.mostrar_mensaje("Fallo al buscar tipos de relación",
                                 mas_info=msg,
                                 detalle = str(ret[1]),
                                 icono="critico")    
        
        self.__modif_celda_tipo_rel = True
                            
    def poblar_personas(self):
        """Puebla todas las personas dadas de alta en el sistema"""
       
        bd = DBManager()
    
        ret = bd.obtener_todas_personas()
        
        if ret[0]:
            # msg = f"Se han recuperado {len(ret[1])} personas correctamente." 
            # self.mostrar_mensaje(msg, caja_texto = False)
    
            # print(ret[1])
            
            self.ui.tableWidget_per.setRowCount(0)
       
            self.ui.tableWidget_per.setColumnHidden(0, True)
            self.ui.tableWidget_per.setColumnWidth(1, 235)
            self.ui.tableWidget_per.setColumnWidth(2, 64)
            self.ui.tableWidget_per.setRowCount(len(ret[1]))
            
            # Poblamos.
            fila = -1
            for persona in ret[1]:
                
                fila += 1
                                
                id_ = str(persona.id_)
                nombre = str(persona.nombre)
                ap1 = str(persona.ap1)
                ap2 = str(persona.ap2)
                foto = persona.foto
                
                self.ui\
                    .tableWidget_per\
                    .setItem(fila, 0, QtWidgets.QTableWidgetItem(id_))

                cadena = f"{nombre} {ap1} {ap2}".strip()
                self.ui\
                    .tableWidget_per\
                    .setItem(fila, 1, QtWidgets.QTableWidgetItem(cadena))
            
                if foto is not None:
                    
                    if len(foto) == 0: pass
                    else:     
                        foto = Image.open(BytesIO(foto))
                        foto_redim = foto.resize((64, 64), Image.LANCZOS)
                        pixmap = QPixmap.fromImage(foto_redim.toqimage())
                        pixmap.detach()
                        # item = self.ui.tableWidget_per.item(fila, 2)
                        # if item is not None: item.setIcon(pixmap)                
                        marco = QLabel()
                        marco.setScaledContents(True)
                        marco.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        marco.setFixedSize(QSize(64, 64))
                        marco.setPixmap(pixmap)
    
                        self.ui.tableWidget_per.setRowHeight(fila, 64)
                        self.ui.tableWidget_per.setCellWidget(fila, 2, marco)                
                    
                
        else:
            self.mostrar_mensaje(f"Fallo al recuperar todas las personas", \
                                             caja_texto = False)
    
            msg = "No se ha podido recuperar ningún registro de personal"
    
            self.mostrar_mensaje("Fallo al buscar personal",
                                             mas_info=msg,
                                             detalle = str(ret[1]),
                                             icono="critico")    
        
    def mostrar_mensaje(self, texto, mas_info = None, detalle = None, \
                        icono = "pregunta", ok = True, cancel = False, \
                        caja_texto = True):
        """Muestra un mensaje:
        
        caja_texto = True, entonces muestra una caja de texto y se
        configura así:        
          - texto : Es el texto del mensaje a mostrar.
          - mas_info : Es una explicación del texto mostrado.
          - detalle : Es un detalle más específico del mensaje a mostrar.
        
          - icono: pregunta, informacion, peligro, critico.
        
          - ok : True para que aparezca el botón con Aceptar. 
          - cancel: True para que aparezca el botón Cancelar.
          
        Si caja_texto = False, entonces se muestra el mensaje de "texto" en la
        barra de estado.
        """
        
        if caja_texto:
            msg = QMessageBox(text=texto,parent=self)
            msg.setWindowTitle("personal")
                    
            if icono == "pregunta": msg.setIcon(QMessageBox.Icon.Question)
            if icono == "informacion": msg.setIcon(QMessageBox.Icon.Information)
            if icono == "peligro": msg.setIcon(QMessageBox.Icon.Warning)
            if icono == "critico": msg.setIcon(QMessageBox.Icon.Critical)
                                         
            if ok and not cancel: boton = QMessageBox.StandardButton.Ok
            if ok and cancel: boton = QMessageBox.StandardButton.Ok\
               |QMessageBox.StandardButton.Cancel
            if not ok and not cancel: boton = None
            if not ok and cancel: boton = QMessageBox.StandardButton.Cancel
                    
            if boton is not None: msg.setStandardButtons(boton)
            if ok: msg.setDefaultButton(QMessageBox.StandardButton.Ok)
    
            if mas_info is not None: msg.setInformativeText(mas_info)
            if detalle is not None: msg.setDetailedText(detalle)
    
            ret = msg.exec()

            if ret == QMessageBox.StandardButton.Cancel: ret = False
            else: ret = True
                        
        else:
            self.ui.statusbar.showMessage(texto, 0)
            ret = True
            
        return ret
    
    def limpiar_datos(self, opcion):
        """Se limpian cajas de texto, a partir de opcion.
        
        - opcion == "personal". Se limpian todas la cajas de texto de datos
          personales.
        - opcion == "contacto". Se limpian todos los tables de datos de
          contacto.
        - opcion == "otros". Se limpian todos los datos restantes
          (observaciones y relación de otras personas).
        """
        
        if opcion == "personal":
            for i in [self.ui.lineEdit_dni_per, self.ui.lineEdit_nombre_per,
                      self.ui.lineEdit_1ap_per, self.ui.lineEdit_2ap_per,
                      self.ui.label_foto_per,  self.ui.dateEdit_fnac_per,
                      self.ui.lineEdit_nrp_per]:
                i.clear()
            
        if opcion == "contacto":
            self.ui.tableWidget_direccion_per.setRowCount(0)
            self.ui.tableWidget_mail_per.setRowCount(0)
            self.ui.tableWidget_tlfno_per.setRowCount(0)
            
        if opcion == "otros":
            for i in [self.ui.textEdit_observ_per, self.ui.lineEdit_rel_per]:
                i.clear()
            self.ui.lineEdit_relacionado_con_id.setText("")
            self.ui.lineEdit_tipo_relacion_id.setText("")
            self.ui.comboBox_tipo_rel_per.setCurrentIndex(-1)
        
    def activar_elementos(self, opcion, estado = True):
        """Se activan elementos, a partir de opcion y estado.
        
        - opcion == "personal". Se activa / desactiva el grupo de personal,
          según estado.
          personales.
        - opcion == "contacto". Se activa / desactiva el grupo de contacto,
          según estado.
        - opcion == "otros". Se activa / desactiva el grupo de otros,
          según estado.
        - opcion == "buscar". Se activa / desactiva el grupo de búsqueda de
          personas, según estado.
        - opcion =="alta". Se activan / desactivan el grupo de botones de
          eliminar usuario, crear usuario, y generar PDF.
        - opcion == "relacion" / "en_edicion". Se desactivan todos los
          botones de las operaciones, excepto cancelar.
         
        """

        if opcion in ["personal", "relacion", "en_edicion"]:
            self.ui.groupBox_personal.setEnabled(estado)
        if opcion in ["contacto", "relacion", "en_edicion"]:
            self.ui.groupBox_contacto.setEnabled(estado)
        if opcion in ["otros", "relacion", "en_edicion"]:
            self.ui.groupBox_otros.setEnabled(estado)
        if opcion == "buscar": self.ui.groupBox_buscar.setEnabled(estado)
        if opcion in ["alta", "relacion", "en_edicion"]:
            self.ui.pushButton_alta_per.setEnabled(estado)
            self.ui.pushButton_baja_per.setEnabled(estado)
            self.ui.pushButton_imp_per.setEnabled(estado)
        # if opcion in ["relacion"]:
        #    self.ui.pushButton_guardar_per.setEnabled(estado)
            
    def cargar_datos_personales(self, id_):
        """Carga datos de la persona con identificador id_ en las cajas"""
        
        bd = DBManager()
        
        ret = bd.obtener_persona_por_id(id_)
        
        if ret[0]:
            
            # Se activan todas las cajas de texto.
            for i in ["personal", "contacto", "otros"]:
                self.activar_elementos(i)
            
            # Se rellenan las cajas de datos personales.
            self.ui.lineEdit_nrp_per.setText(str(ret[1].id_))
            self.ui.lineEdit_dni_per.setText(ret[1].nif)
            self.ui.lineEdit_nombre_per.setText(str(ret[1].nombre))
            self.ui.lineEdit_1ap_per.setText(str(ret[1].ap1))
            self.ui.lineEdit_2ap_per.setText(str(ret[1].ap2))
            self.ui.comboBox_sexo_per.setCurrentText(ret[1].sexo)
            
            anyo = int(ret[1].fnac[0:4])
            mes = int(ret[1].fnac[5:7])
            dia = int(ret[1].fnac[8:10])
            self.ui.dateEdit_fnac_per.setDate(QDate(anyo, mes, dia))
            
            observ = "" if ret[1].observ is None else str(ret[1].observ)
            self.ui.textEdit_observ_per.setText(observ)
            
            # Relaciones.
            relacionado_con = "" if ret[1].relacionado_con is None else \
                str(ret[1].relacionado_con)
            self.ui.lineEdit_relacionado_con_id.setText(relacionado_con)
            tipo_relacion_id = "" if ret[1].tipo_relacion_id is None else \
                str(ret[1].tipo_relacion_id)
            self.ui.lineEdit_tipo_relacion_id.setText(tipo_relacion_id)
            
            # Foto
            if ret[1].foto is not None:
                
                try:
                    
                    foto = Image.open(BytesIO(ret[1].foto))
                    foto_redim = foto.resize((180, 180), Image.LANCZOS)
                    pixmap = QPixmap.fromImage(foto_redim.toqimage())
                    pixmap.detach()
                
                    self.ui.label_foto_per.setPixmap(pixmap)
                
                except: # Exception as e:
                
                    self.OnBorrarFoto()
                
                    # self.mostrar_mensaje("Error", \
                    #                      mas_info="Error al cargar la imagen",
                    #                      detalle=str(e),
                    #                      icono="critico")
            else:
                
                self.OnBorrarFoto()
                
    def cargar_persona(self, id_):
        """Carga como persona actual la asociada a su identificador id_"""
        
        if len(id_.strip()) != 0:
            # Datos personales.
            self.cargar_datos_personales(int(id_))
            # Correos electrónicos.
            self.poblar_mails()
            # Teléfonos.
            self.poblar_tlfnos()
            # Direcciones postales.
            self.poblar_direcciones()
            # Tipos de relacioón entre personas.
            self.posicionar_tipo_relacion()
            # Persona relacionada.
            self.persona_relacionada()
        
    def OnClickPersona(self):
        """Selecciona la persona y lleva sus datos a edición"""
        
        fila = self.ui.tableWidget_per.currentRow()
        if fila >= 0:

            id_ = self.ui.tableWidget_per.item(fila, 0).text()
            nombre = self.ui.tableWidget_per.item(fila, 1).text() 
            
            if self.__estado == "relacion":
            
                self.ui.lineEdit_relacionado_con_id.setText(id_)
                self.ui.lineEdit_rel_per.setText(nombre)
                self.ui.lineEdit_rel_per.setCursorPosition(0)
                
            else:
                
                self.cargar_persona(id_)
                self.__estado = "en_edicion"
                
    def persona_relacionada(self):
        """Visualiza la persona relacionada con la persona actual"""
        
        id_ = self.ui.lineEdit_relacionado_con_id.text()
        if id_ == "" or id_ == None:
            self.ui.lineEdit_rel_per.clear()
            self.ui.lineEdit_rel_per.setToolTip("")
        else:
            bd = DBManager()
            ret = bd.obtener_persona_por_id(int(id_))
            if ret[0]:
                msg = f"{ret[1].nombre} {ret[1].ap1} {ret[1].ap2}"
                self.ui.lineEdit_rel_per.setText(msg)
                self.ui.lineEdit_rel_per.setToolTip(f"DNI {ret[1].nif}")
                self.ui.lineEdit_rel_per.setCursorPosition(0)
            else:
                msg = "No encuentro la persona relacionada"
                self.mostrar_mensaje("Error", \
                                     mas_info=msg,
                                     detalle=str(ret[1]),
                                     icono="critico")
                                
    def OnConfiguracion(self, opcion = "alta"):
        """Abre ventana de configuración"""
        
        tab_actual = self.ui.tabWidget_contacto_per.currentIndex()
        
        if tab_actual == 0: self.__conf_direcciones_postales(opcion)
        if tab_actual == 1: self.__conf_mails(opcion)
        if tab_actual == 2: self.__conf_telefonos(opcion)
                
    def __conf_direcciones_postales(self, opcion):
        """Configuración de direcciones postales"""
 
        if opcion == "editar":
            
            fila = self.ui.tableWidget_direccion_per.currentRow()
            if fila >= 0:
                id_ = self.ui.tableWidget_direccion_per.item(fila, 0).text()
                persona_id = self.ui.tableWidget_direccion_per.\
                    item(fila, 1).text() 
                direccion = self.ui.tableWidget_direccion_per.item(fila, 2).\
                    text()
                cp_id = self.ui.tableWidget_direccion_per.item(fila, 3).text()
                preferencia = self.ui.tableWidget_direccion_per.item(fila, 7).\
                    text()                  
                observ = self.ui.tableWidget_direccion_per.item(fila, 8).text()                  
                
                dialog = Dialog_DireccionesPostales(id_, persona_id, direccion,
                                                    cp_id, preferencia, observ)
                
        else:
            persona_id = self.ui.lineEdit_nrp_per.text().strip()
            if len(persona_id) > 0:            
                dialog = Dialog_DireccionesPostales(persona_id = persona_id)
         
        dialog.exec()        
       
        if dialog.ret["operacion"]:
            # Recargar datos, ya que algo se ha modificado.
            self.poblar_direcciones()
            
        else:
            msg = "No se han hecho cambios en direcciones postales."
            self.mostrar_mensaje(msg, caja_texto = False)                    
        
    def conf_contacto(self, opcion):
        """Configura las columnas de las tablas de contacto"""
       
        if opcion == "direccion_postal":
            self.ui.tableWidget_direccion_per.setRowCount(0)
            self.ui.tableWidget_direccion_per.setColumnHidden(0, True)
            self.ui.tableWidget_direccion_per.setColumnHidden(1, True)
            self.ui.tableWidget_direccion_per.setColumnHidden(3, True)
            self.ui.tableWidget_direccion_per.setColumnWidth(2, 200) # Dir.
            self.ui.tableWidget_direccion_per.setColumnWidth(4, 50) # CP
            self.ui.tableWidget_direccion_per.setColumnWidth(5, 200) # Loc.
            self.ui.tableWidget_direccion_per.setColumnWidth(6, 200) # Prov.
            self.ui.tableWidget_direccion_per.setColumnWidth(7, 80) # Pref.
            self.ui.tableWidget_direccion_per.setColumnWidth(8, 200) # Obs.

        if opcion == "mail":
            self.ui.tableWidget_mail_per.setRowCount(0)
            self.ui.tableWidget_mail_per.setColumnHidden(0, True)
            self.ui.tableWidget_mail_per.setColumnHidden(1, True)
            self.ui.tableWidget_mail_per.setColumnWidth(2, 200) # Mail
            self.ui.tableWidget_mail_per.setColumnWidth(3, 100) # Prefer.
            self.ui.tableWidget_mail_per.setColumnWidth(4, 200) # Observ.
        
        if opcion == "tlfno":
            self.ui.tableWidget_tlfno_per.setRowCount(0)
        
            self.ui.tableWidget_tlfno_per.setColumnHidden(0, True)
            self.ui.tableWidget_tlfno_per.setColumnHidden(1, True)
            self.ui.tableWidget_tlfno_per.setColumnWidth(2, 200) # Teléfono
            self.ui.tableWidget_tlfno_per.setColumnWidth(3, 100) # Prefer.
            self.ui.tableWidget_tlfno_per.setColumnWidth(4, 200) # Observ.
            
    def poblar_direcciones(self):
        """Puebla las direcciones postales de la persona actual"""
        
        persona_id = self.ui.lineEdit_nrp_per.text().strip()
        if len(persona_id) == 0:
            pass
        
        else:
            
            persona_id = int(persona_id)
            bd = DBManager()
            
            ret = bd.obtener_direcciones_por_persona_id(persona_id)
            
            if ret[0]:
                
                self.conf_contacto("direccion_postal")                               
                self.ui.tableWidget_direccion_per.setRowCount(len(ret[1]))
                
                # Poblamos.
                fila = -1
                for direc in ret[1]:
                    
                    fila += 1
                                    
                    id_ = str(direc.id_)
                    persona_id = str(direc.persona_id)
                    direccion = str(direc.direccion)
                    cp_id = str(direc.cp_id)
                    localidad = str(direc.dir_cp.localidad)
                    provincia = str(direc.dir_cp.provincia)
                    cp = str(direc.dir_cp.cp)
                    preferencia = "X" if str(direc.preferencia) == "1" else ""
                    observ = str(direc.observ)
                    
                    col = 0
                    for i in [id_, persona_id, direccion, cp_id, cp, localidad,
                              provincia, preferencia, observ]:
                            
                        self.ui\
                            .tableWidget_direccion_per\
                            .setItem(fila, col, QtWidgets.QTableWidgetItem(i))

                        if col == 7:
                            # Centramos la preferencia.
                            item = self.ui.tableWidget_direccion_per.\
                                item(fila, col)
                            if item is not None:
                                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                                
                        col += 1
                
                # Cerramos la sesión
                ret[2].close()
                
    def poblar_mails(self):
        """Puebla los mails de la persona actual"""
        
        persona_id = self.ui.lineEdit_nrp_per.text().strip()
        if len(persona_id) == 0:
            pass
        
        else:
            
            persona_id = int(persona_id)
            bd = DBManager()
            
            ret = bd.obtener_mails_por_persona_id(persona_id)
            
            if ret[0]:
                # msg = f"Recuperados {len(ret[1])} mails." 
                # self.mostrar_mensaje(msg, caja_texto = False)
                                
                self.conf_contacto("mail")
                self.ui.tableWidget_mail_per.setRowCount(len(ret[1]))
                
                # Poblamos.
                fila = -1
                for mail in ret[1]:
                    
                    fila += 1
                                    
                    id_ = str(mail.id_)
                    persona_id = str(mail.persona_id)
                    correo = str(mail.mail)
                    preferencia = "X" if str(mail.preferencia) == "1" else ""
                    observ = str(mail.observ)
                    
                    col = 0
                    for i in [id_, persona_id, correo, preferencia, observ]:
                            
                        self.ui\
                            .tableWidget_mail_per\
                            .setItem(fila, col, QtWidgets.QTableWidgetItem(i))

                        if col == 3:
                            # Centramos la preferencia.
                            item = self.ui.tableWidget_mail_per.item(fila, col)
                            if item is not None:
                                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                                
                        col += 1
                        
    def poblar_tlfnos(self):
        """Puebla los teléfonos de la persona actual"""
        
        persona_id = self.ui.lineEdit_nrp_per.text().strip()
        if len(persona_id) == 0:
            pass
        
        else:
            
            persona_id = int(persona_id)
            bd = DBManager()
            
            ret = bd.obtener_telefonos_por_persona_id(persona_id)
            
            if ret[0]:
                # msg = f"Recuperados {len(ret[1])} teléfonos." 
                # self.mostrar_mensaje(msg, caja_texto = False)
                                
                self.conf_contacto("tlfno")     
                self.ui.tableWidget_tlfno_per.setRowCount(len(ret[1]))
                
                # Poblamos.
                fila = -1
                for tlfno in ret[1]:
                    
                    fila += 1
                                    
                    id_ = str(tlfno.id_)
                    persona_id = str(tlfno.persona_id)
                    tel = str(tlfno.numero)
                    preferencia = "X" if str(tlfno.preferencia) == "1" else ""
                    observ = str(tlfno.observ)
                    
                    col = 0
                    for i in [id_, persona_id, tel, preferencia, observ]:
                            
                        self.ui\
                            .tableWidget_tlfno_per\
                            .setItem(fila, col, QtWidgets.QTableWidgetItem(i))

                        if col == 3:
                            # Centramos la preferencia.
                            item = self.ui.tableWidget_tlfno_per.item(fila, col)
                            if item is not None:
                                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                                
                        col += 1
                        
    def __conf_mails(self, opcion):
        """Configuración de correos electrónicos"""
 
        if opcion == "editar":
            
            fila = self.ui.tableWidget_mail_per.currentRow()
            if fila >= 0:
                id_ = self.ui.tableWidget_mail_per.item(fila, 0).text()
                persona_id = self.ui.tableWidget_mail_per.item(fila, 1).text()
                correo = self.ui.tableWidget_mail_per.item(fila, 2).text()
                preferencia = self.ui.tableWidget_mail_per.item(fila, 3).text()                  
                observ = self.ui.tableWidget_mail_per.item(fila, 4).text()
                
                dialog = Dialog_Correos(int(id_), int(persona_id), correo,
                                        preferencia, observ)
                
        else:
            
            persona_id = self.ui.lineEdit_nrp_per.text().strip()
            if len(persona_id) > 0:
                dialog = Dialog_Correos(persona_id = int(persona_id))
         
        dialog.exec()        
        
        if dialog.ret["operacion"]:
            # Recargar datos, ya que algo se ha modificado.
            self.poblar_mails()
            
        else:
            msg = "No se han hecho cambios en correos electronicos."
            self.mostrar_mensaje(msg, caja_texto = False)                    
  
    def __conf_telefonos(self, opcion):
        """Configuración de teléfonos"""
 
        if opcion == "editar":
            
            fila = self.ui.tableWidget_tlfno_per.currentRow()
            if fila >= 0:
                id_ = self.ui.tableWidget_tlfno_per.item(fila, 0).text()
                numero = self.ui.tableWidget_tlfno_per.item(fila, 2).\
                    text()
                persona_id = self.ui.tableWidget_tlfno_per.item(fila, 1).text()
                preferencia = self.ui.tableWidget_tlfno_per.item(fila, 3).\
                    text()                  
                observ = self.ui.tableWidget_tlfno_per.item(fila, 4).text()
                
                dialog = Dialog_Telefonos(int(id_), int(persona_id), numero,
                                          preferencia, observ)
                
        else:
            persona_id = self.ui.lineEdit_nrp_per.text().strip()
            if len(persona_id) > 0:
                dialog = Dialog_Telefonos(persona_id = int(persona_id))
         
        dialog.exec()        
                    
        if dialog.ret["operacion"]:
            # Recargar datos, ya que algo se ha modificado.
            self.poblar_tlfnos()
            
        else:
            msg = "No se han hecho cambios en teléfonos."
            self.mostrar_mensaje(msg, caja_texto = False)      
        
    def OnBorrarFoto(self):
        """Borra la foto de la persona actual"""
        
        self.ui.label_foto_per.clear()
        
    def OnFoto(self):
        """Carga una foto en la persona actual"""
        
        nfich, _ = QFileDialog.getOpenFileName(self, "Seleccionar Foto", "", \
                                               "Imágenes (*.png)") 
        if nfich:
            
            try:
                
                # Redimensionar y mostrar la imagen en el QLabel
                
                image = Image.open(nfich)
                # tipo_imagen = image.format
                image_redim = image.resize((180, 180), Image.LANCZOS)
                pixmap = QPixmap.fromImage(image_redim.toqimage())
                pixmap.detach()
                self.ui.label_foto_per.setPixmap(pixmap)
            
                self.__foto = nfich

            except Exception as e:
                
                self.mostrar_mensaje("Error", \
                                     mas_info="Error al cargar la imagen",
                                     detalle=str(e),
                                     icono="critico")
                
            return True
        
    def OnBuscar(self):
        """Búsqueda de personas"""
        
        texto_a_buscar = self.ui.lineEdit_buscar_per.text()
        
        for fila in range(self.ui.tableWidget_per.rowCount()):
            # match_found = False
            #for column in range(self.table_widget.columnCount()):
            #    item = self.table_widget.item(row, column)
            #    if text.lower() in item.text().lower():
            #        match_found = True
            #        break
            
            if len(texto_a_buscar) == 0:
                # Se muestran todas las personas, si no hay nada dentro de la
                # caja de texto de búsqueda.
                self.ui.tableWidget_per.showRow(fila)
            else:
                # Se filtra por el contenido de la caja de búsqueda, ocultando
                # las filas que no contienen el texto.
                if texto_a_buscar.lower() in \
                   self.ui.tableWidget_per.item(fila, 1).text().lower():
                    
                    self.ui.tableWidget_per.showRow(fila)
                
                else:
                    
                    self.ui.tableWidget_per.hideRow(fila)
                
    def OnImpPersona(self):
        """Imprime la persona actual"""
        if self.__estado == "en_edicion" and \
           len(self.ui.lineEdit_nrp_per.text().strip()) == 0:
            self.mostrar_mensaje("No hay nada que imprimir", caja_texto = False)
        
        else:
    
            # Se recupera toda la información de la persona actual.
            
            dni = self.ui.lineEdit_dni_per.text()
            nombre = self.ui.lineEdit_nombre_per.text()
            ap1 = self.ui.lineEdit_1ap_per.text()
            ap2 = self.ui.lineEdit_2ap_per.text()
            fnac = self.ui.dateEdit_fnac_per.text()
            sexo = self.ui.comboBox_sexo_per.currentText()
            observ = self.ui.textEdit_observ_per.toPlainText()
            
            foto = self.ui.label_foto_per.pixmap().toImage()
            byte_array = QByteArray()    
            buffer = QBuffer(byte_array)
            buffer.open(QIODeviceBase.OpenModeFlag.WriteOnly)
            foto.save(buffer, "PNG") 
            buffer.close()
            foto = byte_array
            
            direccion = obs_dir = mail = obs_mail = tlfno = obs_tlfno = ""
            
            for i in [dni, nombre, ap1, ap2, fnac, sexo, observ]:
                if i is None: i = ""
                else: i = i.strip()
                
            for fila in range(self.ui.tableWidget_direccion_per.rowCount()):
                if self.ui.\
                   tableWidget_direccion_per.item(fila, 7).text() == "X":
                    direc = self.ui.\
                        tableWidget_direccion_per.item(fila, 2).text().strip()
                    cp = self.ui.\
                        tableWidget_direccion_per.item(fila, 4).text().strip()
                    local = self.ui.\
                        tableWidget_direccion_per.item(fila, 5).text().strip()
                    prov = self.ui.\
                        tableWidget_direccion_per.item(fila, 6).text().strip()
                    obs_dir = self.ui.\
                        tableWidget_direccion_per.item(fila, 8).text().strip()
                    direccion = f"{direc}, {cp} {local} ({prov})"
                    break
                
            for fila in range(self.ui.tableWidget_mail_per.rowCount()):
                if self.ui.tableWidget_mail_per.item(fila, 3).text() == "X":
                    mail = self.ui.\
                        tableWidget_mail_per.item(fila, 2).text().strip()
                    obs_mail = self.ui.\
                        tableWidget_mail_per.item(fila, 4).text().strip()
                    break
                
            for fila in range(self.ui.tableWidget_tlfno_per.rowCount()):
                if self.ui.tableWidget_tlfno_per.item(fila, 3).text() == "X":
                    tlfno = self.ui.\
                        tableWidget_tlfno_per.item(fila, 2).text().strip()
                    obs_tlfno = self.ui.\
                        tableWidget_tlfno_per.item(fila, 4).text().strip()
                    break
             
            # Se crea el paquete de datos para la persona actual.
            
            datos =  {'nombre': nombre,
                      'apellidos': f"{ap1} {ap2}",
                      'dni': dni,
                      'fnac' : fnac,
                      'sexo' : sexo,
                      'observ' : observ,
                      'direccion': direccion,
                      'obs_direccion': obs_dir,
                      'mail': mail,
                      'obs_mail': obs_mail,
                      'tlfno': tlfno,
                      'obs_tlfno': obs_tlfno,
                      'foto' : foto}
                    
            pdf = CrearInforme(ICO_APLICACION, datos)
            pdf.imprimir_informe()
                
    def OnBorrarPersona(self):
        """Borra la persona actual"""
        
        id_ = self.ui.lineEdit_nrp_per.text().strip() 
        #if self.__estado == "en_edicion" and \
        #   len(id_) == 0:
        if len(id_) == 0:
            self.mostrar_mensaje("No hay nada que eliminar", caja_texto = False)
        else:
            
            msg = "¿Eliminar la persona actual?"
            if self.mostrar_mensaje(texto = msg, cancel=True):
                
                bd = DBManager()
                ret = bd.baja_persona(id_)
            
                if ret[0]:
                    msg = f"Se ha eliminado la persona correctamente." 
                    self.mostrar_mensaje(msg, caja_texto = False)
                    self.cancelar_persona(False)
                    self.poblar_personas()
                else:
                    msg = "Error al eliminar a la persona actual"
                    self.mostrar_mensaje("Error", \
                                         mas_info=msg,
                                         detalle=str(ret[1]),
                                         icono="critico")                

    def cancelar_persona(self, recargar_persona = True):
        """Cancela operación"""
        
        id_ = self.ui.lineEdit_nrp_per.text()

        # Se limpian cajas de texto.
        for i in ["personal", "contacto", "otros"]: self.limpiar_datos(i)
                
        if recargar_persona:
            
            if self.__estado in ["en_edicion", "relacion"]:
                if recargar_persona: self.cargar_persona(id_)
                self.__estado = "en_edicion"
                if id_ != "": self.activar_elementos("en_edicion")
                    
            if self.__estado == "relacion":
                self.activar_elementos("relacion")
                
            if self.__estado == "alta":
                    
                # Se activa la búsqueda y la posibilidad de alta.
                for i in ["buscar", "alta"]: self.activar_elementos(i, True)
                
                # Se desactiva lo demás
                for i in ["contacto", "otros",  "personal"]:
                    self.activar_elementos(i, False)
                
                self.__foto = None
        
        else:
            self.activar_elementos("en_edicion", False)
            self.activar_elementos("alta", True)
                        
    def OnCancelarPersona(self):
        """Cancela la operación que se esté realizando"""
        
        self.cancelar_persona()
        
    def OnAltaPersona(self):
        """Da de alta una persona en el sistema"""
        
        self.__estado = "alta"
        
        # Se limpian cajas de texto.
        for i in ["personal", "contacto", "otros"]: self.limpiar_datos(i)
             
        # Se activa el grupo de datos de la persona.
        self.activar_elementos("personal")
        
        # Se desactivan restantes elementos que no pueden existir si antes
        # no existe la persona nueva.
        for i in ["contacto", "otros", "buscar", "alta"]:
            self.activar_elementos(i, False)
            
    def OnGuardarPersona(self):
        """Crea una persona nueva (datos pesonales) en el sistema"""
        
        # if self.__estado == "en_edicion" and \
        #    len(self.ui.lineEdit_nrp_per.text().strip()) == 0:
        if len(self.ui.lineEdit_nrp_per.text().strip()) == 0 and \
           self.__estado not in ["alta"]: 
            self.mostrar_mensaje("No hay nada que guardar", caja_texto = False)
        
        else:
            
            if self.__estado == "relacion": self.__estado = "en_edicion"
                
            nrp = self.ui.lineEdit_nrp_per.text()
            dni = self.ui.lineEdit_dni_per.text()
            nombre = self.ui.lineEdit_nombre_per.text()
            ap1 = self.ui.lineEdit_1ap_per.text()
            ap2 = self.ui.lineEdit_2ap_per.text()
            fnac = self.ui.dateEdit_fnac_per.text()
            sexo = self.ui.comboBox_sexo_per.currentText()
            observ = self.ui.textEdit_observ_per.toPlainText()
            
            if self.__estado == "alta":
                
                # Buscamos la foto.
                try:
                    with open(self.__foto, 'rb') as f:
                        foto = f.read()
                except:
                    foto = None

            else:
                
                # Recuperamos el tipo de relación.
                i = self.ui.comboBox_tipo_rel_per.currentIndex()
                tipo_rel_id = self.ui.comboBox_tipo_rel_per.itemData(i)
                if tipo_rel_id is not None: tipo_rel_id = int(tipo_rel_id)
                if tipo_rel_id == "": tipo_rel_id = None
                     
                # Recuperamos la persona relacionada.
                relacionado_con_id = self.ui.lineEdit_relacionado_con_id.text()
                if relacionado_con_id == "": relacionado_con_id = None
                if relacionado_con_id is not None:
                    relacionado_con_id = int(relacionado_con_id)
                
                # Se recupera la imagen del QLabel, para crear un flujo de 
                # bytes y poder guardarlos en la base de datos.
                
                foto = self.ui.label_foto_per.pixmap().toImage()
                
                # if len(foto) == 0: foto = None
                # else:
                byte_array = QByteArray()    
                buffer = QBuffer(byte_array)
                buffer.open(QIODeviceBase.OpenModeFlag.WriteOnly)
                foto.save(buffer, "PNG") 
                buffer.close()
                    
                foto = byte_array
                    
            # Comprobamos si la fecha es correcta.
            try:
                fecha_obj = datetime.strptime(fnac, "%d/%m/%Y")
                fecha_formateada = fecha_obj.strftime("%Y-%m-%d")
            except ValueError:
                fecha_formateada = None
        
            if fecha_formateada is None:
                self.mostrar_mensaje("El formato de fecha no es correcto", 
                                     icono="peligro")
            else:
            
                bd = DBManager()
                
                if self.__estado == "alta":
                  
                    ret = bd.alta_persona(dni.strip(), nombre.strip(),
                                          ap1.strip(), ap2.strip(),
                                          fecha_formateada, foto, sexo)
                    aux = "dado de alta"
                    
                    # Se incluye el id_ como NRP.
                    # self.ui.lineEdit_nrp_per.setText(str(ret[1]))
                
                if self.__estado == "en_edicion":
                    
                    # Modificamos.
                    ret = bd.modificar_persona(int(nrp), dni.strip(),
                                              nombre.strip(), ap1.strip(),
                                              ap2.strip(), fecha_formateada,
                                              foto, sexo, observ.strip(),
                                              tipo_rel_id, relacionado_con_id)
                    
                    aux = "modificado"
                    
                if ret[0]:
                    
                    if self.__estado == "alta":
                        self.ui.lineEdit_nrp_per.setText(str(ret[1]))
                    
                    msg = f"Se ha {aux} a {nombre} {ap1} correctamente." 
                    self.mostrar_mensaje(msg, caja_texto = False)
                    
                    # self.OnCancelarPersona()
                
                    self.__foto = None
                    self.__estado = "en_edicion"
                    
                    # Se recargan todas las personas, de nuevo.
                    
                    self.poblar_personas()
                    
                    # Se activan todos los botones.
                    
                    for i in ["personal", "contacto",
                              "otros", "buscar", "alta"]:
                        self.activar_elementos(i)
                    
                    
                else:
                    self.mostrar_mensaje(f"Fallo al crear/modificar a la persona", \
                                         caja_texto = False)
                    
                    msg = "- El DNI debe tener 8 dígitos y una letra, y no debe" + \
                        " de existir en la base de datos previamente.\n" + \
                        "- El nombre, primer apellido y fecha de nacimiento" + \
                        " son obligatorios."
        
                    self.mostrar_mensaje("No se ha podido dar de alta/modificar",
                                         mas_info=msg,
                                         detalle = str(ret[1]),
                                         icono="critico")    
    
