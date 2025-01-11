# ui/utils/text_processor.py

class TextProcessor:
    def __init__(self):
        pass

    def count_text_properties(self, text):
        tokens = len(text.split())
        characters = len(text)
        lines = len(text.splitlines())

        return tokens, characters, lines
    def count_tokens(self, text):
         return len(text.split())

    def count_characters(self, text):
        return len(text)
    
    def count_lines(self, text):
        return len(text.splitlines())