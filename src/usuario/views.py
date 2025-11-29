from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from .models import PerfilUsuario
from .serializers import UsuarioCompletoSerializer
from .services import AuthService

class IsLocalAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            perfil = PerfilUsuario.objects.get(usuario_id_auth=request.user.id)
            return perfil.cargo == PerfilUsuario.Cargo.ADMIN
        except PerfilUsuario.DoesNotExist:
            return False

class CriarUsuarioView(generics.CreateAPIView):
    queryset = PerfilUsuario.objects.all()
    serializer_class = UsuarioCompletoSerializer
    permission_classes = [IsAuthenticated]

class DetalheUsuarioView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PerfilUsuario.objects.all()
    serializer_class = UsuarioCompletoSerializer
    permission_classes = [IsLocalAdmin]

    def perform_destroy(self, instance):
        try:
            AuthService.deletar_usuario_auth(instance.usuario_id_auth)
        except Exception:
            pass
        instance.delete()

class ListaUsuarioView(generics.ListAPIView):
    serializer_class = UsuarioCompletoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = PerfilUsuario.objects.all()
        auth_id = self.request.query_params.get('usuario_id_auth')
        if auth_id:
            return queryset.filter(usuario_id_auth=auth_id)
        return queryset