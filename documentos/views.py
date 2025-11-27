from django.shortcuts import render

def lista_documentos(request):
    return render(request, 'documentos/lista_documentos.html')

def subir_documento_general(request):
    return render(request, 'documentos/subir_documento.html')

def subir_documento_caso(request, caso_id):
    return render(request, 'documentos/subir_documento.html')
