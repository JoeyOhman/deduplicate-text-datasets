# Copyright 2022 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import json
import numpy as np
from collections import defaultdict


def bytes_to_jsonl(loaded_bytes):
    print(loaded_bytes)
    w_split = loaded_bytes.split(b'\xff\xff')
    w_split = [s[4:].decode('utf-8') for s in w_split]
    w_split = [json.dumps({"text": s}, ensure_ascii=False) + "\n" for s in w_split if len(s) > 0]
    # return "\n".join(w_split)
    return "".join(w_split)


def write_bytes(write_ds, bytes_to_write):
    # write_ds.write(bytes_to_write.decode("utf-8", 'ignore'))
    write_ds.write(bytes_to_write)


original = sys.argv[1]
remove_file = sys.argv[2]
deduped = sys.argv[3]

remove = []
fin = open(remove_file)
for line in fin:
    if 'out' in line:
        break
for line in fin:
    remove.append(list(map(int, line.split())))
# remove = remove[::-1]

# Lengths of original docs
sizes = np.frombuffer(open(original + ".size", "rb").read(), dtype=np.uint64)

ds = open(original, "rb")
# new_ds = open(deduped, "w")

remove_ex = defaultdict(list)
ptr = 0
print("sizes")
print(len(sizes))
print(sizes)
# read_bytes = ds.read()
# print(len(read_bytes))
# exit()
# for i, byte_start in enumerate(sizes[:-1]):
for i, byte_start in enumerate(sizes[:-1]):
    byte_end = sizes[i + 1]
    # print("ptr:", ptr)
    # print("len(remove):", len(remove))
    # print("byte start:", byte_start)
    # print("byte end:", byte_end)
    # print("remove[ptr][0]:", remove[ptr][0])
    print("outside:", i)
    while ptr < len(remove) and byte_start <= remove[ptr][0] < byte_end:
        print("inside:", i)
        assert remove[ptr][1] < byte_end + 6
        # The magic value 6 here corresponds to the 4-byte index prefix followed by \xff\xff.
        # remove_ex[i].append((max(int(remove[ptr][0] - byte_start - 6), 0),
        #                      min(int(remove[ptr][1] - byte_start), byte_end - byte_start)))
        remove_ex[i].append((max(int(remove[ptr][0] - byte_start + 3), 0),
                             min(int(remove[ptr][1] - byte_start), byte_end - byte_start)))
        # print(ptr)
        ptr += 1

print(remove_ex)
# print(remove_ex)

# with open("data/my_data.jsonl", 'r') as f:
    # json_lines = f.readlines()
    # text_lines = [json.loads(line.strip())['text'] for line in json_lines]

read_bytes = ds.read()
print(len(read_bytes))
text_lines = [b'\xff\xff' + line for line in read_bytes.split(b'\xff\xff') if len(line.strip()) > 0]
assert len(text_lines) == len(sizes) - 1
for i in range(len(text_lines)):
    print("*" * 50)
    print(i + 1)
    if i in remove_ex:
        print(text_lines[i], "TO REMOVE:")
        for start, end in remove_ex[i][::-1]:
            print(text_lines[i][start:end])
            text_lines[i] = text_lines[i][:start] + text_lines[i][end:]

    text_lines[i] = text_lines[i][6:]

print("Texts:")
for i, t in enumerate(text_lines):
    if len(t) > 0:
        print(f"Text {i}:", t)

with open(deduped, 'w') as f:
    for i, t in enumerate(text_lines):
        if i != 0:
            f.write("\n")
        f.write(json.dumps({"text": t.decode('utf-8')}, ensure_ascii=False))

exit()

print(len(text_lines))
print(remove)
for bytes_to_remove in remove[::-1]:
    start, end = bytes_to_remove
    read_bytes = read_bytes[:start] + read_bytes[end:]

print(read_bytes)
exit()

for idx, text in enumerate(text_lines):
    if idx in remove_ex:
        # text = bytearray(text, 'utf-8')
        # text = text.encode('utf-8')
        print(text)
        print(len(text))
        for start, end in remove_ex[idx][::-1]:
            print(start, end)
            text = text[:start] + text[end:]

        exit()
        # new_row['text'] = row

exit()

# TODO: How does one collect results into file?

"""
buffer = bytearray()
start = 0
while len(remove) > 0:
    a, b = remove.pop()
    buffer += ds.read(a - start)
    ds.seek(b)
    start = b
    

buffer += ds.read()

write_bytes(new_ds, bytes_to_jsonl(buffer))
"""

new_ds.close()

with open(deduped, 'r') as f:
    texts = f.readlines()
    print("Deduplicated texts:")
    for t in texts:
        print(t.strip())

