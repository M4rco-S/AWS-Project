class Alumno:
    def __init__(self, id: int, nombres: str, apellidos: str, matricula: int, promedio:float):
        self.id = id
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

class Profesor:
    def __init__(self, id: int, numero_empleado:int, nombres:str, apellidos:str, horas_clase:int):
        self.id = id
        self.numero_empleado = numero_empleado
        self.nombres = nombres
        self.apellidos = apellidos
        self.horas_clase = horas_clase
    
    def to_dict(self):
        return {
            "id": self.id,
            "numero_empleado": self.numero_empleado,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "horas_clase": self.horas_clase
        }
