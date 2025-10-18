import click
from flask.cli import with_appcontext
from .extensions import db
from .models.user import User, UserRole

@click.command()
@with_appcontext
def init_db():
    """Inicializar la base de datos"""
    db.create_all()
    click.echo('Base de datos inicializada.')

@click.command()
@click.option('--username', prompt=True, help='Username del administrador')
@click.option('--email', prompt=True, help='Email del administrador')
@click.option('--password', prompt=True, hide_input=True, help='Contraseña del administrador')
@with_appcontext
def create_admin(username, email, password):
    """Crear usuario administrador"""
    try:
        # Verificar si ya existe
        if User.find_by_username(username):
            click.echo(f'Error: El usuario {username} ya existe.')
            return
        
        if User.find_by_email(email):
            click.echo(f'Error: El email {email} ya está en uso.')
            return
        
        # Crear administrador
        admin = User(
            username=username,
            email=email,
            password=password,
            nombre='Administrador',
            apellidos='Sistema',
            rol=UserRole.ADMIN
        )
        
        admin.save()
        click.echo(f'Administrador {username} creado exitosamente.')
        
    except Exception as e:
        click.echo(f'Error al crear administrador: {str(e)}')

def init_app(app):
    """Registrar comandos CLI"""
    app.cli.add_command(init_db)
    app.cli.add_command(create_admin)