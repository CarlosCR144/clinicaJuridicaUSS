import os
from django.template.loader import get_template
from django.utils import timezone
from django.core.files.base import ContentFile
from xhtml2pdf import pisa
from io import BytesIO

def generar_pdf_expediente(registro):
    try:
        # 1. Preparar Contexto
        context = {
            'caso': registro.causa,
            'registro': registro,
            'fecha_impresion': timezone.now(),
            'usuario_impresion': registro.actualizado_por, # O el responsable
            'logo_url': 'https://cdn.uss.cl/content/uploads/2025/10/22175624/USShorizontal-tagline-ilumina-dark.svg'
        }

        # 2. Renderizar Template
        template = get_template('casos/pdf_expediente.html')
        html = template.render(context)

        # 3. Generar PDF en memoria
        buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=buffer)

        if pisa_status.err:
            return False

        # 4. Guardar el archivo en el modelo
        filename = f"Expediente_{registro.causa.rol_rit}.pdf"
        
        if registro.archivo:
            try:
                # Verificamos si el archivo físico existe en el disco y lo borramos
                if os.path.isfile(registro.archivo.path):
                    os.remove(registro.archivo.path)
            except Exception as e:
                # Si falla el borrado (ej: archivo en uso), solo imprimimos error pero seguimos
                print(f"No se pudo borrar el archivo anterior: {e}")

        # B) Guardamos el nuevo (Como ya borramos el viejo, Django usará el nombre limpio)
        registro.archivo.save(filename, ContentFile(buffer.getvalue()), save=True)
        
        return True

    except Exception as e:
        print(f"Error generando PDF: {e}")
        return False