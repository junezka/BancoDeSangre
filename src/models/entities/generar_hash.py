from werkzeug.security import generate_password_hash

# Escribe la contraseña que quieres usar para tus pruebas
contrasena_en_texto_plano = 'BMS1234' # O la que tú quieras

# Generamos el hash
hash_generado = generate_password_hash(contrasena_en_texto_plano)

# Imprimimos el hash para que lo puedas copiar
print("Copia y pega este hash en la columna 'password' de tu base de datos:")
print(hash_generado)