def normalize_company(raw_data: dict) -> dict:
    return {
        "id": raw_data.get("id"),
        "name": raw_data.get("razao_social", raw_data.get("name")),
        "cnpj": raw_data.get("cnpj")
    }

def normalize_sale(raw_data: dict) -> dict:
    return {
        "id": raw_data.get("id"),
        "value": raw_data.get("valor_total", raw_data.get("value")),
        "date": raw_data.get("data_venda", raw_data.get("date"))
    }
