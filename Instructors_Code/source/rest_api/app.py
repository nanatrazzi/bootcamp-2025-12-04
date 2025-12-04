from datetime import date
from fastapi import FastAPI
from models.models import SimulacaoRequest, SimulacaoResponse

app = FastAPI()

UR_2024 = 6963.01


def calcular_anos_servico(data_admissao: date) -> float:
    """
    Calcula o tempo de serviço em anos com base na data de admissão.

    O cálculo considera a diferença entre a data atual (hoje) e a data de admissão,
    convertendo o total de dias decorridos em anos utilizando 365 dias como base.

    Args:
        data_admissao (date): Data em que o participante ingressou na patrocinadora.

    Returns:
        float: Tempo total de serviço em anos (valor decimal).
    """
    hoje = date.today()
    return (hoje - data_admissao).days / 365


@app.post("/simular", response_model=SimulacaoResponse)
def simular(payload: SimulacaoRequest):
    """
    Calcula as contribuições mensais do Plano CD Atual da Fundação Previdenciária IBM.

    Este endpoint reproduz exatamente as regras aplicadas na planilha Excel oficial,
    incluindo limites, percentuais e o comportamento de valores negativos para
    contribuições excedentes.

    Regras aplicadas:
    -----------------
    1. Contribuição Voluntária (CV):
        - Calculada como: salario_bruto * (percentual_cv / 100)

    2. Contribuição Patrocinadora 1:
        • Percentual:
            - 1% para participantes com menos de 730 dias (2 anos) de serviço
            - 1.5% para participantes com 730 dias ou mais
        • Base de cálculo:
            - min(salário, UR_2024)
            - Essa regra garante que, acima do limite da UR, o valor permaneça fixo
              (ex.: R$ 104,45 para salário maior que a UR)

    3. Contribuição Patrocinadora 2:
        • Percentual:
            - Usa o mesmo percentual da CV se CV < 6%
            - Trava em 6% caso CV >= 6%
        • Base de cálculo:
            - salario_bruto - UR_2024
            - Pode gerar valores negativos quando o salário é inferior à UR,
              exatamente como ocorre na planilha Excel.

    4. Total Mensal:
        - Soma literal de CV + Patrocinadora 1 + Patrocinadora 2
        - Mantém valores negativos caso existam.

    Args:
        payload (SimulacaoRequest): Dados de entrada contendo salário, data de admissão
            e percentual de contribuição voluntária (CV).

    Returns:
        SimulacaoResponse: Estrutura contendo:
            - salário considerado
            - anos de serviço
            - valores calculados de CV, Patrocinadora 1 e 2
            - percentuais aplicados
            - total mensal final
            - referência da UR vigente
    """

    salario = payload.salario_bruto
    perc_cv = payload.percentual_cv

    anos = calcular_anos_servico(payload.data_admissao)
    dias = anos * 365

    # Contribuição Voluntária (CV)
    valor_cv = salario * (perc_cv / 100)

    # PATROCINADORA 1 (com teto UR para manter valor de R$104,45 acima do UR_2024)
    if dias < 730:
        perc_p1 = 1.0
    else:
        perc_p1 = 1.5

    base_p1 = salario if salario < UR_2024 else UR_2024
    valor_p1 = base_p1 * (perc_p1 / 100)

    # PATROCINADORA 2
    perc_p2 = perc_cv if perc_cv < 6 else 6

    base_p2 = salario - UR_2024
    valor_p2 = base_p2 * (perc_p2 / 100)

    # Total Mensal
    total = valor_cv + valor_p1 + valor_p2

    return SimulacaoResponse(
        salario_bruto=salario,
        anos_servico=round(anos, 2),
        ur_referencia=UR_2024,

        percentual_patroc1=perc_p1,
        percentual_patroc2=perc_p2,

        valor_cv=round(valor_cv, 6),
        valor_patroc1=round(valor_p1, 6),
        valor_patroc2=round(valor_p2, 6),

        total_mensal=round(total, 6)
    )
