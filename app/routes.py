from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:@localhost/db_rest_awsproject'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db = SQLAlchemy(app)
ma = Marshmallow(app)

from app.models import Alumno, Profesor, AlumnoSchema, ProfesorSchema

alumno_schema = AlumnoSchema()
alumnos_schema = AlumnoSchema(many=True)

profesor_schema = ProfesorSchema()
profesores_schema = ProfesorSchema(many=True)

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
    alumnos_data = Alumno.query.all()
    result= alumnos_schema.dump(alumnos_data)
    return jsonify(result), 200

@app.route('/profesores', methods=['GET'])
def get_profesores():
    profesores_data = Profesor.query.all()
    result = profesores_schema.dump(profesores_data)
    return jsonify(result), 200

@app.route('/alumnos/<int:id>', methods=['GET'])
def get_alumno(id):
    alumno = Alumno.query.get(id)
    if alumno:
        result = alumno_schema.dump(alumno)
        return jsonify(result), 200
    return jsonify({'error': 'Alumno no encontrado'}), 404

@app.route('/profesores/<int:id>', methods=['GET'])
def get_profesor(id):
    profesor = Profesor.query.get(id)
    if profesor:
        result = profesor_schema.dump(profesor)
        return jsonify(result), 200
    return jsonify({'error': 'Profesor no encontrado'}), 404

# METODOS POST

@app.route('/alumnos', methods=['POST'])
def create_alumno():
    data = request.get_json()

    campos_esperados = ['nombres', 'apellidos', 'matricula', 'promedio']
    tipos_esperados = [str, str, str, float]

    if validar_datos(data, campos_esperados, tipos_esperados):
        nueva_matricula = data['matricula']
        if Alumno.query.filter_by(matricula=nueva_matricula).first():
            return jsonify({'error': f'Matricula {nueva_matricula} ya está en uso'}), 400

        nuevo_alumno = Alumno(
            nombres=data['nombres'],
            apellidos=data['apellidos'],
            matricula=data['matricula'],
            promedio=data['promedio']
        )

        db.session.add(nuevo_alumno)
        db.session.commit()

        return alumno_schema.jsonify(nuevo_alumno), 201

    return jsonify({'error': 'Datos incompletos o inválidos'}), 400


@app.route('/profesores', methods=['POST'])
def create_profesor():
    data = request.get_json()
    
    campos_esperados = ['numeroEmpleado', 'nombres', 'apellidos', 'horasClase']
    tipos_esperados = [int, str, str, int]
    
    if validar_datos(data, campos_esperados, tipos_esperados):
        numero_empleado = data['numeroEmpleado']
        
        existe_profesor = Profesor.query.filter_by(numeroEmpleado=numero_empleado).first()
        if existe_profesor:
            return jsonify({'error': f'Número de empleado {numero_empleado} ya está en uso'}), 400

        nuevo_profesor = Profesor(
            numeroEmpleado=data['numeroEmpleado'],
            nombres=data['nombres'],
            apellidos=data['apellidos'],
            horasClase=data['horasClase']
        )
        
        db.session.add(nuevo_profesor)
        db.session.commit()
       
        return profesor_schema.jsonify(nuevo_profesor), 201
    
    return jsonify({'error': 'Datos incompletos o inválidos'}), 400


# METODOS PUT

@app.route('/alumnos/<int:id>', methods=['PUT'])
def update_alumno(id):
    alumno = Alumno.query.get(id)
    campos_esperados = ['nombres', 'apellidos', 'matricula', 'promedio']
    tipos_esperados = [str, str, str, float]
    data = request.get_json()

    if alumno:
        if validar_datos(data, campos_esperados, tipos_esperados):
            alumno.nombres = data.get('nombres', alumno.nombres)
            alumno.apellidos = data.get('apellidos', alumno.apellidos)
            alumno.matricula = data.get('matricula', alumno.matricula)
            alumno.promedio = data.get('promedio', alumno.promedio)
            
            db.session.commit()
            
            result = alumno_schema.dump(alumno)
            return jsonify(result), 200
        
        return jsonify({'error': 'Datos incompletos o inválidos'}), 400
    
    return jsonify({'error': 'Alumno no encontrado'}), 404


@app.route('/profesores/<int:id>', methods=['PUT'])
def update_profesor(id):
    profesor = Profesor.query.get(id)
    campos_esperados = ['numeroEmpleado', 'nombres', 'apellidos', 'horasClase']
    tipos_esperados = [int, str, str, int]
    data = request.get_json()

    if profesor:
        if validar_datos(data, campos_esperados, tipos_esperados):
            profesor.numeroEmpleado = data.get('numeroEmpleado', profesor.numeroEmpleado)
            profesor.nombres = data.get('nombres', profesor.nombres)
            profesor.apellidos = data.get('apellidos', profesor.apellidos)
            profesor.horasClase = data.get('horasClase', profesor.horasClase)
            
            db.session.commit()
            
            result = profesor_schema.dump(profesor)
            return jsonify(result), 200
        
        return jsonify({'error': 'Datos incompletos o inválidos'}), 400
    
    return jsonify({'error': 'Profesor no encontrado'}), 404



# METODOS DELETE

@app.route('/alumnos/<int:id>', methods=['DELETE'])
def delete_alumno(id):
    alumno_eliminar = Alumno.query.get(id)

    if alumno_eliminar:
        db.session.delete(alumno_eliminar)
        db.session.commit()
        return jsonify({'message': 'Alumno eliminado'}), 200
    else:
        return jsonify({'error': 'Alumno no encontrado'}), 404

@app.route('/profesores/<int:id>', methods=['DELETE'])
def delete_profesor(id):
    profesor_eliminar = Profesor.query.get(id)

    if profesor_eliminar:
        db.session.delete(profesor_eliminar)
        db.session.commit()
        return jsonify({'message': 'Profesor eliminado'}), 200
    else:
        return jsonify({'error': 'Profesor no encontrado'}), 404

#if __name__ == '__main__':
#    app.run(debug=True)
    
