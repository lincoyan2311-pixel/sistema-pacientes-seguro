"""Lectura, escritura e integridad del archivo de pacientes."""

import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any


DIRECTORIO_DATOS = Path("datos")
ARCHIVO_PACIENTES = DIRECTORIO_DATOS / "pacientes.json"
ARCHIVO_HASH = DIRECTORIO_DATOS / "pacientes.sha256"


class ErrorIntegridadDatos(Exception):
    """Se produce cuando el archivo no coincide con su hash."""


class ErrorAlmacenamiento(Exception):
    """Se produce cuando no es posible leer o escribir los datos."""


def preparar_directorio() -> None:
    """Crea el directorio de datos si todavía no existe."""
    DIRECTORIO_DATOS.mkdir(parents=True, exist_ok=True, mode=0o700)


def calcular_hash_archivo(ruta: Path) -> str:
    """Calcula el hash SHA-256 de un archivo, leyendo por bloques."""
    sha256 = hashlib.sha256()
    try:
        with ruta.open("rb") as archivo:
            while bloque := archivo.read(8192):
                sha256.update(bloque)
    except OSError as error:
        raise ErrorAlmacenamiento(
            "No fue posible calcular la integridad del archivo."
        ) from error
    return sha256.hexdigest()


def guardar_hash() -> None:
    """Calcula y guarda el hash del archivo de pacientes."""
    if not ARCHIVO_PACIENTES.exists():
        raise ErrorAlmacenamiento("No existe el archivo de pacientes.")
    resumen = calcular_hash_archivo(ARCHIVO_PACIENTES)
    try:
        ARCHIVO_HASH.write_text(resumen, encoding="utf-8")
    except OSError as error:
        raise ErrorAlmacenamiento(
            "No fue posible guardar el archivo de integridad."
        ) from error


def verificar_integridad() -> bool:
    """Compara el SHA-256 actual con el resumen guardado."""
    if not ARCHIVO_PACIENTES.exists():
        return True
    if not ARCHIVO_HASH.exists():
        raise ErrorIntegridadDatos(
            "Existe el archivo de pacientes, pero no su hash."
        )
    try:
        hash_guardado = ARCHIVO_HASH.read_text(encoding="utf-8").strip()
    except OSError as error:
        raise ErrorAlmacenamiento(
            "No fue posible leer el archivo de integridad."
        ) from error

    hash_actual = calcular_hash_archivo(ARCHIVO_PACIENTES)
    if not hash_guardado:
        raise ErrorIntegridadDatos("El archivo de integridad está vacío.")
    if not hmac.compare_digest(hash_guardado, hash_actual):
        raise ErrorIntegridadDatos(
            "La integridad de los datos no pudo comprobarse. "
            "El archivo podría haber sido modificado."
        )
    return True


def cargar_pacientes() -> list[dict[str, Any]]:
    """Carga los pacientes; si no hay archivo, devuelve una lista vacía."""
    preparar_directorio()
    if not ARCHIVO_PACIENTES.exists():
        return []
    verificar_integridad()
    try:
        with ARCHIVO_PACIENTES.open("r", encoding="utf-8") as archivo:
            contenido = json.load(archivo)
    except json.JSONDecodeError as error:
        raise ErrorAlmacenamiento(
            "El archivo de pacientes contiene JSON inválido."
        ) from error
    except OSError as error:
        raise ErrorAlmacenamiento(
            "No fue posible leer el archivo de pacientes."
        ) from error

    if not isinstance(contenido, list):
        raise ErrorAlmacenamiento(
            "La estructura principal del archivo debe ser una lista."
        )
    return [elemento for elemento in contenido if isinstance(elemento, dict)]


def escritura_atomica(ruta: Path, contenido: str) -> None:
    """Escribe en un archivo temporal antes de reemplazar el original."""
    ruta_temporal = ruta.with_suffix(ruta.suffix + ".tmp")
    try:
        ruta_temporal.write_text(contenido, encoding="utf-8")
        os.replace(ruta_temporal, ruta)
    except OSError as error:
        try:
            if ruta_temporal.exists():
                ruta_temporal.unlink()
        except OSError:
            pass
        raise ErrorAlmacenamiento("No fue posible guardar los datos.") from error


def guardar_pacientes(pacientes: list[dict[str, Any]]) -> None:
    """Guarda la lista completa de pacientes y actualiza su hash."""
    preparar_directorio()
    if not isinstance(pacientes, list):
        raise ErrorAlmacenamiento("Los pacientes deben almacenarse en una lista.")
    try:
        contenido = json.dumps(pacientes, ensure_ascii=False, indent=4)
    except (TypeError, ValueError) as error:
        raise ErrorAlmacenamiento(
            "Los datos no pueden convertirse a JSON."
        ) from error
    escritura_atomica(ARCHIVO_PACIENTES, contenido)
    guardar_hash()
