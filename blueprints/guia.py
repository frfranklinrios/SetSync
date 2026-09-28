"""Hub de páginas SEO (/guia) — combinações de busca."""

from __future__ import annotations

from flask import Blueprint, abort, render_template

from marketing_shots import PACK_BR, PACK_ESTUDIO, PACK_GOSPEL
from security import external_url_for
from seo_pages import get_seo_page, get_comparison_page, list_seo_pages, list_comparison_pages

guia_bp = Blueprint('guia', __name__, url_prefix='/guia')


def _guia_shot_for_page(page: dict) -> dict | None:
    """Escolhe uma captura de tela ilustrativa para a página do guia."""
    blob = ' '.join([
        str(page.get('slug') or ''),
        str(page.get('h1') or ''),
        str(page.get('phrase') or ''),
        str(page.get('keywords') or ''),
    ]).lower()

    gospel = any(k in blob for k in ('igreja', 'louvor', 'worship', 'gospel', 'ministro', 'culto'))

    if any(k in blob for k in ('estudio', 'estúdio', 'sala', 'reserva')):
        if 'financeiro' in blob or 'receita' in blob or 'despesa' in blob:
            return {
                'pack': PACK_ESTUDIO,
                'name': 'estudio-financeiro-desktop',
                'frame': 'desktop',
                'caption': 'Financeiro do estúdio no Uníssono',
                'alt': 'Painel financeiro do estúdio no Uníssono',
            }
        return {
            'pack': PACK_ESTUDIO,
            'name': 'estudio-painel-mobile',
            'frame': 'mobile',
            'caption': 'Painel do estúdio no celular',
            'alt': 'Painel do estúdio Uníssono no celular',
        }

    if any(k in blob for k in ('financeiro', 'cachê', 'cache', 'despesa', 'receita', 'gorjeta', 'pix', 'couvert')):
        return {
            'pack': PACK_BR,
            'name': 'financeiro-banda-desktop',
            'frame': 'desktop',
            'caption': 'Financeiro da banda — cachês e despesas',
            'alt': 'Financeiro da banda no Uníssono',
        }

    if any(k in blob for k in ('modo tocar', 'tocar', 'palco', 'pedal', 'metrônomo', 'metronomo', 'pedido')):
        pack = PACK_GOSPEL if gospel else PACK_BR
        return {
            'pack': pack,
            'name': 'modo-tocar-mobile',
            'frame': 'mobile',
            'caption': 'Modo Tocar no Uníssono',
            'alt': 'Modo Tocar do Uníssono no celular',
        }

    if any(k in blob for k in ('setlist', 'roteiro', 'repertório', 'repertorio')):
        pack = PACK_GOSPEL if gospel else PACK_BR
        return {
            'pack': pack,
            'name': 'setlist-desktop',
            'frame': 'desktop',
            'caption': 'Setlist / roteiro no Uníssono',
            'alt': 'Setlist no Uníssono',
        }

    # Default ilustrativo
    pack = PACK_GOSPEL if gospel else PACK_BR
    return {
        'pack': pack,
        'name': 'setlist-desktop',
        'frame': 'desktop',
        'caption': 'Uníssono em ação',
        'alt': 'Tela do Uníssono',
    }


@guia_bp.route('/')
def guia_index():
    pages = list_seo_pages()
    return render_template('guia/index.html', pages=pages)


@guia_bp.route('/comparativo/<slug>')
def comparativo(slug: str):
    page = get_comparison_page(slug)
    if not page:
        abort(404)
    canonical = external_url_for('guia.comparativo', slug=slug)
    return render_template(
        'guia/comparativo.html',
        page=page,
        canonical_url=canonical,
        meta_title=page['meta_title'],
        meta_description=page['meta_description'],
        guia_shot=_guia_shot_for_page(page),
    )


@guia_bp.route('/<slug>')
def guia_page(slug: str):
    page = get_seo_page(slug)
    if not page:
        abort(404)
    canonical = external_url_for('guia.guia_page', slug=slug)
    return render_template(
        'guia/page.html',
        page=page,
        canonical_url=canonical,
        meta_title=page['meta_title'],
        meta_description=page['meta_description'],
        guia_shot=_guia_shot_for_page(page),
    )
