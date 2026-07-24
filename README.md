# Sistema seguro de registro de pacientes

Proyecto educativo de consola desarrollado en Python. Permite registrar pacientes
ficticios, validar sus datos, generar un identificador seudónimo, mostrar un reporte
anonimizado y detectar modificaciones del archivo JSON con SHA-256.

> Advertencia: no usar con información clínica real. El ejercicio no tiene cifrado,
> autenticación, roles ni otros controles necesarios para producción.

## Cómo ejecutar

1. Crear el entorno: `python -m venv venv`
2. Activarlo en PowerShell: `.\venv\Scripts\Activate.ps1`
3. Instalar herramientas: `python -m pip install -r requirements-dev.txt`
4. Iniciar: `python app.py`

## Verificación

- Pruebas: `python -m pytest -v`
- Cobertura: `python -m pytest --cov=. --cov-report=term-missing --cov-report=xml`
- Bandit: `python -m bandit -r . -x ./venv,./.venv,./tests -f json -o reporte-bandit.json`

La configuración de SonarQube está en `sonar-project.properties`. Para ejecutarlo se
necesita Docker Desktop, una instancia local de SonarQube y un token guardado como
variable de entorno. El token nunca debe escribirse dentro del proyecto.

## Resultados verificados

- 25 pruebas aprobadas.
- 59 % de cobertura total.
- Bandit: 0 hallazgos en 470 líneas revisadas.
- Integridad: se detectó correctamente una modificación manual del JSON.
- SonarQube: configuración preparada, pero análisis pendiente porque el equipo de
  verificación no tenía Docker instalado.

Antes de entregar, completar los datos personales de la portada del informe y revisar
el archivo `ANTES_DE_ENTREGAR.md`.

## Archivos principales

- `app.py`: menú y flujo del programa.
- `validaciones.py`: validación y sanitización.
- `privacidad.py`: anonimización y seudonimización.
- `almacenamiento.py`: JSON, escritura atómica y hash SHA-256.
- `tests/`: pruebas automatizadas.
- `informe.pdf`: desarrollo escrito y evidencias del trabajo.
