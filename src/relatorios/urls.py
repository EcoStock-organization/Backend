from django.urls import path
from .views import DashboardGeralView, RelatorioEstoqueBaixoView, BuscaGlobalProdutoView


urlpatterns = [
    path('dashboard/', DashboardGeralView.as_view(), name='dashboard-kpis'),
    path('estoque-baixo/', RelatorioEstoqueBaixoView.as_view(), name='relatorio-estoque-baixo'),
    path('busca-global/', BuscaGlobalProdutoView.as_view(), name='busca-global'),
]
