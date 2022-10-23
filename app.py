from pathlib import Path
import pandas as pd
import json

CHUNK_SIZE = 40_000
LIMIT = 200_000

VER = 1
DICT_TITLE = "freq"
REVISION = "frequency1"

# OUTPUT_DIR = Path("dict")

def die(msg):
    print(msg)
    sys.exit()

cli = argparse.ArgumentParser(description='Start an audio server for Yomichan')

cli.add_argument('-i',
                '--input',
                nargs = "+",
                metavar='path',
                help='a supported frequency list file',
                required=True)
cli.add_argument('-o',
                '--output',
                nargs = "+",
                metavar='path',
                help='path to the output yomichan frequency dictionary',
                required=True)

args = cli.parse_args()

input_file = Path(args.input)
output_file = Path(args.output)

if not input_file.exists() or input_file.exists():
    die('Invalid path to frequency file')

header = {"title": DICT_TITLE, "format": VER, "revision": REVISION}

curr = 1

def output_term_bank(df, num):
    global curr
    output_file = OUTPUT_DIR / f"term_meta_bank_{num}.json"

    df = df.reset_index() 

    data = []
    for index, row in df.iterrows():
        entry = [row["word"], "freq", curr]
        data.append(entry)
        curr += 1

    with open(output_file, mode="w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def create_header():
    output_file = OUTPUT_DIR / "index.json"
    output_file.write_text(json.dumps(header))

data = pd.read_csv(input_file, sep="\t", header = None, chunksize=CHUNK_SIZE)

create_header()

for index, chunk in enumerate(data):
    chunk.columns = ["word", "frequency"]
    output_term_bank(chunk, index + 1)

    if curr >= LIMIT:
        break
