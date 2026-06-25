from __future__ import annotations

from flask import render_template, Blueprint

from product_roadmap import roadmap_metrics, roadmap_phases, status_label

roadmap_bp = Blueprint('roadmap', __name__)


@roadmap_bp.route('/roadmap')
def index():
    return render_template(
        'roadmap/index.html',
        growth_phases=roadmap_phases(),
        growth_metrics=roadmap_metrics(),
        status_label=status_label,
    )
