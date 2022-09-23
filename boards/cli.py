"""Console script for boards."""

import fire


def help():
    print("boards")
    print("=" * len("boards"))
    print("industry boards and concept boards")


def main():
    fire.Fire({"help": help})


if __name__ == "__main__":
    main()  # pragma: no cover
