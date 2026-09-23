def remove_duplicates_preserve_order(items):
    seen = set()
    result = []
    for x in items:
        if x not in seen:
            seen.add(x)
            result.append(x)
    return result

if __name__ == "__main__":
    result = remove_duplicates_preserve_order([3, 1, 2, 3, 1, 4])
    print(result)