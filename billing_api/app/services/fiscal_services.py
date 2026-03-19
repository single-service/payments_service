from abc import ABC, abstractmethod
from datetime import datetime
import os
import uuid

from app.integrations.atol import Atol

SNO_MAP = {
    1: "osn",
    2: "usn_income",
    3: "usn_income_outcome",
    4: "esn",
    5: "patent"
}

class BaseOFD(ABC):

    @abstractmethod
    async def create_sell_check(self, application, order):
        raise NotImplementedError    


class AtolService(BaseOFD):
    
    async def register_document(self, application, order, params, operations_service, operation_type: str):
        from app.enums import DocumentType
        
        SITE_HOST = os.getenv("SITE_HOST")
        external_id = uuid.uuid4()
        data = {
            "receipt": {
                "items": [],
                "client": {
                    "email": order.user_email
                },
                "company": {
                    "inn": application.inn,
                    "sno": SNO_MAP.get(application.sno),
                    "email": application.email,
                    "payment_address": application.payment_address 
                },
                "payments": [
                    {
                        "type": 1
                    }
                ]
            },
            "service": {
                "callback_url": f"https://{SITE_HOST}/api/v1/callback-atol/"
            },
            "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "external_id": str(external_id)
        }
        total = 0
        for entity in order.nomenclature:
            price_rubles = entity.get("price") / 100
            count = entity.get("count")
            amount_kopecks = entity.get("amount")
            amount_rubles = (amount_kopecks / 100) if amount_kopecks is not None else round(price_rubles * count, 2)
            total += amount_rubles
            position = {
                "name": entity.get("name"),
                "quantity": count,
                "price": price_rubles,
                "sum": amount_rubles,
                "vat":{ 
                    "type": entity.get("nds") 
                }
            }
            if "payment_method" in entity and entity["payment_method"] is not None:
                position["payment_method"] = entity["payment_method"]

            if "payment_type" in entity and entity["payment_type"] is not None:
                position["payment_object"] = entity["payment_type"]

            if "measure" in entity and entity["measure"] is not None:
                position["measure"] = entity["measure"]
            data["receipt"]["items"].append(position)
        data["receipt"]["total"] = total
        data["receipt"]["payments"][0]["sum"] = total
        document_id = await operations_service.create_fiscal_document(
            str(external_id),
            order.id,
            DocumentType.SALE.value if operation_type == "sell" else DocumentType.REFUND.value,
            data,
            created_dt=datetime.now(),
            updated_dt=datetime.now(),
        )
        if document_id is None:
            return
        uuid_document, status, error = await Atol(
            params.get("ATOL_LOGIN"),
            params.get("ATOL_PASSWORD"),
            params.get("ATOL_ID_GROUP_KKT"),
        ).register_document(data, operation_type)
        await operations_service.update_fiscal_document(
            document_id,
            ofd_document_id=uuid_document,
            status=status,
            error=error,
            updated_dt=datetime.now(),
        )
        
    async def check_callback_data(self, data: dict, operations_service):
        external_id = data["external_id"]
        status = data["status"]
        payload = data["payload"]
        if payload:
            ofd_receipt_url = payload["ofd_receipt_url"]
        else:
            ofd_receipt_url = None
        error = data["error"]
        await operations_service.update_fiscal_document(
            external_id,
            status=status,
            ofd_document_url=ofd_receipt_url,
            error=error,
            updated_dt=datetime.now(),
        )    
