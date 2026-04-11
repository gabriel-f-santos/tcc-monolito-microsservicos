from src.infrastructure.repositories.inmemory_item_estoque_repository import InMemoryItemEstoqueRepository
from src.infrastructure.repositories.inmemory_movimentacao_repository import InMemoryMovimentacaoRepository
from src.application.use_cases.registrar_entrada import RegistrarEntradaUseCase
from src.application.use_cases.registrar_saida import RegistrarSaidaUseCase
from src.application.use_cases.buscar_item import BuscarItemUseCase
from src.application.use_cases.listar_itens import ListarItensUseCase
from src.application.use_cases.listar_movimentacoes import ListarMovimentacoesUseCase


class Container:
    def __init__(self) -> None:
        self.item_repo = InMemoryItemEstoqueRepository()
        self.mov_repo = InMemoryMovimentacaoRepository()

    def registrar_entrada_use_case(self) -> RegistrarEntradaUseCase:
        return RegistrarEntradaUseCase(self.item_repo, self.mov_repo)

    def registrar_saida_use_case(self) -> RegistrarSaidaUseCase:
        return RegistrarSaidaUseCase(self.item_repo, self.mov_repo)

    def buscar_item_use_case(self) -> BuscarItemUseCase:
        return BuscarItemUseCase(self.item_repo)

    def listar_itens_use_case(self) -> ListarItensUseCase:
        return ListarItensUseCase(self.item_repo)

    def listar_movimentacoes_use_case(self) -> ListarMovimentacoesUseCase:
        return ListarMovimentacoesUseCase(self.item_repo, self.mov_repo)


container = Container()
