from decimal import Decimal

from fastapi import HTTPException


async def validate_refund_nomenclature(
    operation,
    refund_request,
    operations_service
):
    order_map = build_order_map(operation.nomenclature)

    refunded_map = await build_refunded_map(
        operation.id,
        operations_service
    )

    total_amount = 0

    for item in refund_request.nomenclature:
        validate_item_exists(item, order_map)
        validate_price(item, order_map)
        validate_quantity(item, order_map, refunded_map)

        item_amount = calculate_item_amount(item)
        validate_item_amount(item, item_amount)

        total_amount += item_amount

    validate_total_amount(total_amount, refund_request.amount)
    
    
def validate_item_exists(item, order_map):
    if item.name not in order_map:
        raise HTTPException(400, f"Item '{item.name}' not found")
    
    
def validate_price(item, order_map):
    if item.price != order_map[item.name]["price"]:
        raise HTTPException(400, f"Invalid price for '{item.name}'")
    
    
def validate_quantity(item, order_map, refunded_map):
    ordered = order_map[item.name]["count"]
    refunded = refunded_map.get(item.name, 0)

    if item.count + refunded > ordered:
        raise HTTPException(
            400,
            f"Too many items to refund for '{item.name}'"
        )
        
        
def calculate_item_amount(item):
    return int(Decimal(item.count) * item.price)


def validate_item_amount(item, expected_amount):
    if item.amount and item.amount != expected_amount:
        raise HTTPException(
            400,
            f"Invalid amount for '{item.name}'"
        )
        
        
def validate_total_amount(total, request_amount):
    if total != request_amount:
        raise HTTPException(
            400,
            "Amount mismatch with nomenclature"
        )
        
        
def build_order_map(nomenclature):
    return {
        item["name"]: item
        for item in nomenclature
    }
    
    
async def build_refunded_map(order_id, operations_service):
    refunds = await operations_service.get_order_refunds(order_id)

    result = {}

    for refund in refunds:
        if refund.status != "done":
            continue

        for item in refund.nomenclature:
            name = item["name"]
            result[name] = result.get(name, 0) + item["count"]

    return result
