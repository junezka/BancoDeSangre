#Se importan las librerias
from flask import Flask, render_template, request, redirect, url_for, flash
from config import config
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import calendar
from datetime import datetime
import re

#Models
from models.modelsUser import modelsUser
from models.modelsPaciente import modelsPaciente
from models.modelsHospitales import modelsHospitales

#Entities
from models.entities.user import Usuarios
from models.entities.paciente import Paciente
from models.entities.hospitales import Hospitales


#Inicializamos la app
app = Flask(__name__)

#Conección a la database
db = MySQL(app)

login_manager_app=LoginManager(app)

@login_manager_app.user_loader
def load_user(id_usuarios):
    user_model = modelsUser(db) # Pasamos la instancia de MySQL
    return user_model.get_by_id(id_usuarios)

#Redireccion desde la url base a la url login
@app.route('/')
def index():
    return redirect (url_for('login'))

#URL Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
            usuario_ingresado = Usuarios(0, request.form['usuario'], request.form['password'])
            
            user_model = modelsUser(db) # Instanciamos el modelo aquí para usarlo
            login_result = user_model.login(usuario_ingresado) # Llamamos al nuevo método

            if login_result["success"]:
                # Si el login fue exitoso, logueamos al usuario
                login_user(login_result["user"])
                return redirect(url_for('bms')) # Redirige al BMS o a la página principal
            else:
                # Si el login falló, mostramos el mensaje que viene del modelo
                flash(login_result["message"], 'error') # Usamos 'error' para el estilo del mensaje
                return render_template('autentication/login.html') 
    else:
        return render_template('autentication/login.html') 

def validar_contraseña(password, usuario):
    # Reglas de validación
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres."
    if not re.search(r"[A-Z]", password):
        return False, "La contraseña debe contener al menos una letra mayúscula."
    if not re.search(r"[a-z]", password):
        return False, "La contraseña debe contener al menos una letra minúscula."
    if not re.search(r"[0-9]", password):
        return False, "La contraseña debe contener al menos un número."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "La contraseña debe contener al menos un carácter especial."
    if usuario.lower() in password.lower():
        return False, "La contraseña no debe contener el nombre de usuario."
    
    return True, "Contraseña válida."

@app.route('/registroUsuario', methods=['GET', 'POST'])
def registroUsuario():
    if request.method == 'POST':
        # Recoger los datos del formulario
        usuario = request.form['usuario']
        password = request.form['password']
        fullname = request.form['fullname']

        # 1. Crear una instancia del modelo pasándole la conexión 'db'
        user_model = modelsUser(db) 
        contr_valida, mensaje = validar_contraseña(password, usuario)
        if not contr_valida:
            flash(mensaje, 'error')  # Muestra el mensaje de error
            return render_template('autentication/registroUsuario.html')
        
        # 2. Llamar al método corregido en la instancia
        if user_model.registroUsuario(usuario, password, fullname): 

            flash("Usuario registrado exitosamente.")
            return redirect(url_for("login"))  # Redirigir a otra página después de registrar
        else:
            flash("Error al registrar usuario.")
            return render_template('autentication/registroUsuario.html') 
    else:
        return render_template('autentication/registroUsuario.html') 

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

#URL luego de registro exitoso
@app.route('/bms')
@login_required
def bms():
    return render_template('bms.html')

@app.route('/calendario')
@login_required
def calendario():    
    
    paciente_model = modelsPaciente(db) # Instanciar el modelo de paciente

    # Lógica para generar el calendario
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    if not year or not month:
        now = datetime.now()
        year = now.year
        month = now.month

    # Asegurarse de que el mes esté en el rango correcto
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(year, month) # Esto retorna una lista de listas, donde cada sublista es una semana

    # Nombres de los meses y días de la semana en español
    month_names = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
        7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    # Obtener todas las citas para el mes actual del calendario
    todas_las_citas_mes = paciente_model.obtenerTodasLasCitas() # Obtener todas las citas
    
    # Filtrar citas para el mes y año actual del calendario
    citas_para_calendario = [
        cita for cita in todas_las_citas_mes
        if datetime.strptime(str(cita[4]), '%Y-%m-%d').year == year and \
        datetime.strptime(str(cita[4]), '%Y-%m-%d').month == month
    ]
    
    # Crear un diccionario para un acceso más fácil a las citas por día
    citas_por_dia = {}
    for cita in citas_para_calendario:
        fecha_cita = datetime.strptime(str(cita[4]), '%Y-%m-%d').day
        if fecha_cita not in citas_por_dia:
            citas_por_dia[fecha_cita] = []
        citas_por_dia[fecha_cita].append(cita)

    return render_template('calendario.html', year=year,
                           month=month,
                           month_name=month_names[month],
                           day_names=day_names,
                           month_days=month_days,
                           citas_por_dia=citas_por_dia)

#URL Registro Pacientes
@app.route('/registroPacientes', methods=['GET', 'POST'])
@login_required
def registroPacientes():
    paciente_model = modelsPaciente(db)
    user_model = modelsUser(db)
    hospitales_model = modelsHospitales(db)

    # Obtener la lista de usuarios para el dropdown "Elaborado por"
    usuarios_disponibles = user_model.get_all_users()
    hospitales_disponibles = hospitales_model.get_all_hospitales()

    if request.method == 'POST':
        # --- 1. Obtener Datos Personales ---
        fechaConsulta = request.form['fechaConsulta'] # Get the current date for fechaConsulta
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        nroCedula = request.form['nroCedula']
        genero = request.form.get('genero')
        fechaNacimiento = request.form['fechaNacimiento']
        direccion = request.form['direccion']
        estado_civil = request.form.get('estCiv')
        diagnostico_inicial = request.form.get('diagnostico')
        remitido_por_id = request.form.get('remision')
        elaborado_por_id = request.form.get('elaborado')

        # Validaciones iniciales
        if not all([fechaConsulta, nombre, apellido, nroCedula, genero, fechaNacimiento, direccion, estado_civil, diagnostico_inicial, remitido_por_id, elaborado_por_id]):
            flash("Por favor, complete todos los campos obligatorios de Datos Personales.")
            # Redireccionar y rellenar si falla
            last_id = paciente_model.get_last_paciente_id()
            next_id = last_id + 1
            return render_template('registroPaciente.html', next_id=next_id, usuarios=usuarios_disponibles, hospitales=hospitales_disponibles, form_data=request.form)

        # --- 2. Obtener Datos de Enfermedades Infecciosas ---
        citomegalovirus_status = request.form.get('citomegalovirus_status')
        tuberculosis_status = request.form.get('tuberculosis_status')
        hepatitis_status = request.form.get('hepatitis_status')
        hepatitis_tipo = request.form.get('hepatitis_tipo')
        varicella_zoster_status = request.form.get('varicella_zoster_status')
        vih_status = request.form.get('vih_status')
        otros_infecciosas_status = request.form.get('otros_infecciosas_status')
        especificar_otros_infecciosas = request.form.get('especificar_otros_infecciosas')

        # --- 3. Obtener Datos de Antecedentes Personales Patológicos ---
        alergia_a_medicamento = request.form.get('alergia_medicamento_status')
        especificar_alergia = request.form.get('especificar_alergia')
        diabetes = request.form.get('diabetes_status')
        hipertension_arterial = request.form.get('hipertension_arterial_status')

        try:
            # Registrar el paciente en la tabla 'paciente'
            # regisroPaciente ahora devuelve el ID del paciente recién insertado
            paciente_id = paciente_model.registroPaciente(fechaConsulta, nombre, apellido, nroCedula, genero, fechaNacimiento, direccion,
                estado_civil, diagnostico_inicial, remitido_por_id, elaborado_por_id,
                citomegalovirus_status, tuberculosis_status, hepatitis_status, hepatitis_tipo,
                varicella_zoster_status, vih_status, otros_infecciosas_status, especificar_otros_infecciosas,
                alergia_a_medicamento, especificar_alergia, diabetes, hipertension_arterial
            )
            if paciente_id is None:
                return render_template('registroPaciente.html', next_id=next_id, usuarios=usuarios_disponibles, hospitales=hospitales_disponibles, form_data=request.form)
            else:
                flash("Paciente registrado exitosamente.")
                return redirect(url_for("consultas"))
        except Exception as e:
            flash(f"Error al registrar paciente: {e}")
            last_id = paciente_model.get_last_paciente_id()
            next_id = last_id + 1
            return render_template('registroPaciente.html', next_id=next_id, usuarios=usuarios_disponibles, hospitales=hospitales_disponibles, form_data=request.form)

    else: # GET request (cuando se carga la página por primera vez)
        last_id = paciente_model.get_last_paciente_id()
        next_id = last_id + 1
        return render_template('registroPaciente.html', next_id=next_id, usuarios=usuarios_disponibles, hospitales=hospitales_disponibles,)


@app.route('/consultas', methods=['GET', 'POST'])
@login_required
def consultas():
    paciente_encontrado = None
    busqueda_realizada = False
    historial_tratamientos = None
    if request.method == 'POST':
        busqueda = request.form['busqueda']  # Este es el valor que necesitas pasar
        if busqueda:
            paciente_model = modelsPaciente(db)
            paciente_encontrado = paciente_model.buscarPaciente(busqueda)  # Asegúrate de que solo pasas un argumento
            busqueda_realizada = True
            if paciente_encontrado:
                historial_tratamientos = paciente_model.obtenerTratamientosPorPaciente(paciente_encontrado[0])
            else:
                flash("No se encontró ningún paciente con el número de historia o cédula proporcionado.")
        else:
            flash("Por favor, ingrese un número de historia o cédula para buscar.")
    return render_template('consultas.html', paciente_encontrado=paciente_encontrado, busqueda_realizada=busqueda_realizada, historial_tratamientos=historial_tratamientos)


@app.route('/tratamientos', methods=['GET', 'POST'])
@login_required
def tratamientos():
    paciente_encontrado = None
    busqueda_realizada = False
    if request.method == 'POST':
        busqueda = request.form['busqueda']  # Este es el valor que necesitas pasar
        if busqueda:
            paciente_model = modelsPaciente(db)
            paciente_encontrado = paciente_model.buscarPaciente(busqueda)  # Asegúrate de que solo pasas un argumento
            busqueda_realizada = True
            if not paciente_encontrado:
                flash("No se encontró ningún paciente con el número de historia o cédula proporcionado.")
        else:
            flash("Por favor, ingrese un número de historia o cédula para buscar.")
    return render_template('tratamientos.html', paciente_encontrado=paciente_encontrado, busqueda_realizada=busqueda_realizada)


@app.route('/registrarTratamiento', methods=['POST'])
@login_required
def registrarTratamiento():
    paciente_model = modelsPaciente(db)

    if request.method == 'POST':
        idPaciente = request.form['idPaciente']

        recibe_tratamiento_status = request.form['recibe_tratamiento_status']
        especificacion_tratamiento = request.form['especificacion_tratamiento']
        fecha_tratamiento = request.form['fecha_tratamiento'] # Viene como string
        medicacion = request.form['medicacion']
    try:
        # Registrar el paciente en la tabla 'paciente'
        # regisroPaciente ahora devuelve el ID del paciente recién insertado
        paciente_id = paciente_model.registrarTratamiento(idPaciente, recibe_tratamiento_status,especificacion_tratamiento,fecha_tratamiento, medicacion)
        if paciente_id is None:
            return render_template('tratamientos.html', form_data=request.form)
        else:
            flash("Tratamiento registrado exitosamente.")
            return redirect(url_for("consultas")) 
    except Exception as e:
            flash(f"Error al registrar tratamiento: str{e}")
            last_id = paciente_model.get_last_paciente_id()
            next_id = last_id + 1
            return render_template('tratamientos.html', next_id=next_id, form_data=request.form)

#URL Configuraciones
@app.route('/configuraciones', methods=['GET', 'POST']) 
@login_required
def configuraciones():
    # Solo permitir acceso si el usuario es admin
    if not current_user.is_admin():
        flash("Acceso denegado. Solo administradores pueden acceder a esta sección.")
        return redirect(url_for('bms')) # Redirigir a una página principal o de error
    
    hospitales_model = modelsHospitales(db)

    last_id_hospital = hospitales_model.get_last_hospital_id()
    next_id_hospital = last_id_hospital + 1

    if request.method == 'POST':
        # Manejar el registro de hospitales
        if 'nombreHospital' in request.form:
            nombreHospital = request.form['nombreHospital']
            
            if not all([nombreHospital]):
                flash("Por favor, complete todos los campos obligatorios para el hospital.")
                # Cuando hay un error en POST, asegúrate de pasar 'all_users' de nuevo
                return render_template('configuraciones.html', next_id_hospital=next_id_hospital, form_data=request.form)

            try:
                hospital_id = hospitales_model.registrarHospital(next_id_hospital, nombreHospital)
                if hospital_id is None:
                    flash("Error al registrar el hospital.")
                    return render_template('configuraciones.html', next_id_hospital=next_id_hospital, form_data=request.form)
                else:
                    flash("Hospital registrado exitosamente.")
                    return redirect(url_for("configuraciones"))
            except Exception as e:
                flash(f"Error al registrar hospital: {e}")
                return render_template('configuraciones.html', next_id_hospital=next_id_hospital, form_data=request.form)

    return render_template('configuraciones.html', 
                           next_id_hospital=next_id_hospital,
                           all_users=modelsUser(db).get_all_users(),
                           form_data=request.form if request.method == 'POST' else {}) 

@app.route('/bloqueo_usuario', methods=['POST'])
@login_required
def bloqueo_usuario():
    if not current_user.is_admin():
        flash("Acceso denegado. Solo administradores pueden acceder a esta sección.")
        return redirect(url_for('configuraciones'))

    user_model = modelsUser(db)
    all_users = user_model.get_all_users()

    if 'toggle_lock_user_id' in request.form:
        user_id_to_toggle = request.form['toggle_lock_user_id']
        current_lock_status = request.form['current_lock_status'].lower() == 'true'

        try:
            if user_model.toggle_user_lock_status(user_id_to_toggle, not current_lock_status):
                flash("El usuario ha sido desbloqueado exitosamente.", 'success')
            else:
                flash("Error al cambiar el estado del usuario.", 'error')
        except Exception as e:
            flash(f"Error al actualizar estado del usuario: {e}")

    return render_template('configuraciones.html',
                           all_users=all_users,
                           form_data=request.form if request.method == 'POST' else {})

#URL Citas
@app.route('/citas', methods=['GET', 'POST'])
@login_required
def citas():
    paciente_encontrado = None
    busqueda_realizada = False
    paciente_citas = []
    
    paciente_model = modelsPaciente(db) # Instanciar fuera del if para usarlo siempre

    if request.method == 'POST':
        if 'busqueda' in request.form: # Si se está buscando un paciente
            busqueda = request.form['busqueda']
            if busqueda:
                paciente_encontrado = paciente_model.buscarPaciente(busqueda)
                busqueda_realizada = True
                if paciente_encontrado:
                    # Si el paciente es encontrado, obtener sus citas
                    paciente_citas = paciente_model.obtenerCitasPorPaciente(paciente_encontrado[0]) # Suponiendo que el ID está en paciente_encontrado[0]
                else:
                    flash("No se encontró ningún paciente con el número de historia o cédula proporcionado.")
            else:
                flash("Por favor, ingrese un número de historia o cédula para buscar.")
        elif 'idPaciente' in request.form: # Si se está registrando una cita
            idPaciente = request.form['idPaciente']
            fechaCita = request.form['fechaCita']
            horaCita = request.form['horaCita']
            motivoCita = request.form['motivoCita']
            
            try:
                paciente_model.registrarCita(idPaciente, fechaCita, horaCita, motivoCita)
                flash("Cita registrada exitosamente!", "success")
                # Después de registrar, recargar las citas para el paciente
                paciente_encontrado = paciente_model.buscarPaciente(idPaciente)
                if paciente_encontrado:
                    paciente_citas = paciente_model.obtenerCitasPorPaciente(idPaciente)
                busqueda_realizada = True # Mantener la vista de búsqueda si se acaba de registrar
            except Exception as e:
                flash(f"Error al registrar la cita: {e}", "error")
                # Si hay error, intentar re-poblar los datos del paciente si es posible
                paciente_encontrado = paciente_model.buscarPaciente(idPaciente)
                if paciente_encontrado:
                    paciente_citas = paciente_model.obtenerCitasPorPaciente(idPaciente)
                    busqueda_realizada = True
    return render_template('citas.html', 
                           paciente_encontrado=paciente_encontrado, 
                           busqueda_realizada=busqueda_realizada,
                           paciente_citas=paciente_citas) 
@app.route('/eliminar_cita/<int:idCita>', methods=['POST'])
@login_required
def eliminar_cita(idCita):
    paciente_model = modelsPaciente(db)
    try:
        if paciente_model.eliminarCita(idCita):
            flash("Cita eliminada exitosamente!")
        else:
            flash("No se pudo eliminar la cita.")
    except Exception as e:
        flash(f"Error al eliminar la cita: {e}")
    return redirect(url_for('citas'))

#URL Estadísticas
@app.route('/estadisticas', methods=['GET', 'POST'])
def estadisticas():
    paciente_model = modelsPaciente(db)

    # Valores por defecto para el rango de fechas
    fecha_inicio = None
    fecha_fin = None

    # Retrieve all available hospitals and users for dropdowns
    hospitales_disponibles = modelsHospitales(db).get_all_hospitales()
    usuarios_disponibles = modelsUser(db).get_all_users()

    estadisticas_personalizadas_citas = []
    estadisticas_remitidos_hospital = []
    estadisticas_atendidos_usuario = []

    if request.method == 'POST':
        fecha_inicio_str = request.form.get('fecha_inicio')
        fecha_fin_str = request.form.get('fecha_fin')       

        if fecha_inicio_str and fecha_fin_str:
            try:
                fecha_inicio_dt = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
                fecha_fin_dt = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()

                if fecha_inicio_dt > fecha_fin_dt:
                    flash("La fecha de inicio no puede ser posterior a la fecha de fin.", "error")
                else:
                    estadisticas_personalizadas_citas = paciente_model.contarPacientesAtendidosPorRangoFechas(fecha_inicio_dt, fecha_fin_dt)
                    estadisticas_remitidos_hospital = paciente_model.contarPacientesRemitidosPorHospital(fecha_inicio_dt, fecha_fin_dt)
                    estadisticas_atendidos_usuario = paciente_model.contarPacientesAtendidosPorUsuario(fecha_inicio_dt, fecha_fin_dt)

            except ValueError:
                flash("Formato de fecha inválido. Por favor, use YYYY-MM-DD.", "error")
        else:
            flash("Por favor, ingrese ambas fechas para la búsqueda personalizada.", "error")

    return render_template('estadisticas.html',
                           fecha_inicio=fecha_inicio_str if 'fecha_inicio_str' in locals() else None, 
                           fecha_fin=fecha_fin_str if 'fecha_fin_str' in locals() else None,
                           estadisticas_personalizadas_citas=estadisticas_personalizadas_citas,
                           estadisticas_remitidos_hospital=estadisticas_remitidos_hospital,
                           estadisticas_atendidos_usuario=estadisticas_atendidos_usuario,
                           hospitales=hospitales_disponibles,
                           usuarios=usuarios_disponibles)


#Se levanta en servidor local
if __name__== '__main__':
    app.config.from_object(config['development'])
    app.run(debug=True) # Siempre usa debug=True durante el desarrollo