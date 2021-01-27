from enum import Enum


class ConnectionMessages(Enum):
    CREATE_GAME = b'\x00'
    JOIN_GAME = b'\x01'
    PORT = b'\x02'
    NO_FREE_PORT = b'\x03'
    CLOSE = b'\x04'
    NICKNAME = b'\x05'
    GET_LOBBIES = b'\x06'

class GameMessages(Enum):

    MOVEN = b'\x01'
    MOVEE = b'\x02'
    MOVES = b'\x03'
    MOVEW = b'\x04'
    MOVENE = b'\x05'
    MOVENW = b'\x06'
    MOVESE = b'\x07'
    MOVESW = b'\x08'

    PLAYER1= b'\x09'
    PLAYER2= b'\x0a'

    SPELL1 = b'\x0b'
    SPELL2 = b'\x0c'
    SPELL3 = b'\x0d'

    END = b'\x0e'
