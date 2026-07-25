"""Pruebas del guardado y la comprobación de integridad."""

from pathlib import Path

import pytest

import almacenamiento
from almacenamiento import ErrorIntegridadDatos


def usar_directorio_temporal(
    monkeypatch: pytest.MonkeyPatch, directorio: Path
) -> None:
    """Evita usar la carpeta datos real durante las pruebas."""
    monkeypatch.setattr(almacenamiento, "DIRECTORIO_DATOS", directorio)
    monkeypatch.setattr(
        almacenamiento, "ARCHIVO_PACIENTES", directorio / "pacientes.json"
    )
    monkeypatch.setattr(
        almacenamiento, "ARCHIVO_HASH", directorio / "pacientes.sha256"
    )


def test_guardar_y_cargar_pacientes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    usar_directorio_temporal(monkeypatch, tmp_path)
    pacientes = [{"id_paciente": "PAC-EJEMPLO1234", "nombre": "Ana Prueba"}]

    almacenamiento.guardar_pacientes(pacientes)

    assert almacenamiento.ARCHIVO_PACIENTES.exists()
    assert almacenamiento.ARCHIVO_HASH.exists()
    assert almacenamiento.cargar_pacientes() == pacientes


def test_detectar_archivo_modificado(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    usar_directorio_temporal(monkeypatch, tmp_path)
    almacenamiento.guardar_pacientes([{"nombre": "Ana Prueba"}])
    almacenamiento.ARCHIVO_PACIENTES.write_text(
        '[{"nombre": "Texto alterado"}]', encoding="utf-8"
    )

    with pytest.raises(ErrorIntegridadDatos):
        almacenamiento.verificar_integridad()


def test_verificar_integridad_sin_archivo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    usar_directorio_temporal(monkeypatch, tmp_path)

    assert almacenamiento.verificar_integridad() is None
