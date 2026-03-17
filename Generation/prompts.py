"""Класс, содержащий все запросы"""
class Prompts:
    """Описание задачи, помогает погрузить модель в контекст"""
    absa_description="""
        Aspect-Based Sentiment Analysis (ABSA) is a method used to understand people's opinions about specific features or parts (aspects) of a product, service, or topic. It goes beyond simply knowing if the overall sentiment is positive or negative, by identifying opinions about particular aspects.

        Key concepts in ABSA:

        AspectTerm: A word or phrase that refers to a specific feature or part of the entity.
        Example: In the sentence "The camera is excellent," the aspect term is "camera".

        OpinionTerm: A word or phrase that expresses an opinion or sentiment about an aspect.
        Example: In "The camera is excellent," the opinion term is "excellent".

        Sentiment: The overall emotional judgment expressed towards an aspect, usually categorized as positive, negative, or neutral.
        Example: In "The camera is excellent," the sentiment towards the camera is positive.

        Putting it together:
        In the sentence "The battery life is disappointing," the aspect term is "battery life", the opinion term is "disappointing", and the sentiment is negative.
    """

    """Запрос для генерации перефразированных примеров"""
    def get_semantic_paraphrasing_prompt(domain, sentence):
        return f'''Generate 10 review sentences about {domain} that convey a similar meaning to the provided review
        sentence: “{sentence}”. Each sentence should capture the essence of the original review while presenting it in a different way. GENERATED SENTENCES SHULD BE ON RUSSIAN LANGUAGE.START GENERATION WITHOUT ANY PREAMBLE!DONT CHANGE OUTPUT FORMAT!
        Output Format:
        SAMPLE i: generated sentence'''
    
    """Запрос для разметки перефразированных примеров"""
    def get_aspect_annotation_prompt(source_sentence, sentences, aspects):
        prompt = f'''Provide aspect annotations for ten sentences that convey a similar meaning to the given source sentence. The source sentence includes an annotated aspect
        term. Your task is to identify and annotate the aspect term within each of the
        ten sentences, ensuring that the aspect term is a subsequence within its sentence and that carries a similar meaning to the source aspect term.
        START GENERATION WITHOUT ANY PREAMBLE! DONT CHANGE OUTPUT FORMAT!
        TRY TO CAPTURE ALL IMPORTANT ASPECTS IN EACH SENTENCE!
        DONT GENERATE ANY EXPLANATIONS OR CLARIFICATIONS!
        GENERATE SENTIMENTS IN ENGLISH LANGUAGE: Positive, Negative or Neutral!
        DON'T CHANGE DELIMETERS OR OTHER CHARACTERS IN OUTPUT FORMAT, LIKE ":" or ";"!!!
        Just output the aspect of each sentence ONLY IN THE FOLLOWING FORMAT:

        ASPECTS i: aspect term 0 for sentence i : sentiment; aspect term 1 for sentence i : sentiment;...;

        Input:
        Source Sentence: {source_sentence}
        Source Aspects and Sentiments: {aspects}
        '''
        for i in range(0,len(sentences)):
            prompt+=f"Sentence {i}: {sentences[i]}"
        return prompt
    
    '''
    Запрос для генерации примеров при помощи метода комбинации
    '''
    def combination_prompt (domain,example1,aspects1, example2, aspects2):
        examples="<sample>\n"
        examples+="<sentence>\n"
        examples+=example1+"\n"
        examples+="</sentence>\n"
        for i in aspects1:
            examples+="<aspect>\n"
            examples+="<term>\n"
            examples+=i.term+"\n"
            examples+="</term>\n"
            examples+="<sentiment>\n"
            examples+=i.sentiment+"\n"
            examples+="</sentiment>\n"
            examples+="</aspect>\n"
        examples+="</sample>\n"
        examples+="<sample>\n"
        examples+="<sentence>\n"
        examples+=example2+"\n"
        examples+="</sentence>\n"
        for i in aspects2:
            examples+="<aspect>\n"
            examples+="<term>\n"
            examples+=i.term+"\n"
            examples+="</term>\n"
            examples+="<sentiment>\n"
            examples+=i.sentiment+"\n"
            examples+="</sentiment>\n"
            examples+="</aspect>\n"
        examples+="</sample>\n"
        return f'''Given 2 {domain} example reviews with the labels, please combine them to generate 2 diverse sentences ON RUSSIAN LANGUAGE. Label each sentence by extracting the aspect term(s) and determine their corresponding sentiment polarity.
        Requirements:
        - GENERATED REVIEWS SHOULD BE ABOUT {domain}!
        - Keep a consistent style and annotation standard with the examples.
        - Maintain the same format as the examples.
        - Combine the aspects and sentiments of both examples in every generated sentence.
        - BEGIN GENERATION FROM <sample> WITHOUT ANY PREAMBLE.
        - WRITE SENTIMENT IN ENGLISH(negative, positive or neutral).
        WRITE GENERATED SENTENCES ONLY IN THIS FORMAT:
        <sample>
        <sentence>
            "sentence1"
        </sentence>
        <aspect>
            <term>
            "aspect1"
            </term>
            <sentiment>
            "sentiment1"
            </sentiment>
        </aspect>
        <aspect>
            <term>
            "aspect2"
            </term>
            <sentiment>
            "sentiment2"
            </sentiment>
        </aspect>
        </sample>
        <sample>
        <sentence>
            "sentence2"
        </sentence>
        <aspect>
            <term>
            "aspect1"
            </term>
            <sentiment>
            "sentiment1"
            </sentiment>
        </aspect>
        <aspect>
            <term>
            "aspect2"
            </term>
            <sentiment>
            "sentiment2"
            </sentiment>
        </aspect>
        </sample>
        Examples:
        {examples}
        '''