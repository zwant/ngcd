from flask import Blueprint, jsonify

bp = Blueprint('swagger', __name__)

@bp.route("/api/swagger/")
def swagger():
    from flask_swagger import swagger
    from flask import current_app as app

    swag = swagger(app, from_file_keyword='swagger_from_file')
    swag['info']['version'] = "0.0.1"
    swag['info']['title'] = "NGCD Event API"
    return jsonify(swag)
