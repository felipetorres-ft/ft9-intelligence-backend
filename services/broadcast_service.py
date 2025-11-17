# services/broadcast_service.py

import csv
import io
import asyncio
import httpx

import logging

logger = logging.getLogger(__name__)
from config import ZAPI_INSTANCE_ID, ZAPI_TOKEN, ZAPI_BASE_URL

LOTE_TAMANHO = 50
INTERVALO_ENTRE_LOTES = 8  # segundos

TEMPLATE_ID = "revisao_de_contrato_2025"  # ajustar se o nome for outro


async def enviar_mensagem_template(client: httpx.AsyncClient, numero: str, nome: str, clinica: str):
    url = f"{ZAPI_BASE_URL}/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-template"

    payload = {
        "phone": numero,
        "templateId": TEMPLATE_ID,
        "variables": {
            "nome": nome,
            "clinica": clinica
        },
        "buttons": [
            {"id": "btn_agendar", "title": "Agendar reunião"},
            {"id": "btn_info", "title": "Quero mais informações"},
            {"id": "btn_parar", "title": "Não tenho interesse"}
        ]
    }

    try:
        resp = await client.post(url, json=payload, timeout=20)
        logger.info(f"[BROADCAST] Enviado para {numero} | Status: {resp.status_code} | Resp: {resp.text}")
    except Exception as e:
        logger.error(f"[BROADCAST] Erro ao enviar para {numero}: {e}")


async def process_csv_and_broadcast(csv_content: bytes):
    """
    Esta função roda em background.
    Ela NÃO deve travar o endpoint.
    """
    logger.info("[BROADCAST] Iniciando processamento do CSV")

    try:
        decoded = csv_content.decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(decoded))

        contatos = []
        for row in csv_reader:
            numero = (row.get("numero") or "").strip()
            nome = (row.get("nome") or "").strip()
            clinica = (row.get("clinica") or "FT9").strip()

            if not numero:
                logger.warning(f"[BROADCAST] Linha ignorada sem número: {row}")
                continue

            contatos.append({
                "numero": numero,
                "nome": nome or "Cliente",
                "clinica": clinica
            })

        total = len(contatos)
        if total == 0:
            logger.warning("[BROADCAST] Nenhum contato válido encontrado no CSV.")
            return

        logger.info(f"[BROADCAST] Total de contatos para envio: {total}")

        async with httpx.AsyncClient() as client:
            # Enviar em lotes
            for i in range(0, total, LOTE_TAMANHO):
                lote = contatos[i:i + LOTE_TAMANHO]
                num_lote = (i // LOTE_TAMANHO) + 1
                logger.info(f"[BROADCAST] Enviando lote {num_lote} com {len(lote)} contatos")

                # Envia um lote em paralelo
                tasks = []
                for contato in lote:
                    tasks.append(
                        enviar_mensagem_template(
                            client,
                            numero=contato["numero"],
                            nome=contato["nome"],
                            clinica=contato["clinica"],
                        )
                    )

                # Espera todas as mensagens deste lote terminarem
                await asyncio.gather(*tasks, return_exceptions=True)

                # Se ainda houver mais contatos, espera o intervalo
                if i + LOTE_TAMANHO < total:
                    logger.info(f"[BROADCAST] Aguardando {INTERVALO_ENTRE_LOTES}s antes do próximo lote...")
                    await asyncio.sleep(INTERVALO_ENTRE_LOTES)

        logger.info("[BROADCAST] Processamento concluído com sucesso.")

    except Exception as e:
        logger.error(f"[BROADCAST] Erro ao processar broadcast: {e}")
