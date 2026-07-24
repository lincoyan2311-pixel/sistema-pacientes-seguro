"""Aplicación educativa de consola para registrar pacientes ficticios."""

from datetime import datetime, timezone
from typing import Any

from almacenamiento import (
    ErrorAlmacenamiento,
    ErrorIntegridadDatos,
    cargar_pacientes,
    guardar_pacientes,
)
from privacidad import crear_vista_anonimizada, generar_id_paciente
from validaciones import sanitizar_estructura_paciente


def mostrar_encabezado() -> None:
    """Muestra el título del programa."""
    print("\n" + "=" * 62)
    print(" SISTEMA SEGURO DE REGISTRO DE PACIENTES")
    print(" Aplicación educativa: no utilizar datos reales")
    print("=" * 62)


def mostrar_menu() -> None:
    """Muestra las opciones disponibles."""
    print("\nMENÚ PRINCIPAL")
    print("1. Registrar paciente")
    print("2. Buscar paciente por identificador")
    print("3. Mostrar reporte anonimizado")
    print("4. Verificar integridad de los datos")
    print("5. Salir")


def solicitar_datos_paciente() -> dict[str, str]:
    """Solicita por teclado los datos todavía no validados."""
    print("\nREGISTRO DE PACIENTE")
    print("-" * 62)
    return {
        "nombre": input("Nombre completo: "),
        "rut": input("RUT: "),
        "edad": input("Edad: "),
        "correo": input("Correo electrónico: "),
        "diagnostico": input("Diagnóstico general de demostración: "),
    }


def existe_rut(pacientes: list[dict[str, Any]], rut: str) -> bool:
    """Comprueba si un RUT ya está registrado."""
    return any(paciente.get("rut") == rut for paciente in pacientes)


def existe_identificador(
    pacientes: list[dict[str, Any]], identificador: str
) -> bool:
    """Comprueba si un identificador ya existe."""
    return any(
        paciente.get("id_paciente") == identificador for paciente in pacientes
    )


def crear_identificador_unico(pacientes: list[dict[str, Any]]) -> str:
    """Genera un ID y evita colisiones en la lista actual."""
    for _ in range(10):
        identificador = generar_id_paciente()
        if not existe_identificador(pacientes, identificador):
            return identificador
    raise RuntimeError("No fue posible generar un identificador único.")


def registrar_paciente(pacientes: list[dict[str, Any]]) -> None:
    """Registra un paciente después de validar todos sus datos."""
    datos_originales = solicitar_datos_paciente()
    try:
        datos_seguros = sanitizar_estructura_paciente(datos_originales)
        if existe_rut(pacientes, datos_seguros["rut"]):
            print("\nNo se realizó el registro.")
            print("Ya existe un paciente con ese RUT.")
            return

        identificador = crear_identificador_unico(pacientes)
        paciente = {
            "id_paciente": identificador,
            **datos_seguros,
            "fecha_registro": datetime.now(timezone.utc).isoformat(),
        }
        pacientes.append(paciente)
        try:
            guardar_pacientes(pacientes)
        except ErrorAlmacenamiento:
            pacientes.pop()
            raise

        print("\nPaciente registrado correctamente.")
        print(f"Identificador asignado: {identificador}")
        print("Guarde el identificador para realizar búsquedas posteriores.")
    except ValueError as error:
        print(f"\nDatos rechazados: {error}")
    except ErrorAlmacenamiento as error:
        print(f"\nNo fue posible guardar el paciente: {error}")
    except RuntimeError as error:
        print(f"\nError al generar el identificador: {error}")


def normalizar_identificador(identificador: str) -> str:
    """Limpia y valida superficialmente el identificador."""
    identificador = identificador.strip().upper()
    if not identificador.startswith("PAC-"):
        raise ValueError("El identificador debe comenzar con PAC-.")
    if len(identificador) < 12 or len(identificador) > 36:
        raise ValueError("La longitud del identificador no es válida.")
    caracteres_validos = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-")
    if any(caracter not in caracteres_validos for caracter in identificador):
        raise ValueError("El identificador contiene caracteres inválidos.")
    return identificador


def buscar_paciente(pacientes: list[dict[str, Any]]) -> None:
    """Busca por ID y muestra solamente la vista anonimizada."""
    entrada = input("\nIngrese el identificador del paciente: ")
    try:
        identificador = normalizar_identificador(entrada)
    except ValueError as error:
        print(f"\nIdentificador rechazado: {error}")
        return

    paciente_encontrado = next(
        (
            paciente
            for paciente in pacientes
            if paciente.get("id_paciente") == identificador
        ),
        None,
    )
    if paciente_encontrado is None:
        print("\nNo se encontró un paciente con ese identificador.")
        return
    print("\nPACIENTE ENCONTRADO")
    print("-" * 62)
    imprimir_paciente_anonimizado(crear_vista_anonimizada(paciente_encontrado))


def imprimir_paciente_anonimizado(paciente: dict[str, object]) -> None:
    """Imprime solamente los datos autorizados para el reporte."""
    print(f"ID: {paciente.get('id_paciente', 'NO DISPONIBLE')}")
    print(f"Nombre: {paciente.get('nombre', 'NO DISPONIBLE')}")
    print(f"RUT: {paciente.get('rut', 'NO DISPONIBLE')}")
    print(f"Edad: {paciente.get('edad', 'NO DISPONIBLE')}")
    print(f"Correo: {paciente.get('correo', 'NO DISPONIBLE')}")
    print(
        "Fecha de registro: "
        f"{paciente.get('fecha_registro', 'NO DISPONIBLE')}"
    )


def mostrar_reporte(pacientes: list[dict[str, Any]]) -> None:
    """Muestra todos los pacientes en formato anonimizado."""
    print("\nREPORTE ANONIMIZADO")
    print("=" * 62)
    if not pacientes:
        print("No existen pacientes registrados.")
        return
    for numero, paciente in enumerate(pacientes, start=1):
        print(f"\nPaciente número {numero}")
        print("-" * 62)
        imprimir_paciente_anonimizado(crear_vista_anonimizada(paciente))


def comprobar_integridad_desde_menu() -> None:
    """Permite verificar la integridad desde el menú."""
    try:
        cargar_pacientes()
        print("\nLa integridad de los datos es correcta.")
    except ErrorIntegridadDatos as error:
        print(f"\nAlerta de integridad: {error}")
    except ErrorAlmacenamiento as error:
        print(f"\nNo fue posible realizar la revisión: {error}")


def ejecutar_aplicacion() -> None:
    """Controla el ciclo principal de la aplicación."""
    mostrar_encabezado()
    try:
        pacientes = cargar_pacientes()
    except ErrorIntegridadDatos as error:
        print("\nALERTA CRÍTICA")
        print(error)
        print(
            "La aplicación se cerrará para evitar trabajar "
            "con datos posiblemente alterados."
        )
        return
    except ErrorAlmacenamiento as error:
        print("\nNo fue posible iniciar el sistema.")
        print(error)
        return

    while True:
        mostrar_menu()
        opcion = input("\nSeleccione una opción: ").strip()
        if opcion == "1":
            registrar_paciente(pacientes)
        elif opcion == "2":
            buscar_paciente(pacientes)
        elif opcion == "3":
            mostrar_reporte(pacientes)
        elif opcion == "4":
            comprobar_integridad_desde_menu()
        elif opcion == "5":
            print("\nAplicación finalizada correctamente.")
            break
        else:
            print("\nOpción inválida. Debe seleccionar un número entre 1 y 5.")


if __name__ == "__main__":
    ejecutar_aplicacion()
