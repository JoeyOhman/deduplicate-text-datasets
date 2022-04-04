
def main():
    with open("data_out/json.train", 'rb') as f:
        data_bytes = f.read()

    # print(data_bytes)  # TODO: Check the outputted byte intervals
    print(data_bytes[0:14])
    print(data_bytes[15:240])
    print(data_bytes[254:264])


if __name__ == '__main__':
    main()
