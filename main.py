from web3 import Web3
import random
import time
from loguru import logger
from sys import stderr
from web3.exceptions import TimeExhausted

logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <3}</level> | <level>{message}</level>")


# Подключение к узлу BSC
bsc_node = 'https://rpc.ankr.com/bsc'
web3 = Web3(Web3.HTTPProvider(bsc_node))

# Проверка подключения
if not web3.is_connected():
    print("Не удалось подключиться к узлу Binance Smart Chain")
    exit()

# Чтение приватных ключей
with open('private_keys.txt', 'r') as file:
    private_keys = file.read().splitlines()

# Определение диапазона суммы перевода и времени задержки
min_transfer_amount = 0.00018  # минимальная сумма перевода в BNB
max_transfer_amount = 0.00022  # максимальная сумма перевода в BNB
min_delay = 10  # минимальное время задержки в секундах
max_delay = 15  # максимальное время задержки в секундах

# Определение gas_limit и значений газа
gas_limit = 22000
max_fee_per_gas = web3.to_wei(1, 'gwei')
max_priority_fee_per_gas = web3.to_wei(1, 'gwei')

# Отправка BNB в заданном диапазоне
for private_key in private_keys:
    from_address = web3.eth.account.from_key(private_key).address
    balance = web3.eth.get_balance(from_address)

    with open('addresses.txt', 'r') as file:
        wallets = file.read().splitlines()

    index = 0
    for wallet in wallets:
        index += 1

        #если надо дозакинуть, куда не пришло, раскомментируй
        #if web3.eth.get_balance(web3.to_checksum_address(wallet)) > 0:
        #    continue

        amount_to_send = web3.to_wei(random.uniform(min_transfer_amount, max_transfer_amount), 'ether')
        nonce = web3.eth.get_transaction_count(from_address)

        total_cost = amount_to_send + gas_limit * max_fee_per_gas

        if balance >= total_cost:
            tx = {
                'nonce': nonce,
                'to': wallet,
                'value': amount_to_send,
                'gas': gas_limit,
                'maxFeePerGas': max_fee_per_gas,
                'maxPriorityFeePerGas': max_priority_fee_per_gas,
                'chainId': 56
            }
            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            logger.info(f"{index} отправлена на {wallet}. https://bscscan.com/tx/{tx_hash.hex()}")

            try:
                web3.eth.wait_for_transaction_receipt(tx_hash, timeout=360)
                balance -= total_cost
            except TimeExhausted:
                print(f"Время ожидания транзакции истекло: {tx_hash.hex()}")
                
            time.sleep(random.randint(min_delay, max_delay))
        else:
            print(f"Недостаточно средств на кошельке {from_address} для отправки на {wallet}")

print("PIZDA REIKAM, GO EBAT!")



