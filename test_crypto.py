import asyncio
from aiocryptopay import AioCryptoPay, Networks
from src.utils.config import config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test():
    crypto = AioCryptoPay(token=config.CRYPTO_PAY_TOKEN, network=Networks.MAIN_NET)

    try:
        print("Checking connection (get_me)...")
        app = await crypto.get_me()
        print(f"Success! App: {app.name} (ID: {app.app_id})")
        
        print("Attempting to create test invoice...")
        invoice = await crypto.create_invoice(amount=1, asset="USDT", payload="test")
        print(f"Success! Invoice created: {invoice.invoice_id}")
        print(f"Link: {invoice.bot_invoice_url}")
        
        # Clean up
        print("Deleting test invoice...")
        await crypto.delete_invoice(invoice.invoice_id)
        print("Deleted.")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await crypto.close()

if __name__ == "__main__":
    asyncio.run(test())
