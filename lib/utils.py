import os
import shutil
from common import const


def get_dir_path(filename):
    return os.path.join('tmp', filename)


def get_root_path():
    dirname = os.path.abspath(__file__)
    dirname = os.path.dirname(dirname)
    return os.path.dirname(dirname)

def get_kv_path():
    root = get_root_path()
    return os.path.join(root, 'kvs')

def is_encrypt(fp):
    cur = fp.tell()
    fp.seek(-len(const.ENCODE_CODE), 2)
    data = fp.read(len(const.ENCODE_CODE))
    ret = list(data) == const.ENCODE_CODE
    fp.seek(cur, 0)
    return ret

def encrypt_file(filename):
    if os.path.isdir(filename):
        return

    def get_enc_code():
        while 1:
            for i in const.ENCODE_CODE:
                yield i

    code_iter = get_enc_code()
    with open(filename, 'rb+') as fp:
        if is_encrypt(fp):
            return

        data = fp.read(const.ENCRYPT_SIZE)
        fp.seek(0, 0)
        write_data = []
        for i in data:
            c = (i + next(code_iter)) % 256
            write_data.append(c)

        fp.write(bytes(write_data))
        fp.seek(0, 2)
        fp.write(bytes(const.ENCODE_CODE))

    os.rename(filename, filename + '.enc')

def decrypt_file(filename):
    if os.path.isdir(filename):
        return

    def get_enc_code():
        while 1:
            for i in const.ENCODE_CODE:
                yield i

    code_iter = get_enc_code()
    with open(filename, 'rb+') as fp:
        if not is_encrypt(fp):
            return

        data = fp.read(const.ENCRYPT_SIZE)
        fp.seek(0, 0)
        write_data = []
        for i in data:
            c = (i - next(code_iter)) % 256
            write_data.append(c)

        fp.write(bytes(write_data))

        fp.seek(-len(const.ENCODE_CODE), 2)
        fp.truncate()

    newname_sp = filename.split('.')
    newname = '.'.join(newname_sp[:-1])
    os.rename(filename, newname)



if __name__ == '__main__':
    get_root_path()