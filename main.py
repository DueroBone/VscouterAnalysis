import Parser
import CLI


def main():
    match_data = Parser.parse_folder("Data")  # type: ignore
    if match_data is None:
        raise Exception("No match data parsed.")
    # Display.compare_team_scores(list(match_data.values()))
    CLI.run_cli(match_data)
    pass


if __name__ == "__main__":
    main()
