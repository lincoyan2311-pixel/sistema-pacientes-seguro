"""Pruebas de las funciones de validación."""

import pytest

from validaciones import (
    calcular_digito_verificador,
    sanitizar_diagnostico,
    sanitizar_estructura_paciente,
    sanitizar_nombre,
    validar_correo,
    validar_edad,
    validar_rut,
)


def test_sanitizar_nombre_valido() -> None:
    assert sanitizar_nombre("  ana   pérez  ") == "Ana Pérez"


def test_sanitizar_nombre_elimina_numeros() -> None:
    assert sanitizar_nombre("Ana123 Pérez") == "Ana Pérez"


def test_sanitizar_nombre_vacio_genera_error() -> None:
    with pytest.raises(ValueError):
        sanitizar_nombre("   ")


def test_validar_edad_correcta() -> None:
    assert validar_edad("35") == 35


def test_validar_edad_negativa_genera_error() -> None:
    with pytest.raises(ValueError):
        validar_edad("-1")


def test_validar_edad_excesiva_genera_error() -> None:
    with pytest.raises(ValueError):
        validar_edad("121")


def test_validar_edad_decimal_genera_error() -> None:
    with pytest.raises(ValueError):
        validar_edad("20.5")


def test_validar_correo_correcto() -> None:
    assert validar_correo("Persona.Prueba@example.com") == (
        "persona.prueba@example.com"
    )


def test_validar_correo_incorrecto() -> None:
    with pytest.raises(ValueError):
        validar_correo("persona@correo")


def test_calcular_digito_verificador() -> None:
    assert calcular_digito_verificador("12345678") == "5"


def test_validar_rut_correcto() -> None:
    assert validar_rut("12.345.678-5") == "12345678-5"


def test_validar_rut_incorrecto() -> None:
    with pytest.raises(ValueError):
        validar_rut("12.345.678-9")


def test_sanitizar_diagnostico_elimina_html() -> None:
    resultado = sanitizar_diagnostico(
        "Control <script>malicioso</script> preventivo"
    )
    assert "<script>" not in resultado
    assert "</script>" not in resultado


def test_sanitizar_estructura_completa() -> None:
    datos = {
        "nombre": "Ana Pérez",
        "rut": "12.345.678-5",
        "edad": "35",
        "correo": "ANA@example.com",
        "diagnostico": "Control preventivo",
    }
    resultado = sanitizar_estructura_paciente(datos)
    assert resultado["nombre"] == "Ana Pérez"
    assert resultado["rut"] == "12345678-5"
    assert resultado["edad"] == 35
    assert resultado["correo"] == "ana@example.com"


def test_sanitizar_estructura_con_campo_faltante() -> None:
    datos = {"nombre": "Ana Pérez", "rut": "12.345.678-5"}
    with pytest.raises(ValueError):
        sanitizar_estructura_paciente(datos)


def test_diagnostico_demasiado_largo_genera_error() -> None:
    """Prueba adicional propuesta con apoyo de IA y revisada manualmente."""
    with pytest.raises(ValueError):
        sanitizar_diagnostico("a" * 151)
