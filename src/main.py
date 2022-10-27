from pathlib import Path
import pandas as pd
import json
import argparse
import os
import csv
import shutil
import sys
import re

def die(msg):
    print(msg)
    sys.exit()

cli = argparse.ArgumentParser(description='Converts frequency lists to yomichan-compatible dictionaries')

cli.add_argument('-i',
                '--input',
                help='a supported frequency list file',
                nargs="+",
                required=True)
cli.add_argument('-o',
                '--output',
                help='directory where output dictionary is stored',
                default=os.path.abspath(os.getcwd()))
cli.add_argument("-n",
                "--name",
                help="name for dictionary",
                required=True)
cli.add_argument("-r",
                "--revision",
                help="custom revision name for metadata - default: freq",
                default="freq")
cli.add_argument("-l",
                "--limit",
                help="limit number of entries in dictionary - default: None",
                default=100_000,
                type=int)
cli.add_argument("-c",
                "--chunksize",
                help="custom size for each chunk during processing: default: 10,000",
                type=int)
cli.add_argument("-p",
                "--postprocess",
                help="remove and clean up entries with irrelevant/garbage words with regex",
                type=str)

args = cli.parse_args()

inputs = [path for path in [Path(input) for input in args.input] if path.exists()]
name = args.name
root_dir = Path(args.output)
chunksize = args.chunksize
limit = args.limit
revision = args.revision
garbage_regex = args.postprocess

if not inputs:
    die('Invalid path(s) to frequency file')
if not root_dir.exists():
    die("Output directory does not exist")

if not chunksize:
    if limit:
        chunksize = limit // 10
    else:
        chunksize = 10_000

if garbage_regex:
    try:
        garbage_regex = re.compile(garbage_regex)
    except re.error:
        die("Invalid regex supplied")

output_dir = root_dir / name
output_dir.mkdir(exist_ok=True)

def get_delimiter(file_path, bytes = 4096):
    sniffer = csv.Sniffer()
    data = open(file_path, "r").read(bytes)
    try:
        delimiter = sniffer.sniff(data).delimiter
        return delimiter
    except:
        return "\r"

def regex_filter(val):
    return not bool(re.search(garbage_regex, val))

def output_term_bank(df, num, prev_total = 0):
    output_file = output_dir / f"term_meta_bank_{num}.json"

    df = df.reset_index() 

    data = []
    processed = 0
    for _, row in df.iterrows():
        processed += 1
        entry = [row["word"], name, row["freq"]]
        data.append(entry)
        if limit and prev_total + processed >= limit: 
            break

    with open(output_file, mode="w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    return processed

def create_header():
    # dict metadata
    header = {"title": name, "format": 3, "revision": revision}
    output_file = output_dir / "index.json"
    output_file.write_text(json.dumps(header))

def chunkit(df): 
    num_chunks = len(df) // chunksize
    if len(df) % chunksize != 0:
        num_chunks += 1
    for i in range(num_chunks):
        yield df[i*chunksize:(i + 1) * chunksize]

print("Creating dictionary metadata...")
create_header()

print("Loading input frequency file...")
df_list = [pd.read_csv(input_file, sep=get_delimiter(input_file), names=["word"], usecols=[0], header=None) for input_file in inputs]
df_list = [df.assign(freq=range(1, len(df) + 1)) for df in df_list]
df = pd.concat(df_list, axis=0)
df = df.groupby(["word"]).mean().sort_values(["freq"]).round()
df = df.freq.astype(int)

if garbage_regex:
    df = df[df['word'].apply(regex_filter)]

curr = 1
for index, chunk in enumerate(chunkit(df)):
    curr += output_term_bank(chunk, index + 1, curr)
    if limit and curr >= limit:
        break

print(f"Processed {curr} entries.")
print("Building archive...")
shutil.make_archive(str(root_dir / name), 'zip', output_dir)
print("Cleaning up...")
shutil.rmtree(output_dir)
print("Done!")
