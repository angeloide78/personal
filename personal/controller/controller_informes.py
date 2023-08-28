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

import subprocess
import sys
import os.path
from io import BytesIO

from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    
class InformeReportLab:
    """Informe de la aplicación"""
    
    def __init__(self, ruta_logo= None, nombre_pdf = "report.pdf"):
        """Inicializa un informe"""
        
        self.__ruta_logo = ruta_logo
        self.__nombre_pdf = nombre_pdf
        
    def crear_informe(self, datos, cabecera, orientacion = "v"):
        """Crea un informe a partir de los datos pasados como parámetros. La
        orientación del documento puede ser "v" (vertical) u "h" (horizontal).
        """
        
        if orientacion == "v": t = portrait(A4)
        if orientacion == "h": t = landscape(A4)
             
        # Se crea la plantilla del documento.
        doc = SimpleDocTemplate(self.__nombre_pdf, pagesize=t, 
                                title="personal, gestión de personas",
                                leftMargin=40, rightMargin=40, topMargin=40,
                                bottomMargin=40)
        story = []

        # Agregar el logo de la empresa a la cabecera
        if self.__ruta_logo:
            logo = Image(self.__ruta_logo, width=64, height=64)  
            story.append(logo)
        
        story.append(Spacer(0, 20))
         
        # Se crea el estilo.
        estilo = getSampleStyleSheet()
        
        # Agregamos cabecera y su estilo.
        texto_cabecera = cabecera
        estilo_cabecera = estilo['Title']
        
        # Se añade un Paragraph.
        story.append(Paragraph(texto_cabecera, estilo_cabecera))
       
        story.append(Spacer(0, 20))
        
        # Agregar la foto (asumiendo que 'foto' es un flujo de bytes)
        if datos['foto']:
            foto = Image(BytesIO(datos['foto']), width=180, height=180)
            story.append(foto)
        
        story.append(Spacer(0, 20))
        
        # Agregar los datos de la persona
        for i in ['obs_direccion', 'obs_mail', 'obs_tlfno']:
            if datos[i] not in ["", None]: datos[i] = f"({datos[i]})"
             
        info = f"""
        <b>Nombre:</b> {datos['nombre']} {datos["apellidos"]}<br/>
        <b>DNI:</b> {datos['dni']}<br/><br/>
        <b>Sexo:</b> {datos['sexo']}<br/>
        <b>Fecha nacimiento:</b> {datos['fnac']}<br/>
        <b>Información:</b> {datos['observ']}<br/><br/>
        <b>Dirección:</b> {datos['direccion']} {datos["obs_direccion"]}<br/>
        <b>Correo Electrónico:</b> {datos['mail']} {datos["obs_mail"]}<br/>
        <b>Teléfono:</b> {datos['tlfno']} {datos["obs_tlfno"]}<br/>
        """        
        
        estilo_info = ParagraphStyle(name='InfoPersona',
                                     parent=estilo['Normal'])
        para_info = Paragraph(info, estilo_info)
        story.append(para_info)
                
        doc.build(story)
        
class CrearInforme:
    """Informes de carritos"""
    
    def __init__(self, ruta_logo, datos):
        
        self.__ruta_logo = ruta_logo
        self.__datos = datos
                
    def __ruta_pdf(self, nombre_pdf):
        """Devuelve la ruta del fichero pdf"""
        
        ejecucion_dir = os.path.dirname(os.path.abspath(__file__))
        dir_actual = os.path.abspath(os.path.join(ejecucion_dir, '..'))       
        
        return os.path.join(*[dir_actual, "static", "pdf", nombre_pdf])                
                
    def imprimir_informe(self, nombre_pdf = "informe_personal.pdf", \
                         cabecera= "Informe Personal", \
                         visualizar_pdf=True, \
                         orientacion="v"):
        """Imprime un informe"""
        
        # Se genera el PDF    
        informe = InformeReportLab(self.__ruta_logo, \
                                   self.__ruta_pdf(nombre_pdf))
        informe.crear_informe(self.__datos, cabecera, orientacion)
        
        # Se visualiza por pantalla el PDF.
        if visualizar_pdf: self.visualizar_informe(self.__ruta_pdf(nombre_pdf))
        
    def visualizar_informe(self, nombre_pdf):
        """Visualiza el PDF con la aplicación por defecto del sistema."""
        
        if sys.platform.startswith('linux'):
            subprocess.run(['xdg-open', self.__ruta_pdf(nombre_pdf)])
        elif sys.platform.startswith('win'):
            subprocess.run(['start', '', self.__ruta_pdf(nombre_pdf)], \
                           shell=True)
