"""
Modify rlcompleter.Completer class such that it does not show hidden
attributes.
"""

import readline
import rlcompleter

class ParselTongueCompleter(rlcompleter.Completer):
    def attr_matches(self, text):
        words = rlcompleter.Completer.attr_matches(self, text)
        new_words = []
        for word in words:
            pos = word.rfind('.')
            if pos > 0:
                if word.find('._', pos) == pos:
                    continue;
            new_words.append(word)
        return new_words

readline.set_completer(ParselTongueCompleter().complete)
