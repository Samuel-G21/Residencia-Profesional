"""
Utilidades de seguridad y robustez compartidas por los controladores.
"""
import os
import re
import time
import logging
import contextlib

from flask import jsonify
from jinja2.sandbox import SandboxedEnvironment

logger = logging.getLogger(__name__)

OUTPUTS_DIR = 'outputs'
TEMPLATES_DIR = 'templates'

# Los IDs de evento se usan como nombre de carpeta en disco y como PK (String(50)).
# Solo se permiten caracteres seguros: evita path traversal ("..", "/", "\\") y nombres raros.
_ID_EVENTO_RE = re.compile(r'^[A-Za-z0-9_-]{1,50}$')

ALLOWED_TEMPLATE_EXTENSIONS = ('.docx', '.xlsx', '.xlsm', '.xls')

# Entorno Jinja con sandbox: las plantillas pueden ser subidas por usuarios, por lo que
# un Environment normal permitiría ejecución remota de código (SSTI) vía {{ ''.__class__... }}.
SANDBOX_ENV = SandboxedEnvironment()

# Fases válidas del flujo de trabajo (ver frontend: Registro .. Cierre).
MIN_FASE = 1
MAX_FASE = 5

# Escala de calificaciones (las estadísticas consideran aprobado >= 8).
MIN_CALIFICACION = 0.0
MAX_CALIFICACION = 10.0

ESTADOS_CERRADOS = ('FINALIZADO', 'CANCELADO')


def is_valid_id_evento(id_evento):
    return isinstance(id_evento, str) and bool(_ID_EVENTO_RE.match(id_evento))


def event_dir(id_evento, create=False):
    """Ruta de la carpeta de salida de un evento. Lanza ValueError si el ID no es seguro."""
    id_ev = str(id_evento).strip()
    if not is_valid_id_evento(id_ev):
        raise ValueError("ID de evento inválido")
    base = os.path.abspath(OUTPUTS_DIR)
    path = os.path.abspath(os.path.join(base, id_ev))
    if os.path.dirname(path) != base:
        raise ValueError("ID de evento inválido")
    if create:
        os.makedirs(path, exist_ok=True)
    return path


def render_template_string(text, context):
    """Renderiza un texto Jinja (celdas de Excel) dentro del sandbox."""
    return SANDBOX_ENV.from_string(text).render(context)


def safe_template_filename(filename):
    """
    Valida el nombre de una plantilla subida. Se conserva el nombre original (con acentos),
    porque el motor busca plantillas por nombre exacto, pero se rechaza cualquier intento
    de escribir fuera de la carpeta templates/.
    """
    if not filename or not isinstance(filename, str):
        return None
    name = filename.strip()
    if name != os.path.basename(name) or '/' in name or '\\' in name or '..' in name:
        return None
    if name.startswith('.') or len(name) > 150:
        return None
    if any(ord(ch) < 32 for ch in name) or any(ch in name for ch in '<>:"|?*'):
        return None
    if not name.lower().endswith(ALLOWED_TEMPLATE_EXTENSIONS):
        return None
    return name


def has_extension(filename, *extensions):
    return bool(filename) and filename.lower().endswith(tuple(e.lower() for e in extensions))


def error_response(message, status=500, exc=None):
    """Respuesta de error genérica. El detalle técnico solo va al log, nunca al cliente."""
    if exc is not None:
        logger.exception("%s: %s", message, exc)
    return jsonify({"status": "error", "message": message}), status


def parse_calificacion(value):
    """Convierte a float validando rango y descartando NaN/inf. Devuelve None si no es válida."""
    if value is None or isinstance(value, bool):
        return None
    try:
        num = float(str(value).strip().replace(',', '.'))
    except (TypeError, ValueError):
        return None
    if num != num or num in (float('inf'), float('-inf')):
        return None
    if num < MIN_CALIFICACION or num > MAX_CALIFICACION:
        return None
    return round(num, 2)


def normalize_ficha(value):
    """'12345.0' -> '12345'. No usa str.replace('.0', '') que corrompía valores como '1.05'."""
    if value is None:
        return ''
    if isinstance(value, float):
        if value != value:
            return ''
        if value.is_integer():
            return str(int(value))
    text = str(value).strip()
    if re.fullmatch(r'\d+\.0+', text):
        text = text.split('.')[0]
    return text


class EventBusyError(Exception):
    pass


_LOCK_STALE_SECONDS = 15 * 60


@contextlib.contextmanager
def event_lock(id_evento):
    """
    Bloqueo exclusivo por evento entre procesos (gunicorn usa varios workers).
    Evita que dos generaciones/descargas simultáneas borren o mezclen archivos del mismo evento.
    """
    id_ev = str(id_evento).strip()
    if not is_valid_id_evento(id_ev):
        raise ValueError("ID de evento inválido")
    lock_dir = os.path.abspath(os.path.join(OUTPUTS_DIR, '.locks'))
    os.makedirs(lock_dir, exist_ok=True)
    lock_path = os.path.join(lock_dir, f"{id_ev}.lock")

    fd = None
    for attempt in range(2):
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            try:
                age = time.time() - os.path.getmtime(lock_path)
            except OSError:
                age = 0
            if attempt == 0 and age > _LOCK_STALE_SECONDS:
                # Lock huérfano (proceso muerto): se libera y se reintenta una vez.
                with contextlib.suppress(OSError):
                    os.remove(lock_path)
                continue
            raise EventBusyError(id_ev)
    if fd is None:
        raise EventBusyError(id_ev)
    try:
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        yield
    finally:
        with contextlib.suppress(OSError):
            os.remove(lock_path)


def busy_response():
    return jsonify({
        "status": "error",
        "message": "El evento está siendo procesado por otra operación. Intenta de nuevo en unos momentos."
    }), 409
