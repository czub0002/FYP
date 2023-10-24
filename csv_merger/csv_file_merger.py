import time

start_time = time.time()

# Example usage to create the metafile
meta_file_name = 'down-trial_index_wiley.txt'
file_prefix = 'down-trial_index_wiley'
file_suffix = '.txt'

header = 'PT AU BA BE GP AF BF CA TI SO SE BS LA DT CT CY CL SP HO DE ID AB C1 C3 RP EM ' \
         'RI OI FU FP FX CR NR TC Z9 U1 U2 PU PI PA SN EI BN J9 JI PD PY VL IS PN SU SI ' \
         'MA BP EP AR DI DL D2 EA PG WC WE SC GA PM OA HC HP DA UT\n'

with open(meta_file_name, 'w') as meta_file:
    meta_file.write(header)

# Open the meta_file in append mode outside the loop
with open(meta_file_name, 'a') as meta_file:
    for i in range(1, 6):  # Start from wiley1 to wiley5
        file_to_append = f'{file_prefix}{i}{file_suffix}'

        with open(file_to_append, 'r') as file:
            content_to_append = file.readlines()[1:]

        meta_file.writelines(content_to_append)

runtime = time.time() - start_time
print(f"Runtime: {runtime:.4f} seconds")