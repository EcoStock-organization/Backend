from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import UsuarioCompletoSerializer
from .models import PerfilUsuario

class CriarUsuarioView(generics.CreateAPIView):
    queryset = PerfilUsuario.objects.all()
    serializer_class = UsuarioCompletoSerializer
    permission_classes = [IsAuthenticated]
