from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import VendaViewSet

app_name = "venda"

router = DefaultRouter()
router.register(r"", VendaViewSet, basename="venda")

urlpatterns = [
    path("", include(router.urls)),
    path('<int:pk>/itens/<int:item_pk>/', VendaViewSet.as_view({'delete': 'remover_item_venda'}), name='remover-item-venda'),
]
