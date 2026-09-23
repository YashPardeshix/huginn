def truncate_sentence(s, k):
    words = s.split(" ")
    return " ".join(words[:k])

if __name__ == "__main__":
    result = truncate_sentence("Hello world and welcome to Huginn", 4)
    print(result)