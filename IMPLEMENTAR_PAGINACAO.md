# 📄 IMPLEMENTAÇÃO: PAGINAÇÃO EM ENDPOINTS

## 🎯 OBJETIVO

Implementar paginação em endpoints que retornam listas grandes para melhorar performance e experiência do usuário.

---

## 📋 ENDPOINTS QUE PRECISAM PAGINAÇÃO

### **1. `/api/market-data` (ou similar)**
- Retorna histórico de dados de mercado
- Pode retornar milhares de registros
- ⚠️ **Necessita paginação**

### **2. `/api/alerts`**
- Lista de alertas do usuário
- Pode crescer com o tempo
- ⚠️ **Necessita paginação**

### **3. Endpoints Admin**
- `/api/admin/users/list` - ✅ **JÁ TEM PAGINAÇÃO**
- Outros endpoints admin

---

## 🔧 PADRÃO DE PAGINAÇÃO

### **Query Parameters:**
```
?page=1&limit=50&offset=0
```

### **Resposta:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 1234,
    "pages": 25,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## ✅ IMPLEMENTAÇÃO

### **1. Helper Function**

```python
def paginate_query(query, page=1, per_page=50):
    """Helper para paginar queries SQLAlchemy"""
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return {
        'items': pagination.items,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }
```

---

## 📊 BENEFÍCIOS

- ⚡ **Menos dados transferidos** (só o necessário)
- ⚡ **Respostas mais rápidas**
- ⚡ **Melhor experiência** do usuário
- ⚡ **Menos carga** no banco de dados

---

**Próximo passo:** Identificar endpoints específicos e implementar paginação.

