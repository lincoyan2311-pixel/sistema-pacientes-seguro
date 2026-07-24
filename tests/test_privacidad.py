"""Pruebas de anonimización y seudonimización."""

import pytest

from privacidad import (
    anonimizar_correo,
    anonimizar_nombre,
    anonimizar_rut,
    crear_vista_anonimizada,
    generar_id_paciente,
)


def test_generar_id_paciente() -> None:
    identificador = generar_id_paciente()
    assert identificador.startswith("PAC-")
    assert len(identificador) == 16


def test_ids_deben_ser_distintos() -> None:
    assert generar_id_paciente() != generar_id_paciente()


def test_generar_id_rechaza_longitud_invalida() -> None:
    with pytest.raises(ValueError):
        generar_id_paciente(5)


def test_anonimizar_nombre() -> None:
    assert anonimizar_nombre("Ana Pérez") == "A** P****"


def test_anonimizar_rut() -> None:
    assert anonimizar_rut("12345678-5") == "********-5"


def test_anonimizar_correo() -> None:
    assert anonimizar_correo("ana.perez@example.com") == (
        "a********@example.com"
    )


def test_vista_no_incluye_diagnostico() -> None:
    paciente = {
        "id_paciente": "PAC-12345678",
        "nombre": "Ana Pérez",
        "rut": "12345678-5",
        "edad": 35,
        "correo": "ana@example.com",
        "diagnostico": "Información sensible",
        "fecha_registro": "2026-01-01T10:00:00+00:00",
    }
    vista = crear_vista_anonimizada(paciente)
    assert "diagnostico" not in vista
    assert vista["nombre"] == "A** P****"
    assert vista["rut"] == "********-5"
