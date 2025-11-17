"""
FT9 Intelligence - Broadcast Service
Serviço principal para disparo massivo via Z-API com anti-banimento
"""

import csv
import io
import time
import asyncio
from fastapi import UploadFile
import logging

from services.zapi_send_service import enviar_template

logger = logging.getLogger(__name__)

# Configurações de segurança anti-banimento
LOTE_TAMANHO = 50  # Mensagens por lote
INTERVALO_ENTRE_LOTES = 8  # Segundos entre lotes (ideal: 6-12s)
LIMITE_DIARIO = 500  # Limite de mensagens por dia

# Template padrão (deve ser criado na Meta)
TEMPLATE_ID = "revisao_de_contrato_2025"


async def enviar_mensagem(numero: str, nome: str, clinica: str) -> dict:
    """
    Envia mensagem individual com template
    
    Args:
        numero: Número WhatsApp com DDI+DDD
        nome: Nome do contato
        clinica: Nome da clínica
        
    Returns:
        dict: Response da Z-API
    """
    variables = {
        "nome": nome,
        "clinica": clinica
    }
    
    buttons = [
        {"id": "btn_agendar", "title": "Agendar reunião"},
        {"id": "btn_info", "title": "Quero mais informações"},
        {"id": "btn_parar", "title": "Não quero receber"}
    ]
    
    result = await enviar_template(numero, TEMPLATE_ID, variables, buttons)
    logger.info(f"Enviando para {numero} ({nome}): {result}")
    return result


async def process_csv_and_broadcast(csv_content: bytes):
    """
    Processa CSV e executa broadcast em lotes
    
    Args:
        csv_file: Arquivo CSV com colunas: nome, numero, clinica (opcional)
        
    CSV Format:
        nome,numero,clinica
        João Silva,5511999999999,Clínica ABC
        Maria Santos,5511988888888,Clínica XYZ
    """
    try:
        # Decodificar CSV (conteúdo já foi lido)
        decoded = csv_content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded))

        # Extrair contatos
        contatos = []
        for row in csv_reader:
            contatos.append({
                "nome": row.get("nome", ""),
                "numero": row.get("numero", ""),
                "clinica": row.get("clinica", "FT9")
            })

        total = len(contatos)
        logger.info(f"📊 Total de contatos: {total}")

        # Validar limite diário
        if total > LIMITE_DIARIO:
            logger.warning(f"⚠️ Total de contatos ({total}) excede limite diário ({LIMITE_DIARIO})")
            logger.info(f"Processando apenas os primeiros {LIMITE_DIARIO} contatos")
            contatos = contatos[:LIMITE_DIARIO]
            total = LIMITE_DIARIO

        # Processar em lotes
        enviados = 0
        falhas = 0
        
        for i in range(0, total, LOTE_TAMANHO):
            lote = contatos[i:i + LOTE_TAMANHO]
            lote_num = (i // LOTE_TAMANHO) + 1
            total_lotes = (total + LOTE_TAMANHO - 1) // LOTE_TAMANHO
            
            logger.info(f"📤 Enviando lote {lote_num}/{total_lotes} com {len(lote)} contatos...")

            # Enviar mensagens do lote
            for contato in lote:
                try:
                    await enviar_mensagem(
                        contato["numero"],
                        contato["nome"],
                        contato["clinica"]
                    )
                    enviados += 1
                except Exception as e:
                    logger.error(f"❌ Erro ao enviar para {contato['numero']}: {e}")
                    falhas += 1
            
            # Aguardar intervalo anti-spam (exceto no último lote)
            if i + LOTE_TAMANHO < total:
                logger.info(f"⏳ Aguardando {INTERVALO_ENTRE_LOTES}s (anti-spam)...")
                await asyncio.sleep(INTERVALO_ENTRE_LOTES)

        # Relatório final
        logger.info("=" * 50)
        logger.info("✅ BROADCAST CONCLUÍDO COM SUCESSO!")
        logger.info(f"📊 Total: {total} | Enviados: {enviados} | Falhas: {falhas}")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"❌ Erro no processamento do broadcast: {e}")
        raise
