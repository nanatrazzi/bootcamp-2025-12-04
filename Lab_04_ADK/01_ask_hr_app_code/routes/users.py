from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime as dt
import pandas as pd
from sqlite3 import Row
import os
from database import get_db_connection
from models import (CriarColaboradorRequest, AtualizarCargoRequest,
    AtualizarEnderecoRequest, SolicitarFolgaRequest)

router = APIRouter(prefix="", tags=["colaboradores"])
TABELA = "colaboradores"

# Mapeamento entre nomes da planilha e nomes da tabela
PLANILHA_HEADERS = {
    "id": "ID",
    "nome": "Nome",
    "saldo_folgas_dias": "Saldo de Folgas (dias)",
    "cargo": "Cargo",
    "endereco": "Endereço",
    "folgas_solicitadas_dias": "Folgas Solicitadas (dias)"
}


def rows_to_dicts(rows: list[Row]) -> list[dict]:
    return [dict(r) for r in rows]


@router.post("/import-users/")
def import_users(file: UploadFile = File(None)):
    """
    Importa dados de colaboradores a partir de uma planilha Excel.
    Valida os dados e insere na base de dados sem sobrescrever registros existentes.
    """
    COL_MAP = {
        "ID": "id",
        "Nome": "nome",
        "Saldo de Folgas (dias)": "saldo_folgas_dias",
        "Cargo": "cargo",
        "Endereço": "endereco",
        "Folgas Solicitadas (dias)": "folgas_solicitadas_dias",
    }

    if file:
        df = pd.read_excel(file.file)
    else:
        path = os.getenv("PLANILHA_PATH", "dados_colaboradores.xlsx")
        if not os.path.exists(path):
            raise HTTPException(400, "Planilha não encontrada")
        df = pd.read_excel(path)

    # Validação dos cabeçalhos
    missing = set(COL_MAP.keys()) - set(df.columns)
    if missing:
        raise HTTPException(400, f"Cabeçalhos faltando: {', '.join(missing)}")

    df = df[list(COL_MAP.keys())].rename(columns=COL_MAP)

    # Conversões de tipo seguras
    df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")
    df["saldo_folgas_dias"] = pd.to_numeric(df["saldo_folgas_dias"], errors="coerce").fillna(0).astype(float)
    df["folgas_solicitadas_dias"] = pd.to_numeric(df["folgas_solicitadas_dias"], errors="coerce").fillna(0).astype(int)
    df["nome"] = df["nome"].astype(str).str.strip()
    df["cargo"] = df["cargo"].astype(str).str.strip()
    df["endereco"] = df["endereco"].astype(str).str.replace("\n", ", ").str.strip()

    conn = get_db_connection()
    cur = conn.cursor()

    # Insere ou atualiza com base no ID
    total = 0
    for _, r in df.iterrows():
        if pd.isna(r.id):
            continue  # ignora linhas sem ID
        cur.execute(f"""
            INSERT INTO {TABELA} (id, nome, saldo_folgas_dias, cargo, endereco, folgas_solicitadas_dias)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                nome=excluded.nome,
                saldo_folgas_dias=excluded.saldo_folgas_dias,
                cargo=excluded.cargo,
                endereco=excluded.endereco,
                folgas_solicitadas_dias=excluded.folgas_solicitadas_dias
        """, (
            int(r.id), r.nome, float(r.saldo_folgas_dias),
            r.cargo, r.endereco, int(r.folgas_solicitadas_dias)
        ))
        total += 1

    conn.commit()
    conn.close()
    return {"message": "Importação concluída com sucesso", "registros": total}


@router.get("/export-users/")
def export_users():
    """
    Exporta os dados dos colaboradores para planilha Excel.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT id, nome, saldo_folgas_dias, cargo, endereco, folgas_solicitadas_dias FROM {TABELA}")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return {"status": "Não há dados disponíveis"}

    df = pd.DataFrame(rows_to_dicts(rows))
    df = df.rename(columns=PLANILHA_HEADERS)

    file_path = "dados_colaboradores.xlsx"
    df.to_excel(file_path, index=False)
    return FileResponse(
        file_path,
        filename="dados_colaboradores.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.delete("/clear-users/")
def clear_users():
    """
    Limpa toda a tabela de colaboradores.
    """
    conn = get_db_connection()
    conn.execute(f"DELETE FROM {TABELA}")
    conn.commit()
    conn.close()
    return {"status": "Todos os dados foram excluídos com sucesso"}


@router.get("/user_profile_details/{id}", operation_id="userProfileDetails")
def get_user_profile(id: int):
    """
    Retorna os dados do colaborador a partir do ID.
    """
    conn = get_db_connection()
    user = conn.execute(
        f"""SELECT id, nome, saldo_folgas_dias, cargo, endereco, folgas_solicitadas_dias
             FROM {TABELA} WHERE id = ?""", (id,)
    ).fetchone()
    conn.close()

    if not user:
        raise HTTPException(404, "Colaborador não encontrado")
    return dict(user)


@router.post("/create-user", operation_id="createUser")
def create_user(request: CriarColaboradorRequest):
    """
    Cria um novo colaborador (sem ID).
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        f"""INSERT INTO {TABELA} (nome, saldo_folgas_dias, cargo, endereco)
            VALUES (?, ?, ?, ?)""",
        (request.nome, request.saldo_folgas_dias, request.cargo, request.endereco)
    )
    conn.commit()
    novo_id = cur.lastrowid
    conn.close()
    return {"message": "Colaborador criado com sucesso", "id": novo_id}



@router.get("/time-off-balance/{id}", operation_id="getTimeOffBalance")
def get_time_off_balance(id: int):
    """
    Consulta o saldo de folgas de um colaborador pelo ID.
    """
    conn = get_db_connection()
    row = conn.execute(f"SELECT saldo_folgas_dias FROM {TABELA} WHERE id = ?", (id,)).fetchone()
    conn.close()

    if not row:
        raise HTTPException(404, "Colaborador não encontrado")
    return {"saldo_folgas_dias": row["saldo_folgas_dias"]}

@router.post("/request-time-off", operation_id="requestTimeOffBalance")
def request_time_off(request: SolicitarFolgaRequest):
    """
    Registra uma solicitação de folga, descontando do saldo de folgas.
    """
    conn = get_db_connection()
    user = conn.execute(f"SELECT * FROM {TABELA} WHERE id = ?", (request.id,)).fetchone()
    if not user:
        conn.close()
        raise HTTPException(404, "Colaborador não encontrado")

    try:
        from_date = dt.strptime(request.data_inicio, "%Y-%m-%d")
        to_date = dt.strptime(request.data_fim, "%Y-%m-%d")
    except ValueError:
        conn.close()
        raise HTTPException(400, "Datas devem estar no formato YYYY-MM-DD")

    days = (to_date - from_date).days
    if days <= 0:
        conn.close()
        raise HTTPException(400, "A data final deve ser posterior à data inicial")

    if days > user["saldo_folgas_dias"]:
        conn.close()
        raise HTTPException(400, "Saldo de folgas insuficiente")

    conn.execute(
        f"""UPDATE {TABELA}
            SET folgas_solicitadas_dias = ?, saldo_folgas_dias = saldo_folgas_dias - ?
            WHERE id = ?""",
        (days, days, user["id"])
    )
    conn.commit()
    conn.close()
    return {"message": "Solicitação registrada", "folgas_solicitadas_dias": days}



@router.put("/update-title", operation_id="updateTitle")
def update_title(request: AtualizarCargoRequest):
    """
    Atualiza o cargo de um colaborador com base no ID.
    """
    conn = get_db_connection()
    res = conn.execute(
        f"UPDATE {TABELA} SET cargo = ? WHERE id = ?",
        (request.novo_cargo, request.id)
    )
    conn.commit()
    conn.close()

    if res.rowcount == 0:
        raise HTTPException(404, "Colaborador não encontrado")
    return {"message": "Cargo atualizado com sucesso", "cargo": request.novo_cargo}


@router.put("/update-address", operation_id="updateAddress")
def update_address(request: AtualizarEnderecoRequest):
    """
    Atualiza o endereço de um colaborador com base no ID.
    """
    conn = get_db_connection()
    res = conn.execute(
        f"UPDATE {TABELA} SET endereco = ? WHERE id = ?",
        (request.novo_endereco, request.id)
    )
    conn.commit()
    conn.close()

    if res.rowcount == 0:
        raise HTTPException(404, "Colaborador não encontrado")
    return {"message": "Endereço atualizado com sucesso", "endereco": request.novo_endereco}