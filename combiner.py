"""
Scratch file to experiment with multi-freq list features
"""

# load all datasets
# df = [
#     pd.read_csv("csv1", sep="	", header=None, usecols=[0], names=["Word"]),
#     pd.read_csv("csv2", sep="	", header=None, usecols=[0], names=["Word"]),
# ]

# # df['Frequency'] = np.arange(len(core))

# # df = pd.concat(df, axis=0).sort_values(["Word"])

# # filtering
# garbage = re.compile(r'^[\u3041-\u3096\u30A0-\u30FF\u2E80-\u2FD5\uFF5F-\uFF9F\u3000-\u303F\uFF01-\uFF5E\u31F0-\u31FF\u3220-\u3243\u3280-\u337F]$')

# def regex_filter(val):
#     res = bool(re.search(garbage, val)) or val in printable
#     return not res

# final_freq['Word'].replace(to_replace="-?[a-zA-Z0-9]*", value="", regex=True, inplace=True)
# final_freq = final_freq[final_freq['Word'].apply(regex_filter)]
# final_freq = final_freq.groupby(["Word"]).mean().sort_values(["Frequency"]).round(2)
# final_freq.to_csv("ultimate_frequencylist.csv")
