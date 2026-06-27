from fastapi import HTTPException
from typing import List

PERMITTED_METHODS = ["GET", "HEAD", "OPTIONS"]
BLOCKED_METHODS = ["POST", "PUT", "PATCH", "DELETE"]

SENSITIVE_KEYWORDS = [
    "delete", "destroy", "update", "edit", "create", "store",
    "cancel", "baixa", "pagamento", "receber", "pagar",
    "ajuste", "movimentar", "alterar", "fiscal", "emitir", "cancelar"
]

class SiberianPolicyError(Exception):
    pass

def validate_request_intent(method: str, endpoint: str):
    method = method.upper()
    if method in BLOCKED_METHODS:
        raise SiberianPolicyError(f"MÉTODO BLOQUEADO: Tentativa de escrita usando '{method}' não autorizada.")
        
    if method not in PERMITTED_METHODS:
        raise SiberianPolicyError(f"MÉTODO DESCONHECIDO: '{method}' não autorizado.")
        
    endpoint_lower = endpoint.lower()
    for kw in SENSITIVE_KEYWORDS:
        if kw in endpoint_lower:
            raise SiberianPolicyError(f"ENDPOINT SENSÍVEL BLOQUEADO: Palavra-chave proibida encontrada '{kw}'.")
            
    return True
