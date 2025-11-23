from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from produto.models import Produto
from filial.models import Filial
from estoque.models import ItemEstoque


class TestesRelatorios(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testerelatorio', password='123')
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        self.prod1 = Produto.objects.create(codigo_barras="111", nome="Prod Normal", tipo_produto='UNITARIO')
        self.prod2 = Produto.objects.create(codigo_barras="222", nome="Prod Baixo Est", tipo_produto='UNITARIO')
        
        self.filial = Filial.objects.create(nome="Filial Relatorio", cep="000", cidade="BSB", estado="DF")
        
        ItemEstoque.objects.create(
            filial=self.filial, produto=self.prod1,
            quantidade_atual=100, preco_venda_atual=10.00, quantidade_minima_estoque=10
        )
        ItemEstoque.objects.create(
            filial=self.filial, produto=self.prod2,
            quantidade_atual=5, preco_venda_atual=20.00, quantidade_minima_estoque=10
        )

    def test_dashboard_kpis(self):
        url = reverse('dashboard-kpis')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        self.assertEqual(data['total_produtos'], 2)
        self.assertEqual(data['total_filiais'], 1)
        self.assertEqual(data['itens_baixo_estoque'], 1)
        
        self.assertEqual(float(data['valor_total_estoque']), 1100.00)

    def test_relatorio_estoque_baixo(self):
        url = reverse('relatorio-estoque-baixo')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['produto'], "Prod Baixo Est")

    def test_busca_global(self):
        url = reverse('busca-global') + "?q=Normal"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['disponibilidade'][0]['filial'], "Filial Relatorio")
