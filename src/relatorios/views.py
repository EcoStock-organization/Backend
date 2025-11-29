from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import models
from django.db.models import F, Sum, Q
from estoque.models import ItemEstoque
from produto.models import Produto
from filial.models import Filial
from .serializers import (
    DashboardGeralSerializer, 
    RelatorioEstoqueBaixoSerializer, 
    BuscaGlobalProdutoSerializer
)

class DashboardGeralView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DashboardGeralSerializer

    def get(self, request):
        total_produtos = Produto.objects.filter(esta_ativo=True).count()
        total_filiais = Filial.objects.filter(esta_ativa=True).count()
        
        valor_total_estoque = ItemEstoque.objects.aggregate(
            total=Sum(
                F('quantidade_atual') * F('preco_venda_atual'),
                output_field=models.DecimalField()
            )
        )['total'] or 0.00

        itens_baixo_estoque = ItemEstoque.objects.filter(
            quantidade_atual__lt=F('quantidade_minima_estoque')
        ).count()

        return Response({
            "total_produtos": total_produtos,
            "total_filiais": total_filiais,
            "valor_total_estoque": valor_total_estoque,
            "itens_baixo_estoque": itens_baixo_estoque
        })

class RelatorioEstoqueBaixoView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RelatorioEstoqueBaixoSerializer

    def get(self, request):
        itens = ItemEstoque.objects.filter(
            quantidade_atual__lt=F('quantidade_minima_estoque')
        ).select_related('produto', 'filial')

        dados = []
        for item in itens:
            dados.append({
                "produto": item.produto.nome,
                "filial": item.filial.nome,
                "quantidade_atual": item.quantidade_atual,
                "minimo": item.quantidade_minima_estoque
            })
        
        return Response(dados)

class BuscaGlobalProdutoView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BuscaGlobalProdutoSerializer

    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({"erro": "Informe o parâmetro 'q'"}, status=status.HTTP_400_BAD_REQUEST)

        # CORREÇÃO: Adicionado select_related('categoria')
        produtos = Produto.objects.filter(
            Q(nome__icontains=query) | Q(codigo_barras__icontains=query),
            esta_ativo=True
        ).select_related('categoria')

        resultados = []
        for produto in produtos:
            itens = ItemEstoque.objects.filter(produto=produto).select_related('filial')
            locais = []
            for item in itens:
                locais.append({
                    "filial": item.filial.nome,
                    "quantidade": item.quantidade_atual,
                    "preco": item.preco_venda_atual
                })
            
            resultados.append({
                "id": produto.id,
                "nome": produto.nome,
                "codigo_barras": produto.codigo_barras,
                # CORREÇÃO: Retornando o nome real da categoria
                "categoria": produto.categoria.nome if produto.categoria else "Sem Categoria",
                "disponibilidade": locais
            })

        return Response(resultados)