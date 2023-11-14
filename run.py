from flask import jsonify
from app.routes import app

def pagina_no_encontrada(error):
   return jsonify({'error': 'Pagina no encontrada'}), 404


if __name__ == '__main__':
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(debug=True, port=5000)