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
import platform

ejecucion_dir = os.path.dirname(os.path.abspath(__file__))
dir_actual = os.path.abspath(os.path.join(ejecucion_dir, '..'))

if platform.system() == "Windows": img_aplic = "icono_aplicacion.ico"
if platform.system() == "Linux": img_aplic = "icono_aplicacion.png"            

ICO_APLICACION = os.path.join(*[dir_actual, "assets", "imagenes", img_aplic])
ICO_ACERCADE = os.path.join(*[dir_actual, "assets", "imagenes", \
                                "icono_aplicacion.png"])
ICO_ALTA = os.path.join(*[dir_actual,"assets", "imagenes", "alta.png"])
ICO_BAJA = os.path.join(*[dir_actual,"assets", "imagenes", "baja.png"])
ICO_CANCELAR = os.path.join(*[dir_actual,"assets", "imagenes", "cancelar.png"])
ICO_GUARDAR = os.path.join(*[dir_actual,"assets", "imagenes", "guardar.png"])
ICO_IMPRIMIR = os.path.join(*[dir_actual,"assets", "imagenes", "imprimir.png"])
ICO_ADD = os.path.join(*[dir_actual,"assets", "imagenes", "add.png"])
ICO_SGTE = os.path.join(*[dir_actual,"assets", "imagenes", "siguiente.png"])
ICO_ANT = os.path.join(*[dir_actual,"assets", "imagenes", "anterior.png"])
ICO_INFO = os.path.join(*[dir_actual,"assets", "imagenes", "info.png"])

