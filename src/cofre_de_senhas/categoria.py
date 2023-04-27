from typing import Self, TypeGuard
from dataclasses import dataclass, replace
from .bd import cf
from .cofre_enum import *
from .dao import *
from .dao_impl import *
from .service import *

cdao = CategoriaDAOImpl(cf)

@dataclass(frozen = True)
class Categoria:
    pk_categoria: int
    nome: str

    def renomear(self, novo_nome: str) -> Categoria:
        Categoria.nao_existente_por_nome(novo_nome)
        return replace(self, nome = novo_nome).__salvar()

    def excluir(self) -> Self:
        cdao.deletar_por_pk(self.pk)
        return self

    def __salvar(self) -> Self:
        cdao.salvar(self.__down)
        return self

    @property
    def chave(self) -> CategoriaChave:
        return CategoriaChave(self.pk_categoria)

    @property
    def pk(self) -> CategoriaPK:
        return CategoriaPK(self.pk_categoria)

    @property
    def up(self) -> CategoriaComChave:
        return CategoriaComChave(self.chave, self.nome)

    @property
    def __down(self) -> DadosCategoria:
        return DadosCategoria(self.pk_categoria, self.nome)

    @staticmethod
    def __promote(dados: DadosCategoria) -> Categoria:
        return Categoria(dados.pk_categoria, dados.nome)

    @staticmethod
    def encontrar_por_chave(chave: CategoriaChave) -> Categoria | None:
        dados: DadosCategoria | None = cdao.buscar_por_pk(CategoriaPK(chave.valor))
        if dados is None: return None
        return Categoria.__promote(dados)

    @staticmethod
    def encontrar_existente_por_chave(chave: CategoriaChave) -> Categoria:
        encontrado: Categoria | None = Categoria.encontrar_por_chave(chave)
        if encontrado is None: raise CategoriaNaoExisteException()
        return encontrado

    @staticmethod
    def encontrar_por_nome(nome: str) -> Categoria | None:
        dados: DadosCategoria | None = cdao.buscar_por_nome(nome)
        if dados is None: return None
        return Categoria.__promote(dados)

    @staticmethod
    def encontrar_existente_por_nome(nome: str) -> Categoria:
        encontrado: Categoria | None = Categoria.encontrar_por_nome(nome)
        if encontrado is None: raise CategoriaNaoExisteException()
        return encontrado

    @staticmethod
    def nao_existente_por_nome(nome: str) -> None:
        talvez: Categoria | None = Categoria.encontrar_por_nome(nome)
        if talvez is not None: raise CategoriaJaExisteException()

    @staticmethod
    def criar(nome: str) -> Categoria:
        Categoria.nao_existente_por_nome(nome)
        pk: CategoriaPK = cdao.criar(DadosCategoriaSemPK(nome))
        return Categoria(pk.pk_categoria, nome)

    @staticmethod
    def listar() -> list[Categoria]:
        return [Categoria.__promote(c) for c in cdao.listar()]

    @staticmethod
    def listar_por_segredo(pk: SegredoPK) -> list[Categoria]:
        return [Categoria.__promote(c) for c in cdao.listar_por_segredo(pk)]

    @staticmethod
    def listar_por_nomes(nomes: set[str]) -> dict[str, Categoria]:
        def filtragem(p: str) -> TypeGuard[tuple[str, Categoria]]:
            return p in nomes
        categorias: dict[str, Categoria] = {categoria.nome: categoria for categoria in Categoria.listar()}
        return dict(filter(filtragem, categorias))