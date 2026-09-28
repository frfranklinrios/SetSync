from pydantic import BaseModel, Field


class Produto(BaseModel):
    id: str
    nome: str
    preco_venda: float = Field(..., ge=0)
    imagem_url: str
    categoria: str = "Acessórios"
    marca: str = "Uníssono"
    preco_de: float | None = None
    fonte: str = "fornecedor"
    sku: str | None = None
    estoque: float = 0
    custo_aquisicao: float = Field(default=0, exclude=True)


class CatalogoStatus(BaseModel):
    fonte: str
    quantidade: int
    mp_configurada: bool
    ultimo_scrape: str | None = None
    usd_brl: float = 5.5
    cj_configurada: bool = False
    erro: str | None = None


class ProdutoAdminIn(BaseModel):
    id: str = Field(..., min_length=2, max_length=80)
    sku: str = ""
    titulo: str = Field(..., min_length=3, max_length=160)
    categoria: str = "Acessórios"
    marca: str = "Uníssono"
    imagem_url: str = ""
    url: str = ""
    preco_base_usd: float = Field(..., ge=0)
    frete_usd: float = Field(0, ge=0)
    estoque: int = Field(0, ge=0)


class CjDisponibilizarIn(BaseModel):
    pid: str = Field(..., min_length=4, max_length=80)
    categoria: str = ""


class ImportarUrlIn(BaseModel):
    url: str = Field(..., min_length=12, max_length=600)
    categoria: str = ""
    marca: str = ""
    publicar: bool = True
    preco_base_usd: float | None = Field(default=None, ge=0)
    frete_usd: float | None = Field(default=None, ge=0)


class ItemPedidoIn(BaseModel):
    produto_id: str
    quantidade: int = Field(1, ge=1, le=20)


class ClientePedido(BaseModel):
    nome: str = Field(..., min_length=3, max_length=120)
    email: str = Field(..., min_length=5, max_length=160)
    telefone: str = Field(..., min_length=10, max_length=20)
    cpf: str = ""
    cep: str = Field(..., min_length=8, max_length=9)
    endereco: str = Field(..., min_length=3, max_length=160)
    numero: str = Field(..., min_length=1, max_length=20)
    complemento: str = ""
    bairro: str = Field(..., min_length=2, max_length=80)
    cidade: str = Field(..., min_length=2, max_length=80)
    uf: str = Field(..., min_length=2, max_length=2)


class PedidoIn(BaseModel):
    itens: list[ItemPedidoIn]
    cliente: ClientePedido
    pagamento: str = "pix"


class ItemPedidoOut(BaseModel):
    produto_id: str
    nome: str
    quantidade: int
    preco_unitario: float
    preco_total: float
    custo_aquisicao: float = Field(default=0, exclude=True)


class PedidoOut(BaseModel):
    id: str
    status: str
    total: float
    total_pix: float
    itens: list[ItemPedidoOut]
    checkout_url: str = ""
    mensagem: str


class LedgerLinha(BaseModel):
    pedido_id: str
    valor_venda: float
    custo_aquisicao: float
    taxa_mp: float
    lucro_liquido: float = 0
    meio_pagamento: str = ""
    payment_id: str = ""
