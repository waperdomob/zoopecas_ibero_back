# run.py
import os
from app import create_app
from app.extensions import db

# Forzar UTF-8 en Windows
if os.name == 'nt':  # Windows
    import sys
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

app = create_app(os.environ.get('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    from app.models.user import User
    return {'db': db, 'User': User}

if __name__ == '__main__':
    # NO usar db.create_all() aquí - las tablas ya están creadas con el SQL
    # Si necesitas crear tablas, usa Flask-Migrate
    app.run(host='0.0.0.0', port=5000, debug=True)