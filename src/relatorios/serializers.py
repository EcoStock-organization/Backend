from rest_framework import serializers


class DashboardGeralSerializer(serializers.Serializer):
    total_produtos = serializers.IntegerField()
    total_filiais = serializers.IntegerField()
    valor_total_estoque = serializers.DecimalField(max_digits=20, decimal_places=2)
    itens_baixo_estoque = serializers.IntegerField()


class RelatorioEstoqueBaixoSerializer(serializers.Serializer):
    produto = serializers.CharField(help_text="Nome do Produto")
    filial = serializers.CharField(help_text="Nome da Filial")
    quantidade_atual = serializers.FloatField()
    minimo = serializers.FloatField(help_text="Quantidade Mínima Configurada")


class DisponibilidadeFilialSerializer(serializers.Serializer):
    filial = serializers.CharField()
    quantidade = serializers.FloatField()
    preco = serializers.DecimalField(max_digits=10, decimal_places=2)


class BuscaGlobalProdutoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nome = serializers.CharField()
    codigo_barras = serializers.CharField()
    categoria = serializers.CharField()
    disponibilidade = DisponibilidadeFilialSerializer(many=True)
