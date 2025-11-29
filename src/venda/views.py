from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import FormaPagamento, Venda, ItemVenda
from estoque.models import ItemEstoque
from .serializers import (
    AdicionarItemVendaSerializer,
    ItemVendaSerializer,
    VendaSerializer,
)

class VendaViewSet(viewsets.ModelViewSet):
    queryset = Venda.objects.all()
    serializer_class = VendaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Venda.objects.filter(usuario_id=self.request.user.id)

    def perform_create(self, serializer):
        usuario_id = self.request.user.id
        serializer.save(usuario_id=usuario_id)

    @action(detail=True, methods=["post"], serializer_class=AdicionarItemVendaSerializer)
    def adicionar_item(self, request, pk=None):
        venda = self.get_object()
        if venda.status != Venda.StatusVenda.ABERTA:
            return Response({"detail": "Venda fechada."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AdicionarItemVendaSerializer(data=request.data, context={"venda": venda})
        if serializer.is_valid():
            item = serializer.save()
            return Response(ItemVendaSerializer(item).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"], url_path='itens/(?P<item_pk>\\d+)/atualizar_quantidade')
    def atualizar_quantidade_item(self, request, pk=None, item_pk=None):
        venda = self.get_object()
        if venda.status != Venda.StatusVenda.ABERTA:
            return Response({"detail": "Venda fechada."}, status=status.HTTP_400_BAD_REQUEST)

        item_venda = get_object_or_404(ItemVenda, pk=item_pk, venda=venda)
        nova_quantidade = request.data.get("quantidade")

        if nova_quantidade is None:
            return Response({"detail": "Qtd obrigatória."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            nova_quantidade = float(nova_quantidade)
            if nova_quantidade <= 0:
                raise ValueError
        except ValueError:
             return Response({"detail": "Qtd deve ser maior que zero."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item_estoque = ItemEstoque.objects.get(filial=venda.filial, produto=item_venda.produto)
            if item_estoque.quantidade_atual < nova_quantidade:
                return Response({"detail": f"Estoque insuficiente. Disp: {item_estoque.quantidade_atual}"}, status=status.HTTP_400_BAD_REQUEST)
        except ItemEstoque.DoesNotExist:
             return Response({"detail": "Item não encontrado no estoque."}, status=status.HTTP_400_BAD_REQUEST)

        item_venda.quantidade_vendida = nova_quantidade
        item_venda.save()
        venda.calcular_valor_total()
        return Response(ItemVendaSerializer(item_venda).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def finalizar_venda(self, request, pk=None):
        venda = self.get_object()
        forma_str = request.data.get("forma_pagamento")
        try:
            forma_enum = FormaPagamento(forma_str)
            venda.finalizar_venda(forma=forma_enum)
        except (ValueError, Exception) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(VendaSerializer(venda).data, status=status.HTTP_200_OK)
    
    def remover_item_venda(self, request, pk=None, item_pk=None):
        venda = self.get_object()
        if venda.status != Venda.StatusVenda.ABERTA:
            return Response({"detail": "Venda fechada."}, status=status.HTTP_400_BAD_REQUEST)
        item_venda = get_object_or_404(ItemVenda, pk=item_pk, venda=venda)
        item_venda.delete()
        venda.calcular_valor_total()
        return Response(status=status.HTTP_204_NO_CONTENT)