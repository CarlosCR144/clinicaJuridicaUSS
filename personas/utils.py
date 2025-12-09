from .models import AuditLog

def log_action(user, accion, modelo, registro_id, detalle=''):
    if user.is_authenticated:
        AuditLog.objects.create(
            usuario=user,
            accion=accion,
            modelo=modelo,
            registro_id=str(registro_id),
            detalle=detalle
        )
