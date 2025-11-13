class WhatsAppGateway:
    def processar_evento(self, payload):
        msg = payload.get("entry",[{}])[0].get("changes",[{}])[0].get("value",{}).get("messages",[{}])[0]
        usuario = msg.get("from","")
        texto = msg.get("text",{}).get("body","")
        return usuario, texto
