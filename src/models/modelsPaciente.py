# models/modelsPaciente.py
from .entities.paciente import Paciente # Asegúrate de que esta importación es correcta

class modelsPaciente():
    def __init__(self, mysql_instance):
        self.mysql = mysql_instance

    def registroPaciente(self, fechaConsulta, nombre, apellido, nroCedula, genero, fechaNacimiento, direccion,
                            estado_civil, diagnostico_inicial, remitido_por_id, elaborado_por_id,
                            citomegalovirus_status, tuberculosis_status, hepatitis_status, hepatitis_tipo,
                            varicella_zoster_status, vih_status, otros_infecciosas_status, especificar_otros_infecciosas,
                            alergia_a_medicamento, especificar_alergia, diabetes, hipertension_arterial): 
            try:
                cursor = self.mysql.connection.cursor()

                # The query to insert a new patient with ALL fields
                query = """
                    INSERT INTO paciente(
                        fechaConsulta, nombre, apellido, nroCedula, genero, fechaNacimiento, direccion,
                        estado_civil, diagnostico_inicial, remitido_por_id, elaborado_por_id,
                        citomegalovirus_status, tuberculosis_status, hepatitis_status, hepatitis_tipo,
                        varicella_zoster_status, vih_status, otros_infecciosas_status, especificar_otros_infecciosas,
                        alergia_a_medicamento, especificar_alergia, diabetes, hipertension_arterial
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                # The data must be passed in the same order as the columns in the query.
                cursor.execute(query, (fechaConsulta,
                    nombre, apellido, int(nroCedula), genero, fechaNacimiento, direccion,
                    estado_civil, diagnostico_inicial, remitido_por_id, elaborado_por_id,
                    citomegalovirus_status, tuberculosis_status, hepatitis_status, hepatitis_tipo,
                    varicella_zoster_status, vih_status, otros_infecciosas_status, especificar_otros_infecciosas,
                    alergia_a_medicamento, especificar_alergia, diabetes, hipertension_arterial # ADD fechaConsulta here
                ))
                self.mysql.connection.commit()

                # Obtener el ID del paciente recién insertado para enlazar el tratamiento
                last_inserted_id = cursor.lastrowid

                cursor.close()
                return last_inserted_id # Retorna el ID del paciente para usarlo con tratamientos

            except Exception as ex:
                print(f"Error en el registro del paciente: {ex}")
                self.mysql.connection.rollback()
                raise Exception(ex)
    
    def check_cedula(self, nroCedula):
        
        try:
            cursor = self.mysql.connection.cursor() 
            query = "SELECT COUNT(*) FROM paciente WHERE nroCedula = %s" 
            cursor.execute(query, (nroCedula,))
            count = cursor.fetchone()[0]
            cursor.close()
            return count > 0
        except Exception as e:
            print(f"Error al verificar cédula existente: {e}")
            return False # En caso de error, asumimos que no existe para evitar bloqueos


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
        
    # --- Métodos para la nueva tabla de Citas ---
    def registrarCita(self, idPaciente, fechaCita, horaCita, motivoCita):
        try:
            cursor = self.mysql.connection.cursor()
            query = """
                INSERT INTO citas (idPaciente, fechaCita, horaCita, motivoCita)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (idPaciente, fechaCita, horaCita, motivoCita,))
            self.mysql.connection.commit()
            cursor.close()
            return True
        except Exception as ex:
            print(f"Error al registrar cita: {ex}")
            self.mysql.connection.rollback()
            raise Exception(ex)

    def obtenerCitasPorPaciente(self, idPaciente):
        try:
            cursor = self.mysql.connection.cursor()
            query = "SELECT idCita, idPaciente, fechaCita, horaCita, motivoCita FROM citas WHERE idPaciente = %s ORDER BY fechaCita DESC, horaCita DESC"
            cursor.execute(query, (idPaciente,))
            citas = cursor.fetchall()
            cursor.close()
            return citas
        except Exception as e:
            print(f"Error al obtener citas: {str(e)}")
            return []

    def obtenerTodasLasCitas(self):
        try:
            cursor = self.mysql.connection.cursor()
            query = """
                SELECT c.idCita, c.idPaciente, p.nombre, p.apellido, c.fechaCita, c.horaCita, c.motivoCita
                FROM citas c
                JOIN paciente p ON c.idPaciente = p.idPaciente
                ORDER BY c.fechaCita ASC, c.horaCita ASC
            """
            cursor.execute(query)
            citas = cursor.fetchall()
            cursor.close()
            return citas
        except Exception as e:
            print(f"Error al obtener todas las citas: {str(e)}")
            return []
        
    def eliminarCita(self, idCita):
        try:
            cursor = self.mysql.connection.cursor()
            query = "DELETE FROM citas WHERE idCita = %s"
            cursor.execute(query, (idCita,))
            self.mysql.connection.commit()
            cursor.close()
            return True
        except Exception as ex:
            print(f"Error al eliminar la cita: {ex}")
            self.mysql.connection.rollback()
            raise Exception(ex)

    def obtenerCitaPorId(self, idCita):
        try:
            cursor = self.mysql.connection.cursor()
            query = "SELECT * FROM citas WHERE idCita = %s"
            cursor.execute(query, (idCita,))
            cita = cursor.fetchone()
            cursor.close()
            return cita
        except Exception as e:
            print(f"Error al obtener la cita por ID: {str(e)}")
            return None
        
    def contarPacientesAtendidosPorRangoFechas(self, fecha_inicio_dt, fecha_fin_dt):
        try:
            cursor = self.mysql.connection.cursor()
            query = """
                SELECT
                    DATE(fechaConsulta) AS fecha_consulta,
                    COUNT(DISTINCT idPaciente) AS total_pacientes
                FROM paciente
                WHERE fechaConsulta BETWEEN %s AND %s
                GROUP BY DATE(fechaConsulta)
                ORDER BY fecha_consulta ASC;
            """
            cursor.execute(query, (fecha_inicio_dt, fecha_fin_dt))
            resultados = cursor.fetchall()
            cursor.close()
            return resultados
        except Exception as e:
            print(f"Error al obtener estadísticas por rango de fechas: {str(e)}")
            return []
        
    def contarPacientesRemitidosPorHospital(self, fecha_inicio_dt, fecha_fin_dt):
        try:
            cursor = self.mysql.connection.cursor()
            query = """
                SELECT 
                    p.remitido_por_id,
                    COUNT(p.idPaciente) AS total_pacientes_remitidos
                FROM 
                    paciente p 
                LEFT JOIN 
                    hospitales h ON p.remitido_por_id = h.id_hospital 
                WHERE 
                    fechaConsulta BETWEEN %s AND %s
                GROUP BY 
                    p.remitido_por_id 
                ORDER BY 
                    total_pacientes_remitidos DESC;
            """
            cursor.execute(query, (fecha_inicio_dt, fecha_fin_dt))
            resultados = cursor.fetchall()
            cursor.close()
            return resultados
        except Exception as e:
            print(f"Error al contar pacientes remitidos por hospital: {str(e)}")
            return []

    def contarPacientesAtendidosPorUsuario(self, fecha_inicio_dt, fecha_fin_dt):
        try:
            cursor = self.mysql.connection.cursor()
            query = """
                SELECT 
                    p.elaborado_por_id,
                    COUNT(p.idPaciente) AS total_pacientes
                FROM 
                    paciente p 
                LEFT JOIN 
                    usuarios u ON p.elaborado_por_id = u.id_usuarios 
                WHERE 
                    fechaConsulta BETWEEN %s AND %s
                GROUP BY 
                    p.elaborado_por_id 
                ORDER BY 
                    total_pacientes DESC;
            """
            cursor.execute(query, (fecha_inicio_dt, fecha_fin_dt))
            resultados = cursor.fetchall()
            cursor.close()
            return resultados
        except Exception as e:
            print(f"Error al contar pacientes atendidos por usuario: {str(e)}")
            return []