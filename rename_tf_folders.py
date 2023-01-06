#!/usr/bin/env pipenv-shebang
# coding:utf8
import sys, os
import argparse
import logging
import glob
import pprint

logging.basicConfig(level=logging.INFO)


def parse_args_or_exit():
    parser = argparse.ArgumentParser(
        description="rename terraform folders to make a clean numerotation."
    )
    parser.add_argument(
        "--tf_folders_path",
        type=str,
        help="the path of the terraform folder (can be absolute or relative)",
    )
    parser.add_argument(
        "--exclude_folders",
        type=str,
        help="exclude folders names (comma separate values)",
    )

    args = parser.parse_args()
    return check_args_valid_or_exit(parser, args)


def check_args_valid_or_exit(parser, args):
    if not args.tf_folders_path:
        logging.error("arg --tf_folders_path is missing, exiting early ...")
        parser.print_help()
        sys.exit(-1)

    if os.path.isdir(args.tf_folders_path):
        args.tf_folders_path = os.path.abspath(args.tf_folders_path)
    else:
        logging.error(
            f"arg --tf_folders_path is not a valid folder path, expected valid folder path, get {args.tf_folders_path} ,exiting early ..."
        )
        sys.exit(-1)

    if args.exclude_folders:
        try:
            args.exclude_folders = {
                exclude: os.path.join(args.tf_folders_path, exclude)
                for exclude in args.exclude_folders.split(",")
            }
        except AttributeError:
            args.exclude_folders = []
            args.exclude_folders.append(args.exclude_folders)
    else:
        args.exclude_folders = []
    return args


def check_exclude_folder_existence(args):

    if args.exclude_folders:
      copy_dict = args.exclude_folders.copy()
      logging.info("print exclude folder path(s):\n")
      for folder_name in args.exclude_folders:
          if os.path.exists(args.exclude_folders[folder_name]):
              logging.info(f"exclude folder {args.exclude_folders[folder_name]}")
          else:
              logging.warning(
                  f"{args.exclude_folders[folder_name]} not found, removing from folder exclude list."
              )
              del copy_dict[folder_name]
      args.exclude_folders = copy_dict
      print("\n")
    return args


def yes_no_question(question):
    while True:
        print("\n" + question)
        response = input()
        if response.lower() in ["yes", "y"]:
            return True
        if response.lower() in ["no", "n"]:
            return False


def generate_renum_dict(args):
    folders_to_rename_list = []
    for path in glob.glob(args.tf_folders_path + "/*"):
        if os.path.isdir(path) and os.path.basename(path) not in [
            folder for folder in args.exclude_folders
        ]:
            folders_to_rename_list.append(os.path.basename(path))
        else:
            logging.info(f"exclude folder {path} from renaming list.")

    sorted_folders = sorted(folders_to_rename_list)
    renamed_folder = {}

    for i in range(0, len(sorted_folders)):
        count_string = f"{i:03d}"
        renamed_folder[sorted_folders[i]] = count_string + sorted_folders[i][3:]
    return renamed_folder


def rename_tf_folders(args, renamed_folder):
    for old_folder_name in renamed_folder:
        print(f"renaming {old_folder_name} -> {renamed_folder[old_folder_name]}")
        old_folder_path = os.path.join(args.tf_folders_path, old_folder_name)
        renamed_folder_path = os.path.join(
            args.tf_folders_path, renamed_folder[old_folder_name]
        )

        os.rename(old_folder_path, renamed_folder_path)


def main():
    args = parse_args_or_exit()
    check_exclude_folder_existence(args)
    renamed_folder = generate_renum_dict(args)

    logging.info(f"folders in parent {args.tf_folders_path} will be renamed this way:")
    pprint.pprint(renamed_folder)

    if not yes_no_question("Is this configuration correct [y/n] ?"):
        logging.info("ok then, maybe trying again later? ¯\_(ツ)_/¯")
        sys.exit(-1)

    rename_tf_folders(args, renamed_folder)


if __name__ == "__main__":
    main()
