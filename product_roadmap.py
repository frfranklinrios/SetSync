"""Roadmap de produto — mercado, conversão e engajamento."""

from __future__ import annotations

from typing import Any

STATUS_DONE = 'done'
STATUS_PROGRESS = 'progress'
STATUS_PLANNED = 'planned'

_STATUS_LABELS = {
    STATUS_DONE: 'Entregue',
    STATUS_PROGRESS: 'Em andamento',
    STATUS_PLANNED: 'Planejado',
}


def roadmap_phases() -> list[dict[str, Any]]:
    return [
        {
            'id': 'recent',
            'badge': 'Recente',
            'title': 'Base lançada',
            'subtitle': 'Fundação para crescimento de inscritos e estúdios',
            'css': 'p0',
            'entries': [
                {
                    'icon': 'fa-comment-dots',
                    'title': 'Assistente de ajuda',
                    'desc': 'Chatbot com busca em Ajuda, Guia e FAQ — widget em todo o site.',
                    'tags': ['Suporte'],
                    'status': STATUS_DONE,
                },
                {
                    'icon': 'fa-route',
                    'title': 'Onboarding de estúdio',
                    'desc': 'Checklist pós-cadastro: perfil, fotos, salas, horários, QR e divulgação.',
                    'tags': ['Estúdio'],
                    'status': STATUS_DONE,
                },
                {
                    'icon': 'fa-qrcode',
                    'title': 'QR de agendamento',
                    'desc': 'Link e PNG para recepção — bandas escaneiam e reservam pelo app.',
                    'tags': ['Estúdio'],
                    'status': STATUS_DONE,
                },
                {
                    'icon': 'fa-shield-halved',
                    'title': 'Estúdios no painel admin',
                    'desc': 'Superadmin vê todos os estúdios, planos e acessa o painel do dono.',
                    'tags': ['Admin'],
                    'status': STATUS_DONE,
                },
                {
                    'icon': 'fa-tags',
                    'title': 'Estúdio Premium R$ 49',
                    'desc': 'Plano pago com salas ilimitadas e trial de 30 dias no primeiro cadastro.',
                    'tags': ['Monetização'],
                    'status': STATUS_DONE,
                },
            ],
        },
        {
            'id': 'conversion-quick',
            'badge': 'Fase 4 · Curto prazo',
            'title': 'Conversão inteligente',
            'subtitle': 'Trial → pago no momento certo, com mensagem baseada em uso real',
            'css': 'p4',
            'entries': [
                {
                    'icon': 'fa-chart-line',
                    'title': 'Upsell contextual no dashboard',
                    'desc': 'Banners quando perto do limite (músicas, integrantes, setlists) ou fim do trial.',
                    'tags': ['Dashboard', 'Pro'],
                    'status': STATUS_DONE,
                },
                {
                    'icon': 'fa-envelope',
                    'title': 'E-mails de onboarding estúdio',
                    'desc': 'Sequência D0, D2, D5, D7 e D10 para donos: painel, QR, fotos, primeira reserva e fim do trial.',
                    'tags': ['E-mail', 'Estúdio'],
                    'status': STATUS_DONE,
                },
                {
                    'icon': 'fa-hand-pointer',
                    'title': 'Chatbot com CTAs logados',
                    'desc': 'Respostas com botões diretos: adicionar cifra, cadastrar estúdio, ver planos.',
                    'tags': ['Suporte', 'Ativação'],
                    'status': STATUS_DONE,
                },
                {
                    'icon': 'fa-user-plus',
                    'title': 'Indicação visível',
                    'desc': 'Card no dashboard após primeira setlist — convide banda e ganhe 15 dias Pro.',
                    'tags': ['Viral', 'Pro'],
                    'status': STATUS_DONE,
                },
                {
                    'icon': 'fa-door-open',
                    'title': 'Paywall no momento aha',
                    'desc': 'Upgrade ao exportar PDF, convidar 6º membro ou ao abrir Modo Tocar no trial.',
                    'tags': ['Pro', 'UX'],
                    'status': STATUS_DONE,
                },
            ],
        },
        {
            'id': 'engagement',
            'badge': 'Fase 5 · Médio prazo',
            'title': 'Engajamento semanal',
            'subtitle': 'Manter a banda ativa entre ensaios e shows',
            'css': 'p5',
            'entries': [
                {
                    'icon': 'fa-calendar-check',
                    'title': 'Ensaio + setlist sugerida',
                    'desc': 'Lembrete antes do evento com link para setlist; sugestão das últimas músicas tocadas.',
                    'tags': ['Agenda'],
                    'status': STATUS_DONE,
                },
                {
                    'icon': 'fa-list-check',
                    'title': 'Onboarding por eventos reais',
                    'desc': 'Checklist marca Modo Tocar só após abrir; agenda após primeiro evento criado.',
                    'tags': ['Ativação'],
                    'status': STATUS_DONE,
                },
                {
                    'icon': 'fa-arrows-turn-to-dots',
                    'title': 'Ponte banda ↔ estúdio',
                    'desc': 'No perfil: “também toca em banda?” / “tem estúdio?” com CTAs cruzados.',
                    'tags': ['LTV'],
                    'status': STATUS_DONE,
                },
                {
                    'icon': 'fa-calendar-days',
                    'title': 'Checkout anual no Mercado Pago',
                    'desc': 'Fechar o desconto anual da landing no pagamento real — toggle Mensal/Anual nos planos (banda e estúdio).',
                    'tags': ['Monetização'],
                    'status': STATUS_DONE,
                },
                {
                    'icon': 'fa-newspaper',
                    'title': 'Conteúdo acionável',
                    'desc': 'Posts e guias com CTA in-app: checklist do culto, setlist em 10 min, encher estúdio.',
                    'tags': ['SEO', 'Blog'],
                    'status': STATUS_DONE,
                },
            ],
        },
        {
            'id': 'studio-market',
            'badge': 'Fase 6 · Estúdio',
            'title': 'Mercado de ensaio',
            'subtitle': 'Densidade de estúdios, confiança e receita recorrente',
            'css': 'p6',
            'entries': [
                {
                    'icon': 'fa-certificate',
                    'title': 'Selo estúdio verificado',
                    'desc': 'Badge na busca para perfil completo: fotos, endereço, disponibilidade e QR ativo.',
                    'tags': ['Busca'],
                    'status': STATUS_DONE,
                },
                {
                    'icon': 'fa-chart-pie',
                    'title': 'Métricas no painel do dono',
                    'desc': 'Visualizações, cliques no QR, solicitações e taxa de confirmação.',
                    'tags': ['Analytics'],
                    'status': STATUS_DONE,
                },
                {
                    'icon': 'fa-rotate-left',
                    'title': 'Retenção pós-trial estúdio',
                    'desc': 'E-mail quando trial expira + downgrade para 2 salas; CTA Premium R$ 49.',
                    'tags': ['E-mail'],
                    'status': STATUS_DONE,
                },
                {
                    'icon': 'fa-map-location-dot',
                    'title': 'Densidade por cidade',
                    'desc': 'Fortaleza primeiro: seeds, busca destacada e parcerias locais.',
                    'tags': ['Go-to-market'],
                    'status': STATUS_DONE,
                },
                {
                    'icon': 'fa-share-nodes',
                    'title': 'Preview social do estúdio',
                    'desc': 'Open Graph rico na página pública e link de agendamento para Instagram/WhatsApp.',
                    'tags': ['Divulgação'],
                    'status': STATUS_DONE,
                },
            ],
        },
        {
            'id': 'strategic',
            'badge': 'Fase 7 · Estratégico',
            'title': 'Escala e Worship',
            'subtitle': 'Posicionamento “app da banda no ensaio e no palco”',
            'css': 'p7',
            'entries': [
                {
                    'icon': 'fa-church',
                    'title': 'Programa Worship para igrejas',
                    'desc': 'Landing + trial de conta + onboarding multi-banda para ministérios.',
                    'tags': ['Worship'],
                    'status': STATUS_DONE,
                },
                {
                    'icon': 'fa-filter',
                    'title': 'Funil de produto',
                    'desc': 'Métricas no admin: cadastro → banda → cifra → setlist → Modo Tocar → pago (banda e estúdio).',
                    'tags': ['Analytics'],
                    'status': STATUS_DONE,
                },
                {
                    'icon': 'fa-star',
                    'title': 'Pesquisa pós-trial',
                    'desc': 'NPS/CSAT in-app após trial — entender churn e priorizar features.',
                    'tags': ['Produto'],
                    'status': STATUS_DONE,
                },
                {
                    'icon': 'fa-mobile-screen',
                    'title': 'PWA como app principal',
                    'desc': 'Instalação guiada pós-cadastro; não competir com app nativo no curto prazo.',
                    'tags': ['Mobile'],
                    'status': STATUS_DONE,
                },
            ],
        },
    ]


def roadmap_metrics() -> list[dict[str, str]]:
    """KPIs para acompanhar mercado e engajamento."""
    return [
        {
            'name': 'Ativação D7',
            'desc': '% de contas com banda + ≥1 cifra + ≥1 setlist em 7 dias',
        },
        {
            'name': 'Modo Tocar D14',
            'desc': 'Proxy de valor no palco — quem abriu o Modo Tocar na 2ª semana',
        },
        {
            'name': 'Trial → pago',
            'desc': 'Conversão separada para banda (Pro) e estúdio (Premium)',
        },
        {
            'name': 'WAU / MAU',
            'desc': 'Engajamento semanal da banda (logins + edições + eventos)',
        },
        {
            'name': 'Reservas / estúdio',
            'desc': 'Solicitações e confirmações por estúdio ativo',
        },
        {
            'name': 'Churn pós-trial',
            'desc': 'Onde o funil quebra — banda e estúdio',
        },
    ]


def status_label(status: str) -> str:
    return _STATUS_LABELS.get(status, status)
