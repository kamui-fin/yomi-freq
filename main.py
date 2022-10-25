from pathlib import Path
import pandas as pd
import json
import argparse
import os
import csv
import shutil
import sys

def die(msg):
    print(msg)
    sys.exit()

cli = argparse.ArgumentParser(description='Converts frequency lists to yomichan-compatible dictionaries')

cli.add_argument('-i',
                '--input',
                help='a supported frequency list file',
                required=True)
cli.add_argument('-o',
                '--output',
                help='directory where output dictionary is stored',
                default=os.path.abspath(os.getcwd()))
cli.add_argument("-n",
                "--name",
                help="custom name for dictionary - default: input file name")
cli.add_argument("-r",
                "--revision",
                help="custom revision name for metadata - default: freq",
                default="freq")
cli.add_argument("-l",
                "--limit",
                help="limit number of entries in dictionary - default: 100,000",
                default=100_000,
                type=int)
cli.add_argument("-c",
                "--chunksize",
                help="custom size for each chunk during processing: default: 10,000 ",
                default=10_0000,
                type=int)

args = cli.parse_args()

input_file = Path(args.input)
root_dir = Path(args.output)
name = args.name or input_file.name
chunksize = args.chunksize
limit = args.limit
revision = args.revision

if not input_file.exists():
    die('Invalid path to frequency file')
if not root_dir.exists():
    root_dir = input_file.parent

output_dir = root_dir / name
output_dir.mkdir(exist_ok=True)

def get_delimiter(file_path, bytes = 4096):
    sniffer = csv.Sniffer()
    data = open(file_path, "r").read(bytes)
    delimiter = sniffer.sniff(data).delimiter
    return delimiter

def output_term_bank(df, num, prev_total = 0):
    output_file = output_dir / f"term_meta_bank_{num}.json"

    df = df.reset_index() 

    data = []
    processed = 0
    for _, row in df.iterrows():
        processed += 1
        entry = [row["word"], "freq", curr]
        data.append(entry)
        if prev_total + processed >= limit: 
            break

    with open(output_file, mode="w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    return processed

def create_header():
    # dict metadata
    header = {"title": name, "format": 3, "revision": revision}
    output_file = output_dir / "index.json"
    output_file.write_text(json.dumps(header))

print("Created dictionary metadata...")
create_header()

print("Loading input frequency file...")
data = pd.read_csv(input_file, sep=get_delimiter(input_file), header = None, chunksize=chunksize)
curr = 1
for index, chunk in enumerate(data):
    chunk.columns = ["word", "frequency"]
    curr += output_term_bank(chunk, index + 1, curr)
    if curr >= limit:
        break

print(f"Processed {curr} entries")
print("Building archive...")
shutil.make_archive(str(root_dir / name), 'zip', output_dir)
shutil.rmtree(output_dir)
print("Cleaning up...")
print("Success!")
