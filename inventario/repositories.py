from abc import ABC, abstractmethod
from typing import Optional
from inventario.models import Herramienta

class IHerramientaRepository(ABC):
    @abstractmethod
    def buscar_por_codigo(self, codigo: str) -> Optional[Herramienta]:
        pass
    @abstractmethod
    def actualizar_estado(self, id_herramienta: int, estado: str) -> None:
        pass

class HerramientaRepositoryImpl(IHerramientaRepository):
    def buscar_por_codigo(self, codigo: str) -> Optional[Herramienta]:
        return Herramienta.objects.filter(codigo_barra=codigo).first()

    def actualizar_estado(self, id_herramienta: int, estado: str) -> None:
        Herramienta.objects.filter(id=id_herramienta).update(estado=estado)
