"""Funciones de validación y sanitización de datos."""

import re
from typing import Any


LONGITUD_MAXIMA_NOMBRE = 80
LONGITUD_MAXIMA_DIAGNOSTICO = 150
EDAD_MINIMA = 0
EDAD_MAXIMA = 120


def asegurar_texto(valor: Any, nombre_campo: str) -> str:
    """Comprueba que un valor sea texto y quita espacios externos."""
    if not isinstance(valor, str):
        raise ValueError(f"El campo {nombre_campo} debe ser texto.")
    return valor.strip()


def sanitizar_nombre(nombre: str) -> str:
    """Limpia un nombre y conserva solamente caracteres permitidos."""
    nombre = asegurar_texto(nombre, "nombre")
    nombre = re.sub(r"\s+", " ", nombre)
    nombre = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚüÜñÑ' -]", "", nombre)
    nombre = nombre.strip()

    if not nombre:
        raise ValueError("El nombre no puede estar vacío.")
    if len(nombre) < 3:
        raise ValueError("El nombre debe contener al menos 3 caracteres.")
    if len(nombre) > LONGITUD_MAXIMA_NOMBRE:
        raise ValueError(
            f"El nombre no puede superar {LONGITUD_MAXIMA_NOMBRE} caracteres."
        )
    return nombre.title()


def limpiar_rut(rut: str) -> str:
    """Elimina puntos, espacios y guiones del RUT."""
    rut = asegurar_texto(rut, "RUT")
    return re.sub(r"[^0-9kK]", "", rut).upper()


def calcular_digito_verificador(cuerpo: str) -> str:
    """Calcula el dígito verificador de un RUT chileno."""
    if not cuerpo.isdigit():
        raise ValueError("El cuerpo del RUT debe contener solo números.")

    suma = 0
    multiplicador = 2
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2

    resultado = 11 - (suma % 11)
    if resultado == 11:
        return "0"
    if resultado == 10:
        return "K"
    return str(resultado)


def validar_rut(rut: str) -> str:
    """Valida el RUT y lo devuelve sin puntos y con guion."""
    rut_limpio = limpiar_rut(rut)
    if len(rut_limpio) < 8 or len(rut_limpio) > 9:
        raise ValueError("El RUT debe tener entre 8 y 9 caracteres.")

    cuerpo = rut_limpio[:-1]
    digito_recibido = rut_limpio[-1]
    if not cuerpo.isdigit():
        raise ValueError("El cuerpo del RUT debe ser numérico.")
    if digito_recibido != calcular_digito_verificador(cuerpo):
        raise ValueError("El RUT ingresado no es válido.")
    return f"{int(cuerpo)}-{digito_recibido}"


def validar_edad(edad: Any) -> int:
    """Valida que la edad sea un entero entre 0 y 120."""
    if isinstance(edad, bool):
        raise ValueError("La edad debe ser un número entero.")
    try:
        edad_numerica = int(edad)
    except (TypeError, ValueError) as error:
        raise ValueError("La edad debe ser un número entero.") from error

    if isinstance(edad, float) and not edad.is_integer():
        raise ValueError("La edad no puede contener decimales.")
    if isinstance(edad, str) and not re.fullmatch(r"\d{1,3}", edad.strip()):
        raise ValueError("La edad debe contener solo números enteros.")
    if edad_numerica < EDAD_MINIMA or edad_numerica > EDAD_MAXIMA:
        raise ValueError(
            f"La edad debe estar entre {EDAD_MINIMA} y {EDAD_MAXIMA} años."
        )
    return edad_numerica


def validar_correo(correo: str) -> str:
    """Realiza una validación básica de correo electrónico."""
    correo = asegurar_texto(correo, "correo").lower()
    if len(correo) > 254:
        raise ValueError("El correo electrónico es demasiado largo.")

    patron = re.compile(
        r"^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+"
        r"@[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
        r"(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$"
    )
    if not patron.fullmatch(correo):
        raise ValueError("El correo electrónico no tiene un formato válido.")
    return correo


def sanitizar_diagnostico(diagnostico: str) -> str:
    """Limpia un diagnóstico ficticio y limita su longitud."""
    diagnostico = asegurar_texto(diagnostico, "diagnóstico")
    diagnostico = re.sub(r"<[^>]*>", "", diagnostico)
    diagnostico = re.sub(r"[\x00-\x1f\x7f]", "", diagnostico)
    diagnostico = re.sub(
        r"[^a-zA-ZáéíóúÁÉÍÓÚüÜñÑ0-9 .,;:()'/-]", "", diagnostico
    )
    diagnostico = re.sub(r"\s+", " ", diagnostico).strip()

    if not diagnostico:
        raise ValueError("El diagnóstico no puede estar vacío.")
    if len(diagnostico) < 3:
        raise ValueError("El diagnóstico debe contener al menos 3 caracteres.")
    if len(diagnostico) > LONGITUD_MAXIMA_DIAGNOSTICO:
        raise ValueError(
            "El diagnóstico no puede superar "
            f"{LONGITUD_MAXIMA_DIAGNOSTICO} caracteres."
        )
    return diagnostico


def sanitizar_estructura_paciente(datos: dict[str, Any]) -> dict[str, Any]:
    """Valida y sanitiza una estructura completa de paciente."""
    if not isinstance(datos, dict):
        raise ValueError("Los datos del paciente deben ser un diccionario.")

    campos_requeridos = {"nombre", "rut", "edad", "correo", "diagnostico"}
    campos_faltantes = campos_requeridos - set(datos.keys())
    if campos_faltantes:
        campos = ", ".join(sorted(campos_faltantes))
        raise ValueError(f"Faltan los siguientes campos: {campos}.")

    return {
        "nombre": sanitizar_nombre(datos["nombre"]),
        "rut": validar_rut(datos["rut"]),
        "edad": validar_edad(datos["edad"]),
        "correo": validar_correo(datos["correo"]),
        "diagnostico": sanitizar_diagnostico(datos["diagnostico"]),
    }
