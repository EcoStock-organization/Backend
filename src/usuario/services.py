import requests
from rest_framework.exceptions import APIException
import os


AUTH_SERVICE_URL = "http://auth-backend:8000/api"

class AuthService:
    @staticmethod
    def criar_usuario_auth(username, email, password):
        url = f"{AUTH_SERVICE_URL}/users/"
        
        try:
            response = requests.post(url, json={
                "username": username,
                "email": email,
                "password": password
            })
            
            if response.status_code == 201:
                return response.json()
            else:
                raise APIException(detail=f"Erro no serviço de Auth: {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise APIException(detail=f"Falha de conexão com serviço de Auth: {str(e)}")
        
    @staticmethod
    def deletar_usuario_auth(usuario_id_auth):
        url = f"{AUTH_SERVICE_URL}/users/{usuario_id_auth}/"
        
        try:            
            response = requests.delete(url)
            
            if response.status_code == 204:
                return True
            elif response.status_code == 404:
                return True
            else:
                raise APIException(detail=f"Erro ao deletar no Auth: {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise APIException(detail=f"Falha de conexão com Auth: {str(e)}")
        
    @staticmethod
    def atualizar_usuario_auth(usuario_id_auth, data):
        url = f"{AUTH_SERVICE_URL}/users/{usuario_id_auth}/"
        
        payload = {}
        if 'username' in data: payload['username'] = data['username']
        if 'email' in data: payload['email'] = data['email']
        if 'password' in data: payload['password'] = data['password']
        if 'is_active' in data: payload['is_active'] = data['is_active']

        if not payload:
            return True

        try:
            response = requests.patch(url, json=payload)

            if response.status_code == 200:
                return response.json()
            
            if response.status_code == 400:
                try:
                    erro_msg = response.json()
                except:
                    erro_msg = response.text
                raise ValidationError(detail=erro_msg)
            
            raise APIException(detail=f"Erro ao atualizar no Auth: {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise APIException(detail=f"Falha de conexão com Auth: {str(e)}")
