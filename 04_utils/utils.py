import polars as pl


def name_finder(text, punctuation = [',','.',';',':','!','?']):
    """
    Function to extract the name of the speaking character from the left context provided by SketchEngine.
    It does so by looking for words fully capitalized, as that's how names are marked in the raw corpus.

    Variables:
    - text (str): The left context provided by SketchEngine
    - punctuation (list(str)): list containing punctuation signs to be cleaned out of text

    Returns:
    - caps (str): The detected name of the character, if no name is found returns None.
    """
    # Get rid of half sentences in the left context and from the end of sentence marker.
    paragraphs = text.split('<s>')
    paragraphs_full = ''.join(paragraphs[1:]).split('</s>')
    text = ' '.join(paragraphs_full)
    # Remove punctuation from text.
    for char in punctuation:
        text = text.replace(char, '')
    text = text.replace('\n', ' ')
    words = text.split(' ')
    caps = ['|']
    previous_was_caps = False
    # Search for words fully in uppercase that are longer than a single letter.
    for word in words:
        if (word == word.upper()) & (len(word) > 1):
            caps.append(word)
            previous_was_caps = True
            continue
        # In case there are more than one name in the captured context, select the last to appear.
        if previous_was_caps:
            caps.append('|')
            previous_was_caps = False
    # print(caps)
    if caps[-1] == '|':
        caps = caps[:-1]
    caps = ' '.join(caps)
    caps = caps.split('|')[-1].strip()
    # If there are none return a null value to make forward filling easier.
    if caps == '':
        caps = None
    return caps

def low_context_name_finder(text, raw_text, match_text_length, punctuation = [',','.',';',':','!','?']):
    """
    Function able to detect the character on instances in which the context provided by SketchEngine
    doesn't include the name of the character speaking.
    It does so by matching a fragment of the given context in raw text.

    Variables:
    - text (str): The left context provided by SketchEngine
    - raw_text (str): The raw corpus to look for the character name in case it's not included in text
    - match_text_length (int): amount of characters from text (starting from the end) that will be used 
                               to match with raw_text
    - punctuation (list(str)): list containing punctuation signs to be cleaned out of text

    Returns:
    - name (str): The detected name of the character, if no name is found returns None.
    """
    # Since polars runs this through all rows of the table regardless of the .when()
    # only actually run the whole function when name_finder 
    name = name_finder(text)
    if name == None:
        # Format the raw text to facilitate matching with the context.
        raw_text_formatted = raw_text.replace('\n',' ').replace('…','...').replace('‘',"'").strip()
        # Format and trim context to facilitate matching with the raw text.
        text = text.replace('<s>','').replace('</s>','').replace('  ',' ')\
                   .replace("''","'").replace("' ","'")[-match_text_length:].strip()

        for punct in punctuation:
            text = text.replace(punct, punct + ' ').replace(punct,'')

        text = text.split(' ')
        text = [word for word in text if word != '']
        text = ' '.join(text)

        # Get left context by splitting the raw text by the context
        new_context = raw_text_formatted.split(text)
        # If there's a match, grab the context and run it through the base name_finder to get the character.
        if len(new_context) == 2:
            new_context = new_context[0]
            name = name_finder(new_context)
            return name
        # Otherwise print the context for debugging and return a null value.
        else:
            print(text)
            print(len(new_context))
            return None
    else: 
        return name