from django.urls import path
from .views import CriarUsuarioView, DetalheUsuarioView


app_name = 'usuario'

urlpatterns = [
    path('criar/', CriarUsuarioView.as_view(), name='criar-usuario'),
    path('<int:pk>/', DetalheUsuarioView.as_view(), name='detalhe-usuario'),
]
