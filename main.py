from Parser import parse_folder
import Display


def main():
    match_data = parse_folder("Data")
    if match_data is None:
        raise Exception("No match data parsed.")
    Display.compare_team_scores(list(match_data.values()))
    pass


if __name__ == "__main__":
    main()
