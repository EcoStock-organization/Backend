from rest_framework import serializers
from .models import PerfilUsuario
from .services import AuthService

class UsuarioCompletoSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = PerfilUsuario
        fields = ['id', 'nome_completo', 'cpf', 'cargo', 'filial', 'ativo', 'username', 'password', 'email', 'usuario_id_auth']
        read_only_fields = ['usuario_id_auth']

    def create(self, validated_data):
        username = validated_data.pop('username', None)
        password = validated_data.pop('password', None)
        email = validated_data.get('email', None)

        if not username or not password or not email:
             raise serializers.ValidationError("Username, senha e email são obrigatórios para criação.")

        auth_data = {
            'username': username,
            'password': password,
            'email': email
        }
        
        user_auth = AuthService.criar_usuario_auth(**auth_data)
        validated_data['usuario_id_auth'] = user_auth['id']
        
        perfil = PerfilUsuario.objects.create(**validated_data)
        return perfil

    def update(self, instance, validated_data):
        auth_data = {}
        
        if 'email' in validated_data:
            auth_data['email'] = validated_data['email']
            auth_data['username'] = validated_data['email']

        if 'password' in validated_data:
            auth_data['password'] = validated_data.pop('password')
        
        if 'ativo' in validated_data:
            auth_data['is_active'] = validated_data['ativo']

        if auth_data:
            try:
                AuthService.atualizar_usuario_auth(instance.usuario_id_auth, auth_data)
            except Exception as e:
                print(f"Aviso: Erro ao atualizar Auth: {e}")

        return super().update(instance, validated_data)
