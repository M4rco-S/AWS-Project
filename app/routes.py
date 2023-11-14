from flask import Flask, request, jsonify
from app.models import Alumno, Profesor


app = Flask(__name__)

alumnos = []
profesores = []


@app.errorhandler(405)
def metodo_no_permitido(error):
    return jsonify({'error': 'Método no permitido en esta ruta'}), 405

@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error(f"ErrorRRRRr: {error}")
    return jsonify({'error': 'Error interno del servidor'}), 500

def validar_datos(data, campos):
    for campo in campos:
        if campo not in data or not data[campo]:
            return False
    return True

# METODOS GET

@app.route('/alumnos', methods=['GET'])
def get_alumnos():
    alumnos_data = [alumno.to_dict() for alumno in alumnos]
    return jsonify(alumnos_data)
    #return jsonify(alumnos), 200
    
@app.route('/profesores', methods=['GET'])
def get_profesores():
    profesores_data = [profesor.to_dict() for profesor in profesores]
    return jsonify(profesores_data)


@app.route('/alumnos/<int:id>', methods=['GET'])
def get_alumno(id):
    alumno = next((alumno for alumno in alumnos if alumno.id == id), None)
    if alumno:
        return jsonify(alumno.to_dict()), 200
    return jsonify({'error': 'Alumno no encontrado'}), 404

@app.route('/profesores/<int:id>', methods=['GET'])
def get_profesor(id):
    profesor = next((profesor for profesor in profesores if profesor.id == id), None)
    if profesor:
        return jsonify(profesor.to_dict()), 200
    return jsonify({'error': 'Profesor no encontrado'}), 404

# METODOS POST

@app.route('/alumnos', methods=['POST'])
def create_alumno():
    data = request.get_json()
    

    if validar_datos(data, ['nombres', 'apellidos', 'matricula', 'promedio']):
        alumno = Alumno(id=len(alumnos) + 1, **data)
        alumnos.append(alumno)
        return jsonify(alumno.to_dict()), 201
        
    return jsonify({'error': 'Datos incompletos o inválidos'}), 400

@app.route('/profesores', methods=['POST'])
def create_profesor():
    data = request.get_json()

    if validar_datos(data, ['numero_empleado','nombres', 'apellidos', 'horas_clase']):
        profesor = Profesor(id=len(profesores) + 1, **data)
        profesores.append(profesor)
        return jsonify(profesor.to_dict()), 201
    return jsonify({'error': 'Datos incompletos o inválidos'}), 400

# METODOS PUT

@app.route('/alumnos/<int:id>', methods=['PUT'])
def update_alumno(id):
    alumno = next((alumno for alumno in alumnos if alumno.id == id), None)
    
    if alumno:
        data = request.get_json()
        alumno.nombres = data.get('nombres', alumno.nombres)
        alumno.apellidos = data.get('apellidos', alumno.apellidos)
        alumno.matricula = data.get('matricula', alumno.matricula)
        alumno.promedio = data.get('promedio', alumno.promedio)
        
        return jsonify(alumno.to_dict()), 200
    return jsonify({'error': 'Alumno no encontrado'}), 404

@app.route('/profesores/<int:id>', methods=['PUT'])
def update_profesor(id):
    profesor = next((profesor for profesor in profesores if profesor.id == id), None)
    
    if profesor:
        data = request.get_json()
        profesor.numero_empleado = data.get('numeroEmpleado', profesor.numero_empleado)
        profesor.nombres = data.get('nombres', profesor.nombres)
        profesor.apellidos = data.get('apellidos', profesor.apellidos)
        profesor.horas_clase = data.get('horasClase', profesor.horas_clase)
        
        return jsonify(profesor.to_dict()), 200
    return jsonify({'error': 'Profesor no encontrado'}), 404

# METODOS DELETE

@app.route('/alumnos/<int:id>', methods=['DELETE'])
def delete_alumno(id):
    global alumnos
    alumnos = [alumno for alumno in alumnos if alumno.id != id]
    return jsonify({'message': 'Alumno eliminado correctamente'}), 200

@app.route('/profesores/<int:id>', methods=['DELETE'])
def delete_profesor(id):
    global profesores
    profesores = [profesor for profesor in profesores if profesor.id != id]
    return jsonify({'message': 'Profesor eliminado correctamente'}), 200

#if __name__ == '__main__':
    #app.run(debug=False)
    
