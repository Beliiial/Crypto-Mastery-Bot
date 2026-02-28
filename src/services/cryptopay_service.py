from aiocryptopay import AioCryptoPay, Networks
from src.utils.config import config
import logging

class CryptoPayService:
    def __init__(self):
        self.crypto = AioCryptoPay(token=config.CRYPTO_PAY_TOKEN, network=Networks.MAIN_NET)

    async def create_invoice(self, amount: float, currency: str = "USDT"):
        try:
            invoice = await self.crypto.create_invoice(
                amount=amount,
                asset=currency,
                payload="subscription_payment"
            )
            return invoice
        except Exception as e:
            logging.error(f"Error creating invoice: {e}")
            return None

    async def get_invoice(self, invoice_id: int):
        try:
            invoices = await self.crypto.get_invoices(invoice_ids=[invoice_id])
            if invoices:
                return invoices[0]
            return None
        except Exception as e:
            logging.error(f"Error getting invoice: {e}")
            return None

    async def get_invoices(self, invoice_ids: list[int]):
        try:
            return await self.crypto.get_invoices(invoice_ids=invoice_ids)
        except Exception as e:
            logging.error(f"Error getting invoices: {e}")
            return []

cryptopay_service = CryptoPayService()
