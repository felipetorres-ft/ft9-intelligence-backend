class KeywordFinder:
    def buscar(self, msgs, keyword):
        return [m for m in msgs if keyword.lower() in m["content"].lower()]
