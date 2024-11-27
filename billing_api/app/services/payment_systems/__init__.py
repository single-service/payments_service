from .systems.robokassa import RobokassaPaymentSystemService
from .systems.dummy_payment_system import DummyPaymentSystemService



# def get_payment_system(payment_system_name):
#     try:
#         module = __import__(
#             f"billing.payment_systems.systems.{payment_system_name.lower()}",
#             globals(),
#             locals(),
#             ["PaymentSystemService"],
#         )
#         _class = getattr(module, "PaymentSystemService")
#         return _class
#     except ImportError:
#         return None
