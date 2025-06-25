import os

for fname in os.listdir('./'):
    if fname.endswith('.md'):
        os.rename(fname, fname[:3] + str(hash(fname)) + '.md')