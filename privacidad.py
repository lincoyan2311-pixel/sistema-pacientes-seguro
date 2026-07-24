"""Funciones básicas de anonimización y seudonimización."""

import secrets
import string


ALFABETO_SEGURO = string.ascii_uppercase + string.digits


def generar_id_paciente(longitud: int = 12) -> str:
    """Genera un identificador seudónimo usando valores seguros."""
    if longitud < 8 or longitud > 32:
        raise ValueError("La longitud del identificador debe estar entre 8 y 32.")
    parte_aleatoria = "".join(
        secrets.choice(ALFABETO_SEGURO) for _ in range(longitud)
    )
    return f"PAC-{parte_aleatoria}"


def anonimizar_nombre(nombre: str) -> str:
    """Deja visible solamente la primera letra de cada palabra."""
    if not isinstance(nombre, str) or not nombre.strip():
        return "NO DISPONIBLE"

    partes_anonimizadas = []
    for parte in nombre.strip().split():
        if len(parte) == 1:
            partes_anonimizadas.append("*")
        else:
            partes_anonimizadas.append(parte[0] + "*" * (len(parte) - 1))
    return " ".join(partes_anonimizadas)


def anonimizar_rut(rut: str) -> str:
    """Oculta el cuerpo del RUT y conserva el dígito verificador."""
    if not isinstance(rut, str) or "-" not in rut:
        return "NO DISPONIBLE"
    cuerpo, digito_verificador = rut.rsplit("-", maxsplit=1)
    if not cuerpo or not digito_verificador:
        return "NO DISPONIBLE"
    return f"{'*' * len(cuerpo)}-{digito_verificador}"


def anonimizar_correo(correo: str) -> str:
    """Oculta el usuario del correo, excepto su primera letra."""
    if not isinstance(correo, str) or "@" not in correo:
        return "NO DISPONIBLE"
    usuario, dominio = correo.rsplit("@", maxsplit=1)
    if not usuario or not dominio:
        return "NO DISPONIBLE"
    usuario_oculto = "*" if len(usuario) == 1 else usuario[0] + "*" * (len(usuario) - 1)
    return f"{usuario_oculto}@{dominio}"


def crear_vista_anonimizada(
    paciente: dict[str, object],
) -> dict[str, object]:
    """Crea una copia para reportes sin incluir el diagnóstico."""
    return {
        "id_paciente": paciente.get("id_paciente", "NO DISPONIBLE"),
        "nombre": anonimizar_nombre(str(paciente.get("nombre", ""))),
        "rut": anonimizar_rut(str(paciente.get("rut", ""))),
        "edad": paciente.get("edad", "NO DISPONIBLE"),
        "correo": anonimizar_correo(str(paciente.get("correo", ""))),
        "fecha_registro": paciente.get("fecha_registro", "NO DISPONIBLE"),
    }
