import struct
from collections import Iterable


STRUCT_MESSAGE_SIZE_FMT = '>i'


def concat_proto(messages: Iterable, f):
    for message in messages:
        size = message.ByteSize()
        # Store the size in big-endian byte order, using standard size
        f.write(struct.pack(STRUCT_MESSAGE_SIZE_FMT, size))
        f.write(message.SerializeToString())


def read_concat_proto(f, message_cls) -> Iterable:
    while True:
        struct_size: int = struct.calcsize(STRUCT_MESSAGE_SIZE_FMT)
        message_size_bytes: bytes = f.read(struct_size)

        if not message_size_bytes:
            break

        message_size, = struct.unpack(STRUCT_MESSAGE_SIZE_FMT,
                                      message_size_bytes)

        data: bytes = f.read(message_size)
        message = message_cls()
        message.ParseFromString(data)
        yield message
