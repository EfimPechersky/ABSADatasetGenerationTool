import pymorphy3
import re
"""Поиск подстроки в тексте"""
def find_russian_substring_simple(text, substring):
        morph = pymorphy3.MorphAnalyzer()

        # Лемматизируем подстроку
        sub_cleaned = re.sub(r'[^\w\s-]', ' ', substring.lower())
        sub_words = sub_cleaned.split()
        sub_lemmas = [morph.parse(word)[0].normal_form for word in sub_words if word]

        # Лемматизируем текст
        text_cleaned = re.sub(r'[^\w\s-]', ' ', text.lower())
        text_words = text_cleaned.split()
        text_lemmas = [morph.parse(word)[0].normal_form for word in text_words if word]

        positions = []

        if not sub_lemmas:
            return positions

        # Поиск
        if len(sub_lemmas) == 1:
            target = sub_lemmas[0]
            for i, lemma in enumerate(text_lemmas):
                if lemma == target:
                    # Ищем позицию исходного слова
                    word = text_words[i]
                    pattern = r'\b' + re.escape(word) + r'\b'

                    for match in re.finditer(pattern, text.lower()):
                        positions.append(match.span())

        else:
            sub_len = len(sub_lemmas)
            for i in range(len(text_lemmas) - sub_len + 1):
                if text_lemmas[i:i+sub_len] == sub_lemmas:
                    # Находим позицию фразы
                    phrase_words = text_words[i:i+sub_len]
                    pattern = r'\s*'.join([r'\b' + re.escape(w) + r'\b' for w in phrase_words])

                    for match in re.finditer(pattern, text.lower()):
                        positions.append(match.span())

        return positions