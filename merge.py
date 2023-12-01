from pointsbet import get_df
from underdog import underdog
import pandas as pd
import numpy as np
import math

if __name__ == "__main__":
    df = get_df()
    UD_final_df = underdog()
    print(df)
    print(UD_final_df)
    merged = pd.merge(UD_final_df, df, left_on = 'stat_type', right_on='prop')
    filtered_df = merged[merged.apply(lambda row: all(word in row['playerName'].split() for word in row['name'].split()), axis=1)]
    filtered_df['odds'] = None
    filtered_df.reset_index(inplace = True, drop = True)
    for i in range(len(filtered_df)):
        line_score = float(filtered_df.loc[i, 'line_score'])
        if line_score < 10:
            if line_score % 1 == 0.5:
                filtered_df.loc[i, 'odds'] = str(filtered_df.loc[i, line_score + 0.5])
            if line_score % 1 == 0:
                filtered_df.loc[i, 'odds'] = str(filtered_df.loc[i, line_score]) + ', ' + str(filtered_df.loc[i, line_score + 1])
        if line_score >= 10:
            lower = 5 * math.floor(line_score / 5)
            upper = 5 + lower
            filtered_df.loc[i, 'odds'] = str(filtered_df.loc[i, lower]) + ', ' + str(filtered_df.loc[i, upper])
    filtered_df = filtered_df[['line_score', 'stat_type', 'name', 'sport', 'playerName', 'prop', 'odds']]
    print(filtered_df)