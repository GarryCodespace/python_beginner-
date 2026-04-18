import string
from collections import Counter
import matplotlib.pyplot as plt


def analyze_text(file_path):
    # Step 1: Read file
    # open this file and name it file 
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    # Step 2: Sentence count
    sentences = text.split(".")
    sentence_count = 0

    for s in sentences:
        if s.strip() != "":
            sentence_count += 1

    # Step 3: Clean text
    text = text.lower()

    # remove punctuation
    for char in string.punctuation:
        text = text.replace(char, "")

    words = text.split()

    # Step 4: Remove common words (stopwords)
    stopwords = {
        "the", "is", "and", "in", "to", "of", "a", "that",
        "it", "on", "for", "as", "with", "was", "were", "be"
    }

    filtered_words = []

    for word in words:
        if word not in stopwords:
            filtered_words.append(word)
            
    # Step 5: Word count
    word_count = len(filtered_words)

    # Step 6: Count frequency
    word_freq = Counter(filtered_words)

    # Step 7: Most common words
    most_common = word_freq.most_common(10)

    # Output results
    print(f"Total words (filtered): {word_count}")
    print(f"Total sentences: {sentence_count}")
    print("\nMost common words:")
    for word, count in most_common:
        print(f"{word}: {count}")

    return word_freq


def plot_word_frequency(word_freq):
    # Take top 10 words
    common = word_freq.most_common(10)

    words = [w for w, c in common]
    counts = [c for w, c in common]

    plt.figure()
    plt.bar(words, counts)
    plt.xlabel("Words")
    plt.ylabel("Frequency")
    plt.title("Top 10 Word Frequencies")
    plt.show()


# ---- Run ----
file_path = "sample.txt"  # change to your file
freq = analyze_text(file_path)

# Optional: plot
plot_word_frequency(freq)