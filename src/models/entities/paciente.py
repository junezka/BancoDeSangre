
class Paciente():
    def __init__(self, id_paciente, nombre, apellido, nroCedula, genero, fechaNacimiento, direccion,
        estado_civil=None, diagnostico_inicial=None, remitido_por=None, elaborado_por_id=None,
        citomegalovirus_status=None, tuberculosis_status=None, hepatitis_status=None, hepatitis_tipo=None,
        varicella_zoster_status=None, vih_status=None, otros_infecciosas_status=None, especificar_otros_infecciosas=None):
        
        self.idPaciente = id_paciente
        self.nombre = nombre
        self.apellido = apellido
        self.nroCedula = nroCedula
        self.genero = genero
        self.fechaNacimiento = fechaNacimiento
        self.direccion = direccion
        self.estado_civil = estado_civil
        self.diagnostico_inicial = diagnostico_inicial
        self.remitido_por = remitido_por
        self.elaborado_por_id = elaborado_por_id
        self.citomegalovirus_status = citomegalovirus_status
        self.tuberculosis_status = tuberculosis_status
        self.hepatitis_status = hepatitis_status
        self.hepatitis_tipo = hepatitis_tipo
        self.varicella_zoster_status = varicella_zoster_status
        self.vih_status = vih_status
        self.otros_infecciosas_status = otros_infecciosas_status
        self.especificar_otros_infecciosas = especificar_otros_infecciosas
