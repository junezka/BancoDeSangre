#Se importan las librerias
from flask import Flask, render_template, request, redirect, url_for, flash
from config import config
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required

#Models
from models.modelsUser import modelsUser
from models.modelsPaciente import modelsPaciente
from models.modelsHospitales import modelsHospitales

#Entities
from models.entities.user import Usuarios
from models.entities.paciente import Paciente


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
        # La clase Usuarios lo recibe como el parámetro 'password'.
        usuario_ingresado = Usuarios(0, request.form['usuario'], request.form['password'])
        user_model = modelsUser(db) # Pasamos la instancia de MySQL
        logged_user = user_model.login(usuario_ingresado) # Cambiado a logged_user para consistencia

        if logged_user is not None: 
            # Aquí la contraseña ya fue verificada exitosamente en el modelo.
            login_user(logged_user)

            return redirect(url_for("bms")) # Si el usuario existe, se redirige a bms
        else:
            # Es mejor un mensaje genérico por seguridad.
            flash("Usuario o Contraseña no válidos. Intente de nuevo.")
            return render_template('autentication/login.html') 
    else:
        return render_template('autentication/login.html') 

@app.route('/registroUsuario', methods=['GET', 'POST'])
def registroUsuario():
    if request.method == 'POST':
        # Recoger los datos del formulario
        usuario = request.form['usuario']
        password = request.form['password']
        fullname = request.form['fullname']

        # 1. Crear una instancia del modelo pasándole la conexión 'db'
        user_model = modelsUser(db) 

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
        if not all([nombre, apellido, nroCedula, genero, fechaNacimiento, direccion, estado_civil, diagnostico_inicial, remitido_por_id, elaborado_por_id]):
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
            paciente_id = paciente_model.regisroPaciente(
                nombre, apellido, nroCedula, genero, fechaNacimiento, direccion,
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

@app.route('/citas')
@login_required
def citas():
    return render_template('citas.html')

@app.route('/estadisticas')
@login_required
def estadisticas():
    return render_template('estadisticas.html')

#Se levanta en servidor local
if __name__== '__main__':
    app.config.from_object(config['development'])
    app.run(debug=True) # Siempre usa debug=True durante el desarrollo