# models/modelsPaciente.py
from .entities.paciente import Paciente # Asegúrate de que esta importación es correcta

class modelsPaciente():
    def __init__(self, mysql_instance):
        self.mysql = mysql_instance

    def regisroPaciente(self, nombre, apellido, nroCedula, genero, fechaNacimiento, direccion,
                        estado_civil, diagnostico_inicial, remitido_por_id, elaborado_por_id,
                        citomegalovirus_status, tuberculosis_status, hepatitis_status, hepatitis_tipo,
                        varicella_zoster_status, vih_status, otros_infecciosas_status, especificar_otros_infecciosas,
                        alergia_a_medicamento, especificar_alergia, diabetes, hipertension_arterial):
        try:
            cursor = self.mysql.connection.cursor()
            
            # La consulta para insertar un nuevo paciente con TODOS los campos
            query = """ 
                INSERT INTO paciente(
                    nombre, apellido, nroCedula, genero, fechaNacimiento, direccion, 
                    estado_civil, diagnostico_inicial, remitido_por_id, elaborado_por_id,
                    citomegalovirus_status, tuberculosis_status, hepatitis_status, hepatitis_tipo,
                    varicella_zoster_status, vih_status, otros_infecciosas_status, especificar_otros_infecciosas,
                    alergia_a_medicamento, especificar_alergia, diabetes, hipertension_arterial
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Los datos deben pasarse en el mismo orden que las columnas en la consulta.
            cursor.execute(query, (
                nombre, apellido, int(nroCedula), genero, fechaNacimiento, direccion,
                estado_civil, diagnostico_inicial, remitido_por_id, elaborado_por_id,
                citomegalovirus_status, tuberculosis_status, hepatitis_status, hepatitis_tipo,
                varicella_zoster_status, vih_status, otros_infecciosas_status, especificar_otros_infecciosas,
                alergia_a_medicamento, especificar_alergia, diabetes, hipertension_arterial
            ))
            self.mysql.connection.commit()
            
            # Obtener el ID del paciente recién insertado
            # Esto es crucial para enlazar el tratamiento
            last_inserted_id = cursor.lastrowid
            
            cursor.close()
            return last_inserted_id # Retorna el ID del paciente para usarlo con tratamientos
            
        except Exception as ex:
            print(f"Error en el registro del paciente: {ex}")
            self.mysql.connection.rollback()
            raise Exception(ex)
        
    def modificarPacientes(self,recibe_tratamiento_status, especificacion_tratamiento, 
                           fecha_tratamiento, medicacion, idPaciente):
        try:
            cursor = self.mysql.connection.cursor()

            sql = """
                UPDATE tratamientos
                SET recibe_tratamiento_status = %s,
                    especificacion_tratamiento = %s,
                    fecha_tratamiento = %s,
                    medicacion = %s
                WHERE idPaciente = %s
            """
            cursor.execute(sql, (recibe_tratamiento_status, especificacion_tratamiento, fecha_tratamiento, medicacion, idPaciente))
            self.mysql.connection.commit()
            cursor.close()
        except Exception as ex:
            print(f"Error en el registro del paciente: {ex}")
            self.mysql.connection.rollback()
            raise Exception(ex)
        
    def get_last_paciente_id(self):
        try:
            cursor = self.mysql.connection.cursor()
            cursor.execute("SELECT MAX(idPaciente) FROM paciente")
            last_id = cursor.fetchone()[0]
            cursor.close()
            return last_id if last_id is not None else 0
        except Exception as e:
            print(f"Error al obtener el último ID de paciente: {str(e)}")
            return 0
        
    def buscarPaciente(self, query_string):
        try:
            cursor = self.mysql.connection.cursor()
            try:
                # Intentar convertir query_string a un entero
                query_int = int(query_string)
            except ValueError:
                query_int = -1  # Si no se puede convertir, usar -1

            sql = """
                SELECT *
                FROM paciente
                WHERE idPaciente = %s OR nroCedula = %s
            """
            # Ejecutar la consulta con ambos parámetros
            cursor.execute(sql, (query_int, query_string))
            paciente = cursor.fetchone()
            cursor.close()
            return paciente
        except Exception as e:
            print(f"Error al buscar paciente: {str(e)}")
            return None


    # --- Métodos para la nueva tabla de Tratamientos ---
    def registrarTratamiento(self, idPaciente, recibe_tratamiento, especificacion_tratamiento, fecha_tratamiento, medicacion):
        try:
            cursor = self.mysql.connection.cursor()
            query = """
                INSERT INTO tratamientos (idPaciente,recibe_tratamiento, especificacion_tratamiento, fecha_tratamiento, medicacion)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (idPaciente,recibe_tratamiento, especificacion_tratamiento, fecha_tratamiento, medicacion,))
            self.mysql.connection.commit()
            cursor.close()
            return True
        except Exception as ex:
            print(f"Error al registrar tratamiento: {ex}")
            self.mysql.connection.rollback()
            raise Exception(ex)

    def obtenerTratamientosPorPaciente(self, idPaciente):
        try:
            cursor = self.mysql.connection.cursor()
            query = "SELECT * FROM tratamientos WHERE idPaciente = %s ORDER BY fecha_tratamiento DESC"
            cursor.execute(query, (idPaciente,))
            tratamiento = cursor.fetchall()
            cursor.close()
            return tratamiento
        except Exception as e:
            print(f"Error al obtener tratamientos: {str(e)}")
            return []