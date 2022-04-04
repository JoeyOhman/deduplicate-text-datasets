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

import sys
import json


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
remove = remove[::-1]

ds = open(original, "rb")
# new_ds = open(deduped,"wb")
new_ds = open(deduped, "w")

buffer = bytearray()
start = 0
while len(remove) > 0:
    a, b = remove.pop()
    buffer += ds.read(a - start)
    # to_write = ds.read(a - start)
    # print(to_write)
    # print(to_write[6:])

    # print(w_split)
    # exit()
    # new_ds.write(ds.read(a-start).decode("utf-8", 'ignore'))
    # write_bytes(new_ds, ds.read(a-start))

    # write_bytes(new_ds, bytes_to_jsonl(ds.read(a - start)))
    ds.seek(b)
    start = b
# new_ds.write(ds.read().decode("utf-8", 'ignore'))

buffer += ds.read()
# write_bytes(new_ds, bytes_to_jsonl(ds.read()))
write_bytes(new_ds, bytes_to_jsonl(buffer))

new_ds.close()

with open(deduped, 'r') as f:
    texts = f.readlines()
    print("Deduplicated texts:")
    for t in texts:
        print(t.strip())

