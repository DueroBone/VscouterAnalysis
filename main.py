from Parser import parse_folder


def main():
    match_data = parse_folder("Data")
    if match_data is None:
        raise Exception("No match data parsed.")
    pass


if __name__ == "__main__":
    main()
