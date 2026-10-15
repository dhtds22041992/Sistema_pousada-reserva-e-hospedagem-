
import datetime
import streamlit as str_visual

# ==========================================
# CONFIGURAÇÕES DA POUSADA (ESTADO DO SISTEMA)
# ==========================================
# Armazena os dados temporariamente enquanto o sistema está rodando
if "reservas" not in str_visual.session_state:
    str_visual.session_state.reservas = []

# Capacidade máxima da pousada
VAGAS_GARAGEM_TOTAIS = 10

# Preços por diária de cada tipo de acomodação
PRECOS_ACOMODACAO = {
    "Quarto Standard": 150.0,
    "Suíte Master": 280.0,
    "Chalé Família": 420.0,
}


# ==========================================
# FUNÇÕES DE LÓGICA DO SISTEMA
# ==========================================
def verificar_garagem_disponivel(data_in, data_out):
    """Conta quantas vagas de garagem já estão ocupadas no período selecionado"""
    vagas_ocupadas = 0
    for res in str_visual.session_state.reservas:
        # Verifica se há sobreposição de datas
        if not (data_out <= res["checkin"] or data_in >= res["checkout"]):
            if res["precisa_garagem"]:
                vagas_ocupadas += 1
    return VAGAS_GARAGEM_TOTAIS - vagas_ocupadas


# ==========================================
# INTERFACE VISUAL (STREAMLIT)
# ==========================================
str_visual.set_page_config(
    page_title="Pousada Império das Araras", page_icon="🦜", layout="centered"
)

# Cabeçalho Principal
str_visual.title("🦜 Pousada Império das Araras")
str_visual.markdown(
    "### Bem-vindo ao nosso sistema de reservas oficiais online!"
)
str_visual.write("Preencha os campos abaixo para garantir a sua estadia.")

# Criação de abas para separar a visão do cliente da visão do dono da pousada
aba_cliente, aba_admin = str_visual.tabs(
    ["📅 Fazer Reserva", "📊 Painel Administrativo"]
)

with aba_cliente:
    str_visual.header("Solicitação de Reserva")

    # Seção 1: Dados Básicos do Hóspede
    str_visual.subheader("1. Seus Dados")
    nome = str_visual.text_input("Nome Completo:")
    cpf = str_visual.text_input("CPF / Documento:")
    email = str_visual.text_input("E-mail para contato:")

    # Seção 2: Calendário e Datas de Estadia
    str_visual.subheader("2. Datas da Estadia")
    hoje = datetime.date.today()

    col1, col2 = str_visual.columns(2)
    with col1:
        data_checkin = str_visual.date_input(
            "Data de Check-in", min_value=hoje, value=hoje
        )
    with col2:
        data_checkout = str_visual.date_input(
            "Data de Check-out",
            min_value=data_checkin + datetime.timedelta(days=1),
            value=data_checkin + datetime.timedelta(days=1),
        )

    # Cálculo do total de diárias
    diarias = (data_checkout - data_checkin).days

    # Seção 3: Tipo de Acomodação
    str_visual.subheader("3. Escolha a Acomodação")
    tipo_quarto = str_visual.selectbox(
        "Tipo de quarto pretendido:", list(PRECOS_ACOMODACAO.keys())
    )

    # Seção 4: Vaga de Garagem com verificação em tempo real
    str_visual.subheader("4. Estacionamento")
    vagas_restantes = verificar_garagem_disponivel(data_checkin, data_checkout)

    if vagas_restantes > 0:
        precisa_garagem = str_visual.checkbox(
            f"Preciso de vaga na garagem ({vagas_restantes} vagas disponíveis para este período)"
        )
    else:
        str_visual.error(
            "⚠️ Desculpe, não há vagas de garagem disponíveis para as datas selecionadas."
        )
        precisa_garagem = False

    # Seção 5: Resumo de Valores e Forma de Pagamento
    str_visual.subheader("5. Pagamento")
    preco_diaria = PRECOS_ACOMODACAO[tipo_quarto]
    valor_total = preco_diaria * diarias

    str_visual.info(
        f"**Resumo do Valor:**\n"
        f"* {tipo_quarto}: R$ {preco_diaria:.2f} por noite\n"
        f"* Total de noites: {diarias}\n"
        f"--- \n"
        f"**Valor Total da Hospedagem: R$ {valor_total:.2f}**"
    )

    momento_pagamento = str_visual.radio(
        "Quando deseja realizar o pagamento?",
        ["Pagar Antecipado (Garantia de Reserva)", "Pagar no momento do Check-in"],
    )

    if momento_pagamento == "Pagar Antecipado (Garantia de Reserva)":
        forma_pagamento = str_visual.selectbox(
            "Selecione a forma de pagamento online:",
            ["Pix (Aprovação Imediata)", "Cartão de Crédito", "Boleto Bancário"],
        )
    else:
        forma_pagamento = str_visual.selectbox(
            "Como pretende pagar no balcão?",
            ["Dinheiro", "Pix", "Cartão de Crédito/Débito"],
        )

    # Botão de Confirmação Final
    if str_visual.button("Confirmar Minha Reserva 🚀"):
        if not nome or not cpf or not email:
            str_visual.warning(
                "Por favor, preencha todos os seus dados pessoais para continuar."
            )
        else:
            # Salvando os dados na lista de reservas do sistema
            nova_reserva = {
                "id": len(str_visual.session_state.reservas) + 1,
                "nome": nome,
                "cpf": cpf,
                "email": email,
                "checkin": data_checkin,
                "checkout": data_checkout,
                "acomodacao": tipo_quarto,
                "precisa_garagem": precisa_garagem,
                "valor_total": valor_total,
                "politica_pagamento": momento_pagamento,
                "forma_pagamento": forma_pagamento,
                "status": (
                    "Confirmada"
                    if momento_pagamento
                    == "Pagar Antecipado (Garantia de Reserva)"
                    else "Pendente (Paga no Check-in)"
                ),
            }

            str_visual.session_state.reservas.append(nova_reserva)
            str_visual.success(
                f"🎉 Parabéns {nome}! Sua reserva para o {tipo_quarto} foi registrada com sucesso no sistema da Império das Araras!"
            )
            str_visual.balloons()


# ==========================================
# PAINEL DO ADMINISTRADOR (POUSADA)
# ==========================================
with aba_admin:
    str_visual.header("⚙️ Painel de Controle - Administração")
    str_visual.write("Gerenciamento de hóspedes, check-ins e movimentações.")

    if len(str_visual.session_state.reservas) == 0:
        str_visual.write("Nenhuma reserva cadastrada até o momento.")
    else:
        for res in str_visual.session_state.reservas:
            # Layout expansível para cada reserva cadastrada
            with str_visual.expander(
                f"Reserva #{res['id']} - Hóspede: {res['nome']}"
            ):
                str_visual.write(f"**CPF:** {res['cpf']} | **E-mail:** {res['email']}")
                str_visual.write(
                    f"**Período:** {res['checkin'].strftime('%d/%m/%Y')} até {res['checkout'].strftime('%d/%m/%Y')}"
                )
                str_visual.write(f"**Acomodação:** {res['acomodacao']}")
                str_visual.write(
                    f"**Vaga de Garagem Reservada?** {'Sim 🚗' if res['precisa_garagem'] else 'Não ❌'}"
                )
                str_visual.write(f"**Valor a ser cobrado:** R$ {res['valor_total']:.2f}")
                str_visual.write(f"**Método Escolhido:** {res['politica_pagamento']}")
                str_visual.write(f"**Forma de Pagamento:** {res['forma_pagamento']}")

                # Badge visual de status
                if res["status"] == "Confirmada":
                    str_visual.success(f"Status atual: {res['status']}")
                else:
                    str_visual.warning(f"Status atual: {res['status']}")

                # Botões de ação para o dono da pousada gerenciar o hóspede
                col_btn1, col_btn2 = str_visual.columns(2)
                with col_btn1:
                    if str_visual.button(
                        f"Realizar Check-in #{res['id']}", key=f"in_{res['id']}"
                    ):
                        str_visual.info(
                            f"Hóspede {res['nome']} deu entrada na pousada!"
                        )
                with col_btn2:
                    if str_visual.button(
                        f"Realizar Check-out #{res['id']}",
                        key=f"out_{res['id']}",
                    ):
                        str_visual.info(
                            f"Hóspede {res['nome']} deu saída. Quarto liberado!"
                        )
