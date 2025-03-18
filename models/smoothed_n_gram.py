import random
import re
from collections import defaultdict


class NGramMarkovChain:
    def __init__(self, n=2, alpha=1.0):
        """
        Initialize an n-gram Markov chain model with Laplace smoothing.

        Args:
            n (int): The number of words to use as context for prediction (default: 2)
            alpha (float): Smoothing parameter for Laplace smoothing (default: 1.0)
        """
        self.n = n
        self.alpha = alpha
        self.transitions = defaultdict(lambda: defaultdict(int))
        self.starting_ngrams = []
        self.vocabulary = set()

    def _get_ngrams(self, words):
        """Generate n-grams from a list of words."""
        return [tuple(words[i : i + self.n]) for i in range(len(words) - self.n + 1)]

    def train(self, text):
        """Train the Markov chain on the provided text."""
        words = re.findall(r"\b\w+\b", text.lower())

        self.vocabulary.update(words)

        if len(words) < self.n + 1:
            print(f"Warning: Text too short to train {self.n}-gram model")
            return

        self.starting_ngrams.append(tuple(words[: self.n]))

        ngrams = self._get_ngrams(words)
        for i in range(len(ngrams) - 1):
            current_ngram = ngrams[i]
            next_word = words[i + self.n]
            self.transitions[current_ngram][next_word] += 1

    def predict_next_word(self, context):
        """
        Predict the next word given the context (last n words) using only Laplace smoothing.

        Args:
            context: List or tuple of the last n words
        """
        if isinstance(context, list):
            context = tuple(context)

        if len(context) < self.n:
            print(f"Warning: Context needs {self.n} words")
            return None
        elif len(context) > self.n:
            context = context[-self.n :]

        if context not in self.transitions:
            if self.vocabulary:
                return random.choice(list(self.vocabulary))
            elif self.starting_ngrams:
                random_start = random.choice(self.starting_ngrams)
                return random_start[-1]
            return None

        word_counts = self.transitions[context]
        total_count = sum(word_counts.values())

        probabilities = {}

        for word in self.vocabulary:
            count = word_counts.get(word, 0)

            probabilities[word] = (count + self.alpha) / (
                total_count + self.alpha * len(self.vocabulary)
            )

        words = list(probabilities.keys())
        probs = list(probabilities.values())
        return random.choices(words, weights=probs, k=1)[0]

    def generate_sentence(self, start_words=None, max_length=25):
        """
        Generate a sentence starting with the given words.

        Args:
            start_words: List of words to start the sentence with
            max_length: Maximum length of the generated sentence
        """
        if not self.transitions:
            return "Model not trained yet."

        if start_words is None or len(start_words) < self.n:
            if not self.starting_ngrams:
                return "Model not trained properly."

            if start_words is None:
                start_ngram = random.choice(self.starting_ngrams)
                sentence = list(start_ngram)
            else:
                sentence = list(start_words)

                while len(sentence) < self.n:
                    random_start = random.choice(self.starting_ngrams)
                    sentence.append(random_start[len(sentence)])
        else:
            if len(start_words) > self.n:
                start_words = start_words[-self.n :]

            sentence = list(start_words)

        for _ in range(max_length - len(sentence)):
            current_context = tuple(sentence[-self.n :])
            next_word = self.predict_next_word(current_context)

            if next_word is None:
                break

            sentence.append(next_word)

        return " ".join(sentence)

    def train_on_file(self, file_path):
        """Train the model on text from a file."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
            self.train(text)
            return True
        except Exception as e:

            return False


if __name__ == "__main__":
    model = NGramMarkovChain(n=3, alpha=0.0001)
    model.train_on_file("conversation_datasets/cleaned_files/cleaned_dailydialog.txt")

    sentence = model.generate_sentence()
    print(sentence)
