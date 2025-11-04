from flask import request, url_for
from math import ceil

class Pagination:
    """Clase para manejar paginación"""
    
    def __init__(self, query, page, per_page, total, items):
        self.query = query
        self.page = page
        self.per_page = per_page
        self.total = total
        self.items = items
    
    @property
    def pages(self):
        """Número total de páginas"""
        return ceil(self.total / self.per_page)
    
    @property
    def has_prev(self):
        """Tiene página anterior"""
        return self.page > 1
    
    @property
    def prev_num(self):
        """Número de página anterior"""
        return self.page - 1 if self.has_prev else None
    
    @property
    def has_next(self):
        """Tiene página siguiente"""
        return self.page < self.pages
    
    @property
    def next_num(self):
        """Número de página siguiente"""
        return self.page + 1 if self.has_next else None
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'page': self.page,
            'pages': self.pages,
            'per_page': self.per_page,
            'total': self.total,
            'has_prev': self.has_prev,
            'prev_num': self.prev_num,
            'has_next': self.has_next,
            'next_num': self.next_num
        }

def paginate_query(query, page=None, per_page=None, error_out=True):
    """Paginar una consulta SQLAlchemy"""
    if page is None:
        page = request.args.get('page', 1, type=int)
    if per_page is None:
        per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    if error_out and page > 1 and len(items) == 0:
        raise ValueError('Página no encontrada')
    
    return Pagination(query, page, per_page, total, items)
