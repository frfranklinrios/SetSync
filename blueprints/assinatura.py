from flask import Blueprint, request, jsonify
from db import resgatar_voucher
from blueprints.auth import login_required

assinatura_bp = Blueprint('assinatura', __name__)

@assinatura_bp.route('/voucher/resgatar', methods=['POST'])
@login_required
def resgatar():
    data = request.json
    codigo = data.get('codigo')
    banda_id = data.get('banda_id')
    
    if not codigo or not banda_id:
        return jsonify({"success": False, "msg": "Dados incompletos"}), 400
    
    # O resgatar_voucher valida e aplica o voucher no banco [cite: 198, 199]
    resultado = resgatar_voucher(codigo, banda_id)
    return jsonify(resultado)
