from .fixtures import *
from connection.conn import IntegrityViolationException
from cofre_de_senhas.dao import CategoriaDAO, CategoriaPK, DadosCategoria, DadosCategoriaSemPK, SegredoPK, NomeCategoria
from cofre_de_senhas.bd.raiz import Raiz
from cofre_de_senhas.categoria.categoria_dao_impl import CategoriaDAOImpl
from pytest import raises

@db.decorator
def test_instanciar() -> None:
    s: CategoriaDAO = CategoriaDAOImpl()
    assert s == CategoriaDAO.instance()

@db.transacted
def test_criar_categoria() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    dados: DadosCategoriaSemPK = dados_millenium_falcon
    pk: CategoriaPK = dao.criar(dados)
    assert pk.pk_categoria == millenium_falcon.pk_categoria

@db.transacted
def test_ler_categoria_por_pk() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    pk: CategoriaPK = CategoriaPK(producao.pk_categoria)
    lido: DadosCategoria | None = dao.buscar_por_pk(pk)
    assert lido == producao

@db.transacted
def test_ler_categoria_por_nome() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    lido: DadosCategoria | None = dao.buscar_por_nome(nome_producao)
    assert lido == producao

@db.transacted
def test_criar_e_ler_categoria() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    dados: DadosCategoriaSemPK = dados_millenium_falcon
    pk: CategoriaPK = dao.criar(dados)
    assert pk.pk_categoria == millenium_falcon.pk_categoria

    lido1: DadosCategoria | None = dao.buscar_por_pk(pk)
    lido2: DadosCategoria | None = dao.buscar_por_nome(nome_millenium_falcon)

    assert lido1 == millenium_falcon
    assert lido2 == millenium_falcon
    assert lido1 is not lido2
    assert lido1 is not millenium_falcon
    assert lido2 is not millenium_falcon

@db.transacted
def test_ler_categoria_por_pk_nao_existe() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    lido: DadosCategoria | None = dao.buscar_por_pk(CategoriaPK(lixo3))
    assert lido is None

@db.transacted
def test_ler_categoria_por_nome_nao_existe() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    lido: DadosCategoria | None = dao.buscar_por_nome(nome_nao_existe)
    assert lido is None

@db.transacted
def test_listar_categorias_por_pk() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    pk1: CategoriaPK = CategoriaPK(api.pk_categoria)
    pk2: CategoriaPK = CategoriaPK(producao.pk_categoria)
    pk3: CategoriaPK = CategoriaPK(homologacao.pk_categoria)
    lido: list[DadosCategoria] = dao.listar_por_pks([pk1, pk2, pk3])
    assert lido == parte_categorias

@db.transacted
def test_listar_categorias_por_pk_nao_existem() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    pk1: CategoriaPK = CategoriaPK(lixo2)
    pk2: CategoriaPK = CategoriaPK(lixo1)
    pk3: CategoriaPK = CategoriaPK(lixo3)
    lido: list[DadosCategoria] = dao.listar_por_pks([pk1, pk2, pk3])
    assert lido == []

@db.transacted
def test_listar_categorias_por_pk_alguns_existem() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    pk1: CategoriaPK = CategoriaPK(lixo3)
    pk2: CategoriaPK = CategoriaPK(api.pk_categoria)
    pk3: CategoriaPK = CategoriaPK(lixo2)
    pk4: CategoriaPK = CategoriaPK(homologacao.pk_categoria)
    pk5: CategoriaPK = CategoriaPK(producao.pk_categoria)
    pk6: CategoriaPK = CategoriaPK(lixo1)
    lido: list[DadosCategoria] = dao.listar_por_pks([pk1, pk2, pk3, pk4, pk5, pk6])
    assert lido == parte_categorias

@db.transacted
def test_listar_categorias_por_nome() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    n1: NomeCategoria = NomeCategoria("Homologação")
    n2: NomeCategoria = NomeCategoria("API")
    n3: NomeCategoria = NomeCategoria("Produção")
    lido: list[DadosCategoria] = dao.listar_por_nomes([n1, n2, n3])
    assert lido == parte_categorias

@db.transacted
def test_listar_categorias_por_nome_nao_existem() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    n1: NomeCategoria = NomeCategoria("Melancia")
    n2: NomeCategoria = NomeCategoria("Cachorro")
    n3: NomeCategoria = NomeCategoria("Elefante")
    lido: list[DadosCategoria] = dao.listar_por_nomes([n1, n2, n3])
    assert lido == []

@db.transacted
def test_listar_categorias_por_nome_alguns_existem() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    n1: NomeCategoria = NomeCategoria("Homologação")
    n2: NomeCategoria = NomeCategoria("Melancia")
    n3: NomeCategoria = NomeCategoria("API")
    n4: NomeCategoria = NomeCategoria("Produção")
    n5: NomeCategoria = NomeCategoria("Cachorro")
    n6: NomeCategoria = NomeCategoria("Elefante")
    lido: list[DadosCategoria] = dao.listar_por_nomes([n1, n2, n3, n4, n5, n6])
    assert lido == parte_categorias

@db.transacted
def test_listar_tudo() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    lido: list[DadosCategoria] = dao.listar()
    assert lido == todas_categorias

@db.transacted
def test_listar_tudo_apos_insercao() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    dados: DadosCategoriaSemPK = dados_millenium_falcon
    pk: CategoriaPK = dao.criar(dados)
    assert pk.pk_categoria == millenium_falcon.pk_categoria
    lido: list[DadosCategoria] = dao.listar()
    esperado: list[DadosCategoria] = todas_categorias[:]
    esperado.append(millenium_falcon)
    assert lido == esperado

@db.transacted
def test_excluir_categoria_por_pk() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    pk: CategoriaPK = CategoriaPK(desenvolvimento.pk_categoria)
    lido1: DadosCategoria | None = dao.buscar_por_pk(pk)
    assert lido1 == desenvolvimento
    dao.deletar_por_pk(pk)
    lido2: DadosCategoria | None = dao.buscar_por_pk(pk)
    assert lido2 is None

@db.transacted
def test_excluir_categoria_por_pk_viola_chave_estrangeira() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    pk: CategoriaPK = CategoriaPK(qa.pk_categoria)

    with raises(IntegrityViolationException):
        dao.deletar_por_pk(pk)

    lido: DadosCategoria | None = dao.buscar_por_pk(pk)
    assert lido == qa

@db.transacted
def test_excluir_categoria_por_pk_nao_existe() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    pk: CategoriaPK = CategoriaPK(lixo2)
    dao.deletar_por_pk(pk)
    lido: DadosCategoria | None = dao.buscar_por_pk(pk)
    assert lido is None

@db.transacted
def test_salvar_categoria_com_pk() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    dados: DadosCategoria = DadosCategoria(qa.pk_categoria, "Pikachu")
    dao.salvar_com_pk(dados) # Transforma QA em Pikachu.

    pk: CategoriaPK = CategoriaPK(qa.pk_categoria)
    lido: DadosCategoria | None = dao.buscar_por_pk(pk)
    assert lido == dados

@db.transacted
def test_salvar_categoria_com_pk_nao_existe() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    dados: DadosCategoria = DadosCategoria(lixo3, "Pikachu")
    dao.salvar_com_pk(dados) # Não é responsabilidade do DAO saber se isso existe ou não, ele apenas roda o UPDATE.

    pk: CategoriaPK = CategoriaPK(lixo3)
    lido: DadosCategoria | None = dao.buscar_por_pk(pk)
    assert lido is None

@db.transacted
def test_criar_categoria_nome_repetido() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    dados: DadosCategoriaSemPK = DadosCategoriaSemPK("QA")

    with raises(IntegrityViolationException):
        dao.criar(dados)

    lido: DadosCategoria | None = dao.buscar_por_nome(nome_qa)
    assert lido == qa

@db.transacted
def test_criar_categoria_nome_curto() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    dados: DadosCategoriaSemPK = DadosCategoriaSemPK("")

    with raises(IntegrityViolationException):
        dao.criar(dados)

    lido: DadosCategoria | None = dao.buscar_por_nome(NomeCategoria(""))
    assert lido is None

@db.transacted
def test_criar_categoria_nome_longo() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    dados: DadosCategoriaSemPK = DadosCategoriaSemPK(nome_longo)

    with raises(IntegrityViolationException):
        dao.criar(dados)

    lido: DadosCategoria | None = dao.buscar_por_nome(NomeCategoria(nome_longo))
    assert lido is None

@db.transacted
def test_salvar_categoria_com_pk_nome_repetido() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    dados: DadosCategoria = DadosCategoria(qa.pk_categoria, "Produção")

    with raises(IntegrityViolationException):
        dao.salvar_com_pk(dados)

    lido1: DadosCategoria | None = dao.buscar_por_nome(nome_qa)
    assert lido1 == qa

    lido2: DadosCategoria | None = dao.buscar_por_nome(nome_producao)
    assert lido2 == producao

@db.transacted
def test_salvar_categoria_com_pk_nome_curto() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    dados: DadosCategoria = DadosCategoria(qa.pk_categoria, "")

    with raises(IntegrityViolationException):
        dao.salvar_com_pk(dados)

    lido1: DadosCategoria | None = dao.buscar_por_nome(nome_qa)
    assert lido1 == qa

    lido2: DadosCategoria | None = dao.buscar_por_nome(NomeCategoria(""))
    assert lido2 is None

@db.transacted
def test_salvar_categoria_com_pk_nome_longo() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    dados: DadosCategoria = DadosCategoria(qa.pk_categoria, nome_longo)

    with raises(IntegrityViolationException):
        dao.salvar_com_pk(dados)

    lido1: DadosCategoria | None = dao.buscar_por_nome(nome_qa)
    assert lido1 == qa

    lido2: DadosCategoria | None = dao.buscar_por_nome(NomeCategoria(nome_longo))
    assert lido2 is None

# TODO:
# Testar listar_por_segredo