from app.routes import db, ma

class Alumno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100))
    apellidos = db.Column(db.String(100))
    matricula = db.Column(db.String(20), unique=True)
    promedio = db.Column(db.Float)
    
    def __init__(self, nombres, apellidos, matricula, promedio):
        self.nombres = nombres
        self.apellidos = apellidos
        self.matricula = matricula
        self.promedio = promedio
        
    def to_dict(self):
        return {
            "id": self.id,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "matricula": self.matricula,
            "promedio": self.promedio
        }


class Profesor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numeroEmpleado = db.Column(db.Integer)
    nombres = db.Column(db.String(100))
    apellidos = db.Column(db.String(100))
    horasClase = db.Column(db.Integer)
    
    def __init__(self, numeroEmpleado, nombres, apellidos, horasClase):
        self.numeroEmpleado = numeroEmpleado
        self.nombres = nombres
        self.apellidos = apellidos
        self.horasClase = horasClase
    
    def to_dict(self):
        return {
            "id": self.id,
            "numeroEmpleado": self.numeroEmpleado,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "horasClase": self.horasClase
        }

#db.create_all()

class AlumnoSchema(ma.Schema):
    class Meta:
        fields = ('id', 'nombres', 'apellidos', 'matricula', 'promedio')

class ProfesorSchema(ma.Schema):
    class Meta:
        fields = ('id', 'numeroEmpleado', 'nombres', 'apellidos', 'horasClase')
