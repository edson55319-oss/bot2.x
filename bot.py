
from telegram import (
    Update,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)

from modules.reports import (
    monthly_report,
    expenses_by_category,
    total_balance,
    generate_pdf,
    generate_excel
)

from config import BOT_TOKEN
VALOR, DESCRICAO, PAGAMENTO = range(3)

from modules.users import (
    create_user_if_not_exists,
    get_user_by_telegram_id
)

from modules.accounts import (
    create_account,
    get_balance,
    get_account_by_user
)

from modules.transactions import (
    add_transaction
)


# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    nome = update.effective_user.first_name

    telegram_id = update.effective_user.id

    create_user_if_not_exists(
        nome,
        telegram_id
    )

    user = get_user_by_telegram_id(
        telegram_id
    )

    user_id = user[0]

    create_account(
        user_id,
        f"Carteira {nome}"
    )

    await update.message.reply_text(
        f"Olá {nome}!"
    )

# SALDO
async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    telegram_id = update.effective_user.id

    user = get_user_by_telegram_id(
        telegram_id
    )

    if not user:

        await update.message.reply_text(
            "Usuário não encontrado. Use /start primeiro."
        )

        return

    user_id = user[0]

    account = get_account_by_user(user_id)

    if not account:

        await update.message.reply_text(
            "Conta não encontrada."
        )

        return

    account_id = account[0]

    saldo_atual = get_balance(account_id)

    await update.message.reply_text(
        f"Saldo atual: R$ {saldo_atual:.2f}"
    )

  # RELATORIO
async def relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):

    telegram_id = update.effective_user.id

    user = get_user_by_telegram_id(
        telegram_id
    )

    user_id = user[0]

    report = monthly_report(user_id)

    if not report:

        await update.message.reply_text(
            "Nenhuma transação encontrada."
        )

        return

    mensagem = "📊 RELATÓRIO\n\n"

    for tipo, total in report:

        mensagem += (
            f"{tipo} | "
            f"R$ {total:.2f}\n"
        )

    await update.message.reply_text(mensagem)
      

    # PDF
async def pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):

    telegram_id = update.effective_user.id

    user = get_user_by_telegram_id(
        telegram_id
       )

    user_id = user[0]

    arquivo = generate_pdf(user_id)

    with open(arquivo, "rb") as f:

        await context.bot.send_document(
        chat_id=update.effective_chat.id,
            document=f
        )

        # EXCEL
async def excel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    telegram_id = update.effective_user.id

    user = get_user_by_telegram_id(
        telegram_id
    )

    user_id = user[0]

    arquivo = generate_excel(user_id)

    with open(arquivo, "rb") as f:

        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=f
        )



        # HELP
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    texto = (
        "📌 COMANDOS DISPONÍVEIS\n\n"
        "/saldo - Ver saldo\n"
        "/entrada valor descricao\n"
        "/saida valor descricao\n"
        "/relatorio - Ver relatório\n"
        "/pdf - Gerar relatório em PDF\n"
        "/excel - Gerar relatório em Excel\n"
        "/help - Ver comandos disponíveis\n"
        "/cancel - Cancelar operação atual"
    )

    await update.message.reply_text(texto)

# ========================
# ENTRADA GUIADA
# =========================

async def entrada(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["tipo"] = "entrada"

    await update.message.reply_text(
        "💰 Qual o valor da entrada?"
    )

    return VALOR


# =========================
# SAIDA GUIADA
# =========================

async def saida(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["tipo"] = "saida"

    await update.message.reply_text(
        "💸 Qual o valor da saída?"
    )

    return VALOR


# =========================
# RECEBER VALOR
# =========================

async def receber_valor(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        valor = float(
            update.message.text.replace(",", ".")
        )

        context.user_data["valor"] = valor

        await update.message.reply_text(
            "📝 Digite a descrição:"
        )

        return DESCRICAO

    except:

        await update.message.reply_text(
            "❌ Digite apenas números."
        )

        return VALOR


# =========================
# RECEBER DESCRICAO
# =========================

async def receber_descricao(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["descricao"] = update.message.text

    teclado = [
        ["PIX", "Débito"],
        ["Crédito", "Dinheiro"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        teclado,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "💳 Escolha o pagamento:",
        reply_markup=reply_markup
    )

    return PAGAMENTO


# =========================
# RECEBER PAGAMENTO
# =========================

async def receber_pagamento(update: Update, context: ContextTypes.DEFAULT_TYPE):

    pagamento = update.message.text

    valor = context.user_data["valor"]

    descricao = context.user_data["descricao"]

    tipo = context.user_data["tipo"]

    nome = update.effective_user.first_name
    telegram_id = update.effective_user.id

    user = get_user_by_telegram_id(
    telegram_id
    )

    user_id = user[0]
    category_id = 1 if tipo == "entrada" else 5

    account = get_account_by_user(user_id)

    account_id = account[0]

    add_transaction(
          user_id=user_id,
          account_id=account_id,
          category_id=1,
          tipo='entrada',
          valor=valor,
          descricao=descricao,
          pagamento=pagamento
        )

    await update.message.reply_text(
        f"✅ {tipo.capitalize()} registrada!\n"
        f"💰 R$ {valor:.2f}\n"
        f"📝 {descricao}\n"
        f"💳 {pagamento}"
    )
    return ConversationHandler.END


# =========================
# CANCELAR
# =========================

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "❌ Operação cancelada."
    )

    return ConversationHandler.END

# MAIN
def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("saldo", saldo))
    conv_handler = ConversationHandler(

    entry_points=[
        CommandHandler("entrada", entrada),
        CommandHandler("saida", saida)
    ],

    states={

        VALOR: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                receber_valor
            )
        ],

        DESCRICAO: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                receber_descricao
            )
        ],

        PAGAMENTO: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                receber_pagamento
            )
        ]
    },

    fallbacks=[
        CommandHandler("cancel", cancel)
    ]
)

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("relatorio", relatorio))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("pdf", pdf))
    app.add_handler(CommandHandler("excel", excel))

    print("BOT ONLINE!")

    app.run_polling()


if __name__ == "__main__":
    main()
