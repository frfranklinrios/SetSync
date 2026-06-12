"""Hub de páginas SEO (/guia) — combinações de busca."""

from __future__ import annotations

from flask import Blueprint, abort, render_template

from security import external_url_for
from seo_pages import get_seo_page, list_seo_pages

guia_bp = Blueprint('guia', __name__, url_prefix='/guia')


@guia_bp.route('/')
def guia_index():
    pages = list_seo_pages()
    return render_template('guia/index.html', pages=pages)


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
    )
