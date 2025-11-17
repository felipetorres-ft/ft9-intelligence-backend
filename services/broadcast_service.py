# services/broadcast_service.py

import csv
import io
import asyncio
import httpx

import logging

logger = logging.getLogger(__name__)
from config import settings

LOTE_TAMANHO = 50
INTERVALO_ENTRE_LOTES = 8  # segundos

# Mensagem padrão do broadcast
MENSAGEM_TEMPLATE = """Olá {nome}! 👋

Aqui é da equipe {clinica}.

Estamos entrando em contato para oferecer uma oportunidade especial de revisão e otimização para 2025.

🎯 *O que podemos fazer por você:*
• Análise completa da sua situação atual
• Identificação de oportunidades de crescimento
• Planejamento estratégico para 2025

📅 *Que tal agendar uma conversa?*

Responda esta mensagem e vamos encontrar o melhor horário para você!

Equipe {clinica} 🚀"""


async def enviar_mensagem_template(client: httpx.AsyncClient, numero: str, nome: str, clinica: str):
    url = f"{settings.ZAPI_BASE_URL}/instances/{settings.ZAPI_INSTANCE_ID}/token/{settings.ZAPI_TOKEN}/send-text"

    # Substituir variáveis na mensagem
    mensagem = MENSAGEM_TEMPLATE.format(nome=nome, clinica=clinica)

    payload = {
        "phone": numero,
        "message": mensagem
    }

    try:
        resp = await client.post(url, json=payload, timeout=30)
        logger.info(f"[BROADCAST] Enviado para {numero} | Status: {resp.status_code} | Resp: {resp.text}")
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        logger.error(f"[BROADCAST] Erro HTTP ao enviar para {numero}: {e}")
    except Exception as e:
        logger.error(f"[BROADCAST] Erro inesperado ao enviar para {numero}: {e}")


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
