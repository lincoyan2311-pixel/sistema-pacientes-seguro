"""Pruebas de la interfaz de consola y sus opciones principales."""

from typing import Any

import pytest

import app
from almacenamiento import ErrorAlmacenamiento, ErrorIntegridadDatos


def paciente_ejemplo() -> dict[str, Any]:
    """Entrega datos ficticios válidos para las pruebas."""
    return {
        "id_paciente": "PAC-ABCDEF123456",
        "nombre": "Ana Prueba",
        "rut": "12.345.678-5",
        "edad": 31,
        "correo": "ana.prueba@example.com",
        "diagnostico": "Control preventivo",
        "fecha_registro": "2026-07-24T12:00:00+00:00",
    }


def test_mostrar_encabezado_y_menu(capsys: pytest.CaptureFixture[str]) -> None:
    app.mostrar_encabezado()
    app.mostrar_menu()

    salida = capsys.readouterr().out
    assert "SISTEMA SEGURO" in salida
    assert "Registrar paciente" in salida
    assert "5. Salir" in salida


def test_solicitar_datos_paciente(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    respuestas = iter(
        [
            "Ana Prueba",
            "12.345.678-5",
            "31",
            "ana.prueba@example.com",
            "Control preventivo",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _mensaje: next(respuestas))

    datos = app.solicitar_datos_paciente()

    assert datos["nombre"] == "Ana Prueba"
    assert datos["edad"] == "31"
    assert datos["diagnostico"] == "Control preventivo"


def test_busquedas_y_creacion_de_identificador(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pacientes = [paciente_ejemplo()]
    assert app.existe_rut(pacientes, "12.345.678-5")
    assert app.existe_identificador(pacientes, "PAC-ABCDEF123456")
    assert not app.existe_rut(pacientes, "11.111.111-1")

    identificadores = iter(["PAC-ABCDEF123456", "PAC-NUEVO123456"])
    monkeypatch.setattr(
        app, "generar_id_paciente", lambda: next(identificadores)
    )
    assert app.crear_identificador_unico(pacientes) == "PAC-NUEVO123456"


def test_crear_identificador_detecta_colisiones(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pacientes = [paciente_ejemplo()]
    monkeypatch.setattr(
        app, "generar_id_paciente", lambda: "PAC-ABCDEF123456"
    )

    with pytest.raises(RuntimeError):
        app.crear_identificador_unico(pacientes)


def test_registrar_paciente_correctamente(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    pacientes: list[dict[str, Any]] = []
    datos = paciente_ejemplo()
    datos.pop("id_paciente")
    datos.pop("fecha_registro")

    monkeypatch.setattr(app, "solicitar_datos_paciente", lambda: {})
    monkeypatch.setattr(
        app, "sanitizar_estructura_paciente", lambda _datos: datos
    )
    monkeypatch.setattr(
        app, "crear_identificador_unico", lambda _lista: "PAC-NUEVO123456"
    )
    monkeypatch.setattr(app, "guardar_pacientes", lambda _lista: None)

    app.registrar_paciente(pacientes)

    assert len(pacientes) == 1
    assert pacientes[0]["id_paciente"] == "PAC-NUEVO123456"
    assert "Paciente registrado correctamente" in capsys.readouterr().out


def test_registrar_rechaza_rut_repetido(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    pacientes = [paciente_ejemplo()]
    datos = paciente_ejemplo()
    datos.pop("id_paciente")
    datos.pop("fecha_registro")
    monkeypatch.setattr(app, "solicitar_datos_paciente", lambda: {})
    monkeypatch.setattr(
        app, "sanitizar_estructura_paciente", lambda _datos: datos
    )

    app.registrar_paciente(pacientes)

    assert len(pacientes) == 1
    assert "Ya existe un paciente" in capsys.readouterr().out


def test_registrar_controla_errores(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    pacientes: list[dict[str, Any]] = []
    monkeypatch.setattr(app, "solicitar_datos_paciente", lambda: {})

    def rechazar_datos(_datos: dict[str, str]) -> dict[str, Any]:
        raise ValueError("Dato inválido")

    monkeypatch.setattr(app, "sanitizar_estructura_paciente", rechazar_datos)
    app.registrar_paciente(pacientes)
    assert "Datos rechazados" in capsys.readouterr().out

    datos = paciente_ejemplo()
    datos.pop("id_paciente")
    datos.pop("fecha_registro")
    monkeypatch.setattr(
        app, "sanitizar_estructura_paciente", lambda _datos: datos
    )
    monkeypatch.setattr(
        app, "crear_identificador_unico", lambda _lista: "PAC-NUEVO123456"
    )

    def fallar_guardado(_lista: list[dict[str, Any]]) -> None:
        raise ErrorAlmacenamiento("Disco no disponible")

    monkeypatch.setattr(app, "guardar_pacientes", fallar_guardado)
    app.registrar_paciente(pacientes)
    assert pacientes == []
    assert "No fue posible guardar" in capsys.readouterr().out

    def fallar_identificador(_lista: list[dict[str, Any]]) -> str:
        raise RuntimeError("Sin identificador")

    monkeypatch.setattr(app, "crear_identificador_unico", fallar_identificador)
    app.registrar_paciente(pacientes)
    assert "Error al generar" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("entrada", "mensaje"),
    [
        ("ABC", "comenzar con PAC-"),
        ("PAC-1", "longitud"),
        ("PAC-ABC_DEF12", "caracteres inválidos"),
    ],
)
def test_normalizar_identificador_rechaza_entradas(
    entrada: str, mensaje: str
) -> None:
    with pytest.raises(ValueError, match=mensaje):
        app.normalizar_identificador(entrada)


def test_normalizar_identificador_valido() -> None:
    assert app.normalizar_identificador(" pac-abcdef12 ") == "PAC-ABCDEF12"


def test_buscar_paciente(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    pacientes = [paciente_ejemplo()]

    monkeypatch.setattr("builtins.input", lambda _mensaje: "ABC")
    app.buscar_paciente(pacientes)
    assert "Identificador rechazado" in capsys.readouterr().out

    monkeypatch.setattr(
        "builtins.input", lambda _mensaje: "PAC-NOEXISTE12"
    )
    app.buscar_paciente(pacientes)
    assert "No se encontró" in capsys.readouterr().out

    monkeypatch.setattr(
        "builtins.input", lambda _mensaje: "PAC-ABCDEF123456"
    )
    app.buscar_paciente(pacientes)
    salida = capsys.readouterr().out
    assert "PACIENTE ENCONTRADO" in salida
    assert "A** P*****" in salida
    assert "Control preventivo" not in salida


def test_imprimir_y_mostrar_reporte(
    capsys: pytest.CaptureFixture[str],
) -> None:
    app.imprimir_paciente_anonimizado({})
    assert "NO DISPONIBLE" in capsys.readouterr().out

    app.mostrar_reporte([])
    assert "No existen pacientes" in capsys.readouterr().out

    app.mostrar_reporte([paciente_ejemplo()])
    salida = capsys.readouterr().out
    assert "Paciente número 1" in salida
    assert "Control preventivo" not in salida


def test_comprobar_integridad_desde_menu(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(app, "cargar_pacientes", lambda: [])
    app.comprobar_integridad_desde_menu()
    assert "integridad de los datos es correcta" in capsys.readouterr().out

    def integridad_invalida() -> list[dict[str, Any]]:
        raise ErrorIntegridadDatos("Archivo alterado")

    monkeypatch.setattr(app, "cargar_pacientes", integridad_invalida)
    app.comprobar_integridad_desde_menu()
    assert "Alerta de integridad" in capsys.readouterr().out

    def lectura_invalida() -> list[dict[str, Any]]:
        raise ErrorAlmacenamiento("No fue posible leer")

    monkeypatch.setattr(app, "cargar_pacientes", lectura_invalida)
    app.comprobar_integridad_desde_menu()
    assert "No fue posible realizar" in capsys.readouterr().out


def test_ejecutar_aplicacion_recorrer_menu(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    llamadas: list[str] = []
    opciones = iter(["0", "1", "2", "3", "4", "5"])
    monkeypatch.setattr(app, "cargar_pacientes", lambda: [])
    monkeypatch.setattr("builtins.input", lambda _mensaje: next(opciones))
    monkeypatch.setattr(
        app, "registrar_paciente", lambda _lista: llamadas.append("registrar")
    )
    monkeypatch.setattr(
        app, "buscar_paciente", lambda _lista: llamadas.append("buscar")
    )
    monkeypatch.setattr(
        app, "mostrar_reporte", lambda _lista: llamadas.append("reporte")
    )
    monkeypatch.setattr(
        app,
        "comprobar_integridad_desde_menu",
        lambda: llamadas.append("integridad"),
    )

    app.ejecutar_aplicacion()

    assert llamadas == ["registrar", "buscar", "reporte", "integridad"]
    salida = capsys.readouterr().out
    assert "Opción inválida" in salida
    assert "Aplicación finalizada" in salida


def test_ejecutar_aplicacion_controla_error_inicial(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def integridad_invalida() -> list[dict[str, Any]]:
        raise ErrorIntegridadDatos("Archivo alterado")

    monkeypatch.setattr(app, "cargar_pacientes", integridad_invalida)
    app.ejecutar_aplicacion()
    assert "ALERTA CRÍTICA" in capsys.readouterr().out

    def almacenamiento_invalido() -> list[dict[str, Any]]:
        raise ErrorAlmacenamiento("No fue posible leer")

    monkeypatch.setattr(app, "cargar_pacientes", almacenamiento_invalido)
    app.ejecutar_aplicacion()
    assert "No fue posible iniciar" in capsys.readouterr().out
