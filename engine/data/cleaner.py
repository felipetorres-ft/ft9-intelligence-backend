class DataCleaner:
    def limpar(self, msgs):
        limpas = []
        vistos = set()
        for m in msgs:
            chave = (m["timestamp"], m["content"])
            if chave not in vistos:
                vistos.add(chave)
                limpas.append(m)
        return limpas
