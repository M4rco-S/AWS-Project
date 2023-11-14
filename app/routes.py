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


def validar_datos(data, campos, tipos_esperados):
    if len(campos) != len(tipos_esperados):
        return False

    for campo, tipo_esperado in zip(campos, tipos_esperados):
        if campo not in data or not isinstance(data[campo], tipo_esperado):
            return False
    return True

# METODOS GET

@app.route('/alumnos', methods=['GET'])
def get_alumnos():
    alumnos_data = [alumno.to_dict() for alumno in alumnos]
    return jsonify(alumnos_data), 200
    #return jsonify(alumnos), 200
    
@app.route('/profesores', methods=['GET'])
def get_profesores():
    profesores_data = [profesor.to_dict() for profesor in profesores]
    return jsonify(profesores_data), 200


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
    
    campos_esperados = ['id','nombres', 'apellidos', 'matricula', 'promedio']
    tipos_esperados = [int, str, str, str, float]
    
    if validar_datos(data, campos_esperados, tipos_esperados):
        
        nuevo_id = data['id']
        if any(alumno.id == nuevo_id for alumno in alumnos):
            return jsonify({'error': f'ID {nuevo_id} ya está en uso'}), 400

        
        alumno = Alumno(id=nuevo_id, nombres=data['nombres'], apellidos=data['apellidos'], matricula=data['matricula'], promedio=data['promedio'])
        alumnos.append(alumno)
        return jsonify(alumno.to_dict()), 201
        
    return jsonify({'error': 'Datos incompletos o inválidos'}), 400

@app.route('/profesores', methods=['POST'])
def create_profesor():
    data = request.get_json()
    
    campos_esperados = ['id','numeroEmpleado', 'nombres', 'apellidos', 'horasClase']
    tipos_esperados = [int, int, str, str, int]
    
    if validar_datos(data, campos_esperados, tipos_esperados):
        
        nuevo_id = data['id']
        if any(profesor.id == nuevo_id for profesor in profesores):
            return jsonify({'error': f'ID {nuevo_id} ya está en uso'}), 400

        
        profesor = Profesor(id=nuevo_id, numeroEmpleado=data['numeroEmpleado'], nombres=data['nombres'], apellidos=data['apellidos'], horasClase=data['horasClase'])
        profesores.append(profesor)
        return jsonify(profesor.to_dict()), 201

    
    return jsonify({'error': 'Datos incompletos o inválidos'}), 400

# METODOS PUT

@app.route('/alumnos/<int:id>', methods=['PUT'])
def update_alumno(id):
    global alumnos
    alumno = next((alumno for alumno in alumnos if alumno.id == id), None)
    campos_esperados = ['nombres', 'apellidos', 'matricula', 'promedio']
    tipos_esperados = [str, str, str, float]
    data = request.get_json()
    
    if alumno:
        
        if validar_datos(data, campos_esperados, tipos_esperados):
        
            alumno.nombres = data.get('nombres', alumno.nombres)
            alumno.apellidos = data.get('apellidos', alumno.apellidos)
            alumno.matricula = data.get('matricula', alumno.matricula)
            alumno.promedio = data.get('promedio', alumno.promedio)
        
            return jsonify(alumno.to_dict()), 200
        
        return jsonify({'error': 'Datos incompletos o inválidos'}), 400
    
    return jsonify({'error': 'Alumno no encontrado'}), 404

   
    
    

@app.route('/profesores/<int:id>', methods=['PUT'])
def update_profesor(id):
    global profesores
    profesor = next((profesor for profesor in profesores if profesor.id == id), None)
    campos_esperados = ['numeroEmpleado', 'nombres', 'apellidos', 'horasClase']
    tipos_esperados = [int, str, str, int]
    data = request.get_json()
    
    if profesor:
        
        if validar_datos(data, campos_esperados, tipos_esperados):
        
            profesor.numeroEmpleado = data.get('numeroEmpleado', profesor.numeroEmpleado)
            profesor.nombres = data.get('nombres', profesor.nombres)
            profesor.apellidos = data.get('apellidos', profesor.apellidos)
            profesor.horasClase = data.get('horasClase', profesor.horasClase)
        
            return jsonify(profesor.to_dict()), 200
        
        return jsonify({'error': 'Datos incompletos o inválidos'}), 400
    
    return jsonify({'error': 'Profesor no encontrado'}), 404


# METODOS DELETE

@app.route('/alumnos/<int:id>', methods=['DELETE'])
def delete_alumno(id):
    
    global alumnos
    alumno_eliminar = next((alumno for alumno in alumnos if alumno.id == id), None)

    
    if alumno_eliminar:
        alumnos = [alumno for alumno in alumnos if alumno.id != id]
        return jsonify({'message': 'Alumno eliminado'}), 200
    else:
        return jsonify({'error': f'Alumno no encontrado'}), 404

@app.route('/profesores/<int:id>', methods=['DELETE'])
def delete_profesor(id):
    global profesores
    profesor_eliminar = next((profesor for profesor in profesores if profesor.id == id), None)

    if profesor_eliminar:
        profesores = [profesor for profesor in profesores if profesor.id != id]
        return jsonify({'message': 'Profesor eliminado'}), 200
    else:
        return jsonify({'error': f'Profesor no encontrado'}), 404

#if __name__ == '__main__':
#    app.run(debug=True)
    
