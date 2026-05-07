from collections import OrderedDict

# start of integers 
TOKEN_INT = b'i'
# start of lists
TOKEN_LIST = b'l'
# start of dictionaries
TOKEN_DICT = b'd'
# end of tokens
TOKEN_END = b'e'
# split length and data sections in strings
TOKEN_SPLIT = b':'

class Decoder:
    """Decodes a bencoded sequence of bytes"""

    def __init__(self, data: bytes):
        if not isinstance(data, bytes):
            raise TypeError('argument "data" must be of type bytes')
        
        self._data = data
        self._indx = 0

    def decode(self):
        """
        Decodes the bencoded data and returns the matching python object

        :return A python object representing the bencoded data
        """
        c = self._next()
        if c == None:
            raise EOFError("Unexpected end of file")
        elif c == TOKEN_INT:
            self._progress()
            return self._decode_int()
        elif c == TOKEN_LIST:
            self._progress()
            return self._decode_list()
        elif c == TOKEN_DICT:
            self._progress()
            return self._decode_dict()
        elif c == TOKEN_END:
            return None
        elif c in b'0123456789':
            return self._decode_string()
        else:
            raise RuntimeError("unexpected token: {0} at index {1}".format(str(c), str(self._indx)))

    
    def _next(self):
        """
        checks the next byte from the bencoded data
        """
        if self._indx + 1 >= len(self._data):
            return None
        return self._data[self._indx : self._indx + 1]
    
    def _progress(self, cnt : int = 1):
        """
        Progresses to the next byte of the data
        """
        self._indx += cnt

    def _read_delim(self, delim : bytes):
        """
        Reads until the delimmiter and progresses
        """
        try:
            ind = self._data.index(delim, self._indx)
            data = self._data[self._indx : ind]
            self._indx = ind + 1
            return data
        except ValueError:
            raise RuntimeError('unable to find token {0}'.format(str(delim)))
    def _read(self, cnt : int):
        """
        Reads the next cnt byte(s) from the bencoded data
        """
        if self._indx + cnt > len(self._data):
            return None
        return self._data[self._indx : self._indx + cnt]
        
    def _decode_int(self):
        """
        Decoedes a bencoded integer
        """
        num = self._read_delim(TOKEN_END)
        return int(num)

    def _decode_list(self):
        """
        Decodes a bencoded list
        """
        arr = []
        while self._read(1) != TOKEN_END:
            arr.append(self.decode())
        self._progress()
        return arr
    
    def _decode_dict(self):
        """
        Decodes a bencoded dictionary
        """
        dict = OrderedDict()
        while self._read(1) != TOKEN_END:
            key = self.decode()
            value = self.decode()
            dict[key] = value
        self._progress()
        return dict
    
    def _decode_string(self):
        """
        Decodes a bencoded string
        """
        len = int(self._read_delim(TOKEN_SPLIT))
        data = self._read(len)
        self._progress(len)
        return data
            
class Encoder:
    """
    Encodes a python object into a bencoded byte string

    supported datatypes:
        - int
        - str
        - list
        - dict
        - bytes
    unspported types will return None
    """
    def __init__(self, obj):
        self._obj = obj

    def encode(self, obj = None):
        if obj == None:
            obj = self._obj
        if type(obj) == str:
            return self._encode_string(obj)
        elif type(obj) == int:
            return self._encode_int(obj)
        elif type(obj) == list:
            return self._encode_list(obj)
        elif type(obj) == dict or type(obj) == OrderedDict:
            return self._encode_dict(obj)
        elif type(obj) == bytes:
            return self._encode_bytes(obj)
        else:
            return None
        
    def _encode_int(self, num : int):
        return str.encode('i' + str(num) + 'e')
    
    def _encode_string(self, s : str):
        length = len(s)
        s = str(length) + ':' + s
        return str.encode(s)
    
    def _encode_list(self, arr : list):
        res = bytearray('l', 'utf-8')
        for x in arr:
            res += self.encode(x)
        res += b'e'
        return res
    
    def _encode_dict(self, dic : dict):
        res = bytearray('d', 'utf-8')
        for k, v in dic.items():
            k = self.encode(k)
            v = self.encode(v)
            if k and v:
                res += k
                res += v
            else:
                raise RuntimeError("Bad dictionary {0}".format(dic))
        res += b'e'
        return res
                

