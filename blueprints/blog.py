"""Blog público com SEO."""

from __future__ import annotations

import os
import re

from flask import Blueprint, abort, render_template, request

from db import get_blog_post_by_slug, list_blog_posts
from security import external_url_for

blog_bp = Blueprint('blog', __name__)


def _markdown_to_html(text: str) -> str:
    if not text:
        return ''
    if text.lstrip().startswith('<'):
        return text
    return text.replace('\n', '<br>\n')


@blog_bp.route('/blog')
def blog_index():
    posts = list_blog_posts(published_only=True)
    return render_template('blog/index.html', posts=posts)


@blog_bp.route('/blog/<slug>')
def blog_post(slug: str):
    post = get_blog_post_by_slug(slug, published_only=True)
    if not post:
        abort(404)
    canonical = external_url_for('blog.blog_post', slug=slug)
    og_image = post.get('imagem_capa') or external_url_for(
        'static', filename='logoSetSync.png', _external=True,
    )
    conteudo_html = _markdown_to_html(post.get('conteudo') or '')
    return render_template(
        'blog/post.html',
        post=post,
        conteudo_html=conteudo_html,
        canonical_url=canonical,
        og_image=og_image,
        meta_title=post.get('meta_title') or post['titulo'],
        meta_description=post.get('meta_description') or post.get('resumo') or '',
    )
