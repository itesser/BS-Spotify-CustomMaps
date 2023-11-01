import pandas as pd

def get_tags(df, qty=20):
    tags = df['tags']
    tag_list = list(tags)
    for i in range(len(tag_list)):
        tag_list[i] = tag_list[i].replace('[','').replace(']','').replace("'","")
    bulk_tags = ""
    for i in range(len(tag_list)):
        if tag_list[i] == 'none':
            pass
        else:
            bulk_tags += tag_list[i]
            bulk_tags += ', '
    tags_conformed = bulk_tags.split(',')
    tag_df = pd.DataFrame(tags_conformed)
    output_tags = list(tag_df.value_counts().reset_index().head(qty)[0])
    for i in range(len(output_tags)):
        output_tags[i] = output_tags[i].strip()
    return output_tags