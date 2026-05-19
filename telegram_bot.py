from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

from config import BOT_TOKEN

from modules.users import (
    create_user_if_not_exists,
    get_user_by_name
)

from modules.accounts import (
    create_account,
    get_balance
)

from modules.transactions import (
    add_transaction
)


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    nome = update.effective_user.first_name

    create_user_if_not_exists(nome)

    user = get_user_by_name(nome)

    if user:

        user_id = user[0]

        create_account(user_id, "Carteira Principal")

    await update.message.reply_text(
        f"Olá {nome}! BOT Financeiro 2.0 iniciado."
    )


# =========================
# SALDO
# =========================

async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    nome = update.effective_user.first_name

    user = get_user_by_name(nome)

    if not user:

        await update.message.reply_text(
            "Usuário não encontrado."
        )

        return

    user_id = user[0]

    saldo_atual = get_balance(user_id)

    await update.message.reply_text(
        f"Seu saldo atual é R$ {saldo_atual:.2f}"
    )


# =========================
# ENTRADA
# =========================

async def entrada(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        valor = float(context.args[0])

        descricao = " ".join(context.args[1:])

        nome = update.effective_user.first_name

        user = get_user_by_name(nome)

        user_id = user[0]

        add_transaction(
            user_id=user_id,
            account_id=1,
            category_id=1,
            tipo='entrada',
            valor=valor,
            descricao=descricao
        )

        await update.message.reply_text(
            f"Entrada de R$ {valor:.2f} adicionada!"
        )

    except:

        await update.message.reply_text(
            "Use: /entrada valor descricao"
        )


# =========================
# SAÍDA
# =========================

async def saida(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        valor = float(context.args[0])

        descricao = " ".join(context.args[1:])

        nome = update.effective_user.first_name

        user = get_user_by_name(nome)

        user_id = user[0]

        add_transaction(
            user_id=user_id,
            account_id=1,
            category_id=5,
            tipo='saida',
            valor=valor,
            descricao=descricao
        )

        await update.message.reply_text(
            f"Saída de R$ {valor:.2f} adicionada!"
        )

    except:

        await update.message.reply_text(
            "Use: /saida valor descricao"
        )


# =========================
# MAIN
# =========================

def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("saldo", saldo))
    app.add_handler(CommandHandler("entrada", entrada))
    app.add_handler(CommandHandler("saida", saida))

    print("BOT 2.0 ONLINE!")

    app.run_polling()


if __name__ == "__main__":
    main()
