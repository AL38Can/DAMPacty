from datetime import datetime

def formatear_fecha(fecha_iso):
    """Convierte una fecha en formato ISO a un formato más legible."""
    try:
        fecha = datetime.strptime(fecha_iso, "%Y-%m-%d")
        return fecha.strftime("%d de %B de %Y")
    except ValueError:
        return fecha_iso