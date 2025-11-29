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
    """
    View simplificada. A lógica de criação (Auth + DB Local) 
    está inteiramente encapsulada no UsuarioCompletoSerializer.
    """
    queryset = PerfilUsuario.objects.all()
    serializer_class = UsuarioCompletoSerializer
    permission_classes = [IsAuthenticated] # Ou [IsLocalAdmin] se apenas admin puder criar

# --- CORREÇÃO AQUI ---
# Mudamos de RetrieveDestroyAPIView para RetrieveUpdateDestroyAPIView
class DetalheUsuarioView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PerfilUsuario.objects.all()
    serializer_class = UsuarioCompletoSerializer
    permission_classes = [IsLocalAdmin]

    def perform_destroy(self, instance):
        # Tenta deletar no Auth Service ao deletar localmente
        try:
            AuthService.deletar_usuario_auth(instance.usuario_id_auth)
        except Exception:
            # Logar erro se necessário, mas não impedir a deleção local
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