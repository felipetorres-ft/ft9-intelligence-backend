# services/broadcast_service.py

import csv
import io
import asyncio
import httpx
import logging

from config import settings

logger = logging.getLogger(__name__)

LOTE_TAMANHO = 50
INTERVALO_ENTRE_LOTES = 8  # segundos


async def enviar_mensagem_texto(client: httpx.AsyncClient, numero: str, nome: str, clinica: str):
    """
    Envia uma mensagem de texto simples via Z-API (sem template oficial).
    """
    url = f"{settings.ZAPI_BASE_URL}/instances/{settings.ZAPI_INSTANCE_ID}/token/{settings.ZAPI_TOKEN}/send-text"
    
    headers = {
        "Content-Type": "application/json",
        "Client-Token": settings.ZAPI_CLIENT_TOKEN
    }

    mensagem = (
        f"Bom dia, Dr. {nome}! Aqui é a Camila, da equipe do Felipe Torres. 😊\n\n"
        "Estamos retomando contato com alguns profissionais que já fizeram parte da nossa jornada e o seu nome "
        "apareceu aqui na nossa lista.\n\n"
        "O Felipe abriu algumas conversas individuais (apenas algumas vagas nas próximas 2 semanas) para uma "
        "mentoria de 2 horas focada em estratégias práticas para conquistar novos clientes e aumentar a retenção "
        "dos atuais.\n\n"
        "Quer que eu te envie os horários disponíveis?"
    )

    payload = {
        "phone": numero,
        "message": mensagem,
    }

    try:
        resp = await client.post(url, json=payload, headers=headers, timeout=30)
        logger.info(f"[BROADCAST-TEXTO] Enviado para {numero} | Status: {resp.status_code} | Resp: {resp.text}")
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"[BROADCAST-TEXTO] Erro ao enviar para {numero}: {e}")


async def process_csv_and_broadcast(csv_content: bytes):
    """
    Processa o CSV e dispara mensagens em lotes, em background.
    """
    logger.info("[BROADCAST] Iniciando processamento do CSV (texto simples)")

    try:
        decoded = csv_content.decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(decoded))

        contatos = []
        for row in csv_reader:
            # Aceitar tanto formato antigo (numero/nome/clinica) quanto novo (phone/name/custom1)
            numero = (row.get("numero") or row.get("phone") or "").strip()
            nome = (row.get("nome") or row.get("name") or "").strip() or "Cliente"
            clinica = (row.get("clinica") or row.get("custom1") or "FT9").strip()

            if not numero:
                logger.warning(f"[BROADCAST] Linha ignorada sem número: {row}")
                continue

            contatos.append(
                {
                    "numero": numero,
                    "nome": nome,
                    "clinica": clinica,
                }
            )

        total = len(contatos)
        if total == 0:
            logger.warning("[BROADCAST] Nenhum contato válido encontrado no CSV.")
            return

        logger.info(f"[BROADCAST] Total de contatos para envio: {total}")

        async with httpx.AsyncClient() as client:
            for i in range(0, total, LOTE_TAMANHO):
                lote = contatos[i : i + LOTE_TAMANHO]
                num_lote = (i // LOTE_TAMANHO) + 1
                logger.info(f"[BROADCAST] Enviando lote {num_lote} com {len(lote)} contatos")

                tasks = []
                for contato in lote:
                    tasks.append(
                        enviar_mensagem_texto(
                            client,
                            numero=contato["numero"],
                            nome=contato["nome"],
                            clinica=contato["clinica"],
                        )
                    )

                await asyncio.gather(*tasks, return_exceptions=True)

                if i + LOTE_TAMANHO < total:
                    logger.info(
                        f"[BROADCAST] Aguardando {INTERVALO_ENTRE_LOTES}s antes do próximo lote..."
                    )
                    await asyncio.sleep(INTERVALO_ENTRE_LOTES)

        logger.info("[BROADCAST] Processamento concluído com sucesso (texto simples).")

    except Exception as e:
        logger.error(f"[BROADCAST] Erro ao processar broadcast: {e}")
