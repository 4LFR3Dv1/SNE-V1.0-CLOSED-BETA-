"""
Helper functions for pagination in API endpoints
"""

from typing import Dict, Any, List, Optional
from flask import request
from flask_sqlalchemy.pagination import Pagination


def get_pagination_params() -> tuple[int, int]:
    """
    Extrai parâmetros de paginação dos query parameters
    
    Returns:
        tuple: (page, per_page)
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    limit = request.args.get('limit', None, type=int)
    
    # Se limit foi especificado, usar como per_page
    if limit:
        per_page = limit
    
    # Validar valores
    page = max(1, page)  # Mínimo 1
    per_page = max(1, min(100, per_page))  # Entre 1 e 100
    
    return page, per_page


def format_pagination_response(
    items: List[Any],
    pagination: Pagination,
    serializer_func=None
) -> Dict[str, Any]:
    """
    Formata resposta com paginação
    
    Args:
        items: Lista de itens da página atual
        pagination: Objeto Pagination do Flask-SQLAlchemy
        serializer_func: Função opcional para serializar cada item
    
    Returns:
        dict: Resposta formatada com dados e paginação
    """
    # Serializar itens se função fornecida
    if serializer_func:
        serialized_items = [serializer_func(item) for item in items]
    else:
        serialized_items = items
    
    return {
        'data': serialized_items,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
            'next_page': pagination.next_num if pagination.has_next else None,
            'prev_page': pagination.prev_num if pagination.has_prev else None
        }
    }


def paginate_query(query, page: Optional[int] = None, per_page: Optional[int] = None) -> Pagination:
    """
    Pagina uma query SQLAlchemy
    
    Args:
        query: Query SQLAlchemy
        page: Número da página (opcional, pega de request.args)
        per_page: Itens por página (opcional, pega de request.args)
    
    Returns:
        Pagination: Objeto de paginação do Flask-SQLAlchemy
    """
    if page is None or per_page is None:
        page, per_page = get_pagination_params()
    
    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

