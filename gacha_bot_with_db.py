import sqlite3
import random
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Substitua 'YOUR_TOKEN' pelo token fornecido pelo BotFather
TOKEN = '7458083912:AAHiLn1kK2n_Tyo9sfhvs4JihQp1XNrpnD4'

# Itens com suas probabilidades (quanto maior o número, menor a chance de ser puxado)
items = [
    ("🥉 gatuê", 50),
    ("🥉 gatinho baigudinho", 50),
    ("🥈 gatinho surtado ajuda ele", 20),
    ("🥈 gatinho coitadinho", 15),
    ("🥇 Elle Yoichi Parker", 5),
    ("🥇 Alexander Samuel Parker", 5),
    ("🥇 Salem Yoichi Parker", 5),
    ("🥇 Pão Quentinho", 5),
    ("🥇 Otto Yoichi Parker", 5)
]

# Inicializar banco de dados
conn = sqlite3.connect('gacha_bot.db', check_same_thread=False)
cursor = conn.cursor()

# Criar tabela de inventário se não existir
cursor.execute('''
CREATE TABLE IF NOT EXISTS inventory (
    user_id INTEGER,
    item TEXT
)
''')
conn.commit()

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Bem-vindo ao Kollector! Use /kollect para sortear.')

def kollect(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    item = random.choices([i[0] for i in items], [i[1] for i in items])[0]
    
    # Adicionar item ao inventário do usuário no banco de dados
    cursor.execute('INSERT INTO inventory (user_id, item) VALUES (?, ?)', (user_id, item))
    conn.commit()
    
    # Enviar a imagem correspondente ao item
    image_path = f'images/{item}.png'  # Suponha que o caminho das imagens esteja na pasta "images"
    try:
        with open(image_path, 'rb') as image_file:
            update.message.reply_photo(photo=image_file, caption=f'Você kolletou: {item}')
    except FileNotFoundError:
        update.message.reply_text(f'Você kolletou: {item} (nera pra ter foto aqui?)')

def caixinha(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    cursor.execute('SELECT item FROM inventory WHERE user_id = ?', (user_id,))
    items = cursor.fetchall()
    
    if items:
        # Contar a quantidade de cada item
        item_counts = {}
        for item in items:
            if item[0] in item_counts:
                item_counts[item[0]] += 1
            else:
                item_counts[item[0]] = 1
        
        # Criar a mensagem de inventário
        caixinha_list = '\n'.join([f'{item}: {count}' for item, count in item_counts.items()])
        update.message.reply_text(f'Sua caixinha:\n{caixinha_list}')
    else:
        update.message.reply_text('Opa, nadinha aqui.')

def delete_item(update: Update, context: CallbackContext) -> None:
         # Obter o nome do item a ser deletado do comando
        item_to_delete = ' '.join(context.args)
        user_id = update.message.from_user.id
             
        # Deletar o item específico do inventário do usuário no banco de dados
        cursor.execute('DELETE FROM inventory WHERE user_id = ? AND item = ?', (user_id, item_to_delete))
        conn.commit()
        update.message.reply_text(f'O pobi "{item_to_delete}" foi com Deus.')

def limpar(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    # Limpar todo o inventário do usuário no banco de dados
    cursor.execute('DELETE FROM inventory WHERE user_id = ?', (user_id,))
    conn.commit()

    update.message.reply_text('ta liso amigo.')


def main() -> None:
    updater = Updater(TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('kollect', kollect))
    dispatcher.add_handler(CommandHandler('delete', delete_item))
    dispatcher.add_handler(CommandHandler('caixinha', caixinha))
    dispatcher.add_handler(CommandHandler('limpar', limpar))


    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
