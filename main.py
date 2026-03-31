import Parser
import CLI


def main():
    match_data = Parser.parse_folder("Data")
    if match_data is None:
        raise Exception("No match data parsed.")
    CLI.run_cli(match_data)


if __name__ == "__main__":
    main()
