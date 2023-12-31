import random
import string
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import boto3
import json
import botocore.exceptions
import uuid
import time


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://admin:12345678@database-1-instance-1.cu2axqbcvtdk.us-east-1.rds.amazonaws.com/dbaws'
#app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:@localhost:3306/db_rest_awsproject'
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

global_aws_access_key_id='ASIAVQEVC2TXHJUEQIPW'
global_aws_secret_access_key='hLocF2HWTuHTFFb7Rhq9Y6eHH2jMg68s61a23oGW'
global_aws_session_token='FwoGZXIvYXdzEAIaDG598PjYE24VwV8J0iLOAf/dyOmYuSHVyMGU/9e0LiVhUTOsxiWbjilKkBNBGrlzBZ+xUH5pri/htfQUm83fd8GHezYaaluuaA7ITc8uipouqUnMn4bRGVw4AQApE6076dngOJxg+RaK9mwJ+aO+VH7LrKCM2mde9RkjdEF058Rzqyqr3LcaY62pzxIKA9Z1ID6BTY8pMh2WlcQ8ZkYDYSSylUjh3A3MqvY+4iKMZGpuECcq5EbPkV6t/YZ6mFrC1CBApaVbJ43rhsRRSzz9DhK53n8vwrGgzj+MhjknKO+17qsGMi3O+gdXXdcmzXIdJ+PfbQY7pKu0s/a6jsaocdGSeCAtXh6ee2kf286vPhRhezI='
s3 = boto3.client(
    's3',
    region_name='us-east-1',
    aws_access_key_id=global_aws_access_key_id,
    aws_secret_access_key=global_aws_secret_access_key,
    aws_session_token= global_aws_session_token
    )

sns = boto3.client(
    'sns',
    region_name='us-east-1',
    aws_access_key_id=global_aws_access_key_id,
    aws_secret_access_key=global_aws_secret_access_key,
    aws_session_token= global_aws_session_token
    )


dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-east-1',
    aws_access_key_id=global_aws_access_key_id,
    aws_secret_access_key=global_aws_secret_access_key,
    aws_session_token=global_aws_session_token
)

table = dynamodb.Table('sesiones-alumnos')



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

@app.route('/alumnos/<int:id>', methods=['GET'])
def get_alumno(id):
    
    alumno = Alumno.query.get(id)

    if not alumno:
        return jsonify({'error': 'Alumno no encontrado'}), 404

    bucket_name = 'marcoascawsbucket'  
    foto_perfil_url = f'https://{bucket_name}.s3.amazonaws.com/alumnos/{id}_fotoPerfil.jpg'

    alumno_data = {
        'id': alumno.id,
        'nombres': alumno.nombres,
        'apellidos': alumno.apellidos,
        'matricula': alumno.matricula,
        'promedio': alumno.promedio,
        'fotoPerfilUrl': foto_perfil_url,
        'password': alumno.password
       
    }

    return jsonify(alumno_data), 200


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



@app.route('/profesores/<int:id>', methods=['GET'])
def get_profesor(id):
    profesor = Profesor.query.get(id)
    if profesor:
        result = profesor_schema.dump(profesor)
        return jsonify(result), 200
    return jsonify({'error': 'Profesor no encontrado'}), 404

# METODOS POST

#POST /alumnos/{id}/fotoPerfil

@app.route('/alumnos/<int:id>/email', methods=['POST'])
def send_notification(id):
    
    alumno = Alumno.query.get(id)
    
    if not alumno:
        return jsonify({'error': 'Alumno no encontrado'}), 404

    student_data = {
        'id': alumno.id,
        'nombre': alumno.nombres,
        'apellido': alumno.apellidos
    }

    message = json.dumps(student_data)

    response = sns.publish(
        TopicArn='arn:aws:sns:us-east-1:378269783278:notificar-alumnos',
        Message=message,
        Subject='Notificación de calificaciones'
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return jsonify({'message': 'Notificación enviada correctamente'}), 200
    else:
        return jsonify({'error': 'Hubo un problema al enviar la notificación'}), 404

@app.route('/alumnos/<int:id>/session/login', methods=['POST'])
def login_session(id):

    password = request.json.get('password')
    #print(password) 
    alumno = Alumno.query.get(id)
    
    if not alumno:
        return jsonify({'error': 'Alumno no encontrado'}), 404
    
   
    if password == alumno.password:  
        alumnoId = id  
        
        
        def generate_session_string():
            return ''.join(random.choices(string.ascii_letters + string.digits, k=128))
        
        sessionStr = generate_session_string()
      
        try:
            session_item = {
                'id': str(uuid.uuid4()),
                'fecha': int(time.time()),
                'alumnoId': int(alumnoId),
                'active': True,
                'sessionString': sessionStr
            }
            
            
            response = table.put_item(Item=session_item)
            
            #print("Ítem creado exitosamente:", response)
            return jsonify({'message': 'Sesión iniciada correctamente','sessionString': sessionStr}), 200
        
        except botocore.exceptions.ClientError as e:
            #print("Error al crear el ítem:", e)
            return jsonify({'error': 'Hubo un problema al iniciar sesión'}), 500

    else:
        print(password, alumno.password)
        return jsonify({'error': 'Contraseña incorrecta'}), 400

@app.route('/alumnos/<int:id>/session/verify', methods=['POST'])
def verify_session(id):
    

    sessionString = request.json.get('sessionString')

    try:
        response = table.get_item(Key={'id': sessionString})
        item = response.get('Item')
        #print(item.get('active'))
        if item and item.get('alumnoId') == id and item.get('active', True):
            return jsonify({'message': 'Sesión válida'}), 200
        else:
            return jsonify({'error': 'Sesión inválida'}), 400
        
    except Exception as e:
        print("Error al verificar la sesión:", e)
        return jsonify({'error': 'Error al verificar la sesión'}), 500

@app.route('/alumnos/<int:alumnoId>/session/logout', methods=['POST'])
def logout_session(alumnoId):
    sessionString = request.json.get('sessionString') 
    
    try:

        response = table.get_item(Key={'id': sessionString})
        
        if 'Item' in response:
            item = response['Item']
            
           
            if item.get('alumnoId') == alumnoId:
                table.update_item(
                    Key={'id': sessionString},
                    UpdateExpression='SET active = :val',
                    ExpressionAttributeValues={':val': False}
                )
                return jsonify({'message': 'Sesión cerrada correctamente'}), 200
        else:
            return jsonify({'error': 'SessionString no válida'}), 400        
    except botocore.exceptions.ClientError as e:
        return jsonify({'error': 'Hubo un problema al cerrar la sesión'}), 500

@app.route('/alumnos/<int:id>/fotoPerfil', methods=['POST'])
def upload_photo(id):
    
    alumno = Alumno.query.get(id)
    
    if not alumno:
        return jsonify({'error': 'Alumno no encontrado'}), 404

    if 'foto' not in request.files:
        return jsonify({'response': 'Error: No file part'}), 400
   
    
    try:
    
        photo = request.files['foto']
       
        bucket_name = 'marcoascawsbucket'
        s3.upload_fileobj(photo, bucket_name, f'alumnos/{id}_fotoPerfil.jpg')
        object_url = f'https://{bucket_name}.s3.amazonaws.com/alumnos/{id}_fotoPerfil.jpg'
        return jsonify({'fotoPerfilUrl':object_url}), 200
    except Exception as e:
        return f'Error al subir la imagen: {str(e)}', 500
    

@app.route('/alumnos', methods=['POST'])
def create_alumno():
    data = request.get_json()

    campos_esperados = ['nombres', 'apellidos', 'matricula', 'promedio', 'password']
    tipos_esperados = [str, str, str, float, str]

    if validar_datos(data, campos_esperados, tipos_esperados):
        nueva_matricula = data['matricula']
        if Alumno.query.filter_by(matricula=nueva_matricula).first():
            return jsonify({'error': f'Matricula {nueva_matricula} ya está en uso'}), 400

        nuevo_alumno = Alumno(
            nombres=data['nombres'],
            apellidos=data['apellidos'],
            matricula=data['matricula'],
            promedio=data['promedio'],
            fotoPerfilUrl = '',
            password =data['password']
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
    
