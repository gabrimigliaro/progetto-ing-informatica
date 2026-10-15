'''
Riferimenti Standard e Specifiche Matematiche:
  - NIST FIPS PUB 197: "Advanced Encryption Standard (AES)"
    https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197.pdf
  - Struttura dei Round per AES-256 (14 Rounds, 60 parole di Key Expansion):
    * SubBytes (S-Box)
    * ShiftRows
    * MixColumns (Moltiplicazione polinomiale in GF(2^8))
    * AddRoundKey & KeyExpansion (RCON)
'''

import os
import dbus #type: ignore

from assets.managers.LogsManager import LOGS

class EncryptUtils:
    def __init__(self):
        self.key = os.environ.get("BLE_KEY").encode("utf-8")

        if len(self.key) != 32:
            raise ValueError(f"[ERRORE] La chiave deve essere lunga esattamente 32 caratteri.")

        self.s_box = [99,124,119,123,242,107,111,197,48,1,103,43,254,215,171,118,202,130,201,125,250,89,71,240,173,212,162,175,156,164,114,192,183,253,147,38,54,63,247,204,52,165,229,241,113,216,49,21,4,199,35,195,24,150,5,154,7,18,128,226,235,39,178,117,9,131,44,26,27,110,90,160,82,59,214,179,41,227,47,132,83,209,0,237,32,252,177,91,106,203,190,57,74,76,88,207,208,239,170,251,67,77,51,133,69,249,2,127,80,60,159,168,81,163,64,143,146,157,56,245,188,182,218,33,16,255,243,210,205,12,19,236,95,151,68,23,196,167,126,61,100,93,25,115,96,129,79,220,34,42,144,136,70,238,184,20,222,94,11,219,224,50,58,10,73,6,36,92,194,211,172,98,145,149,228,121,231,200,55,109,141,213,78,169,108,86,244,234,101,122,174,8,186,120,37,46,28,166,180,198,232,221,116,31,75,189,139,138,112,62,181,102,72,3,246,14,97,53,87,185,134,193,29,158,225,248,152,17,105,217,142,148,155,30,135,233,206,85,40,223,140,161,137,13,191,230,66,104,65,153,45,15,176,84,187,22]
        self.rcon = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]

        #self.inv_s_box=[82,9,106,213,48,54,165,56,191,64,163,158,129,243,215,251,124,227,57,130,155,47,255,135,52,142,67,68,196,222,233,203,84,123,148,50,166,194,35,61,238,76,149,11,66,250,195,78,8,46,161,102,40,217,36,178,118,91,162,73,109,139,209,37,114,248,246,100,134,104,152,22,212,164,92,204,93,101,182,146,108,112,72,83,247,240,6,69,170,183,115,87,28,237,107,125,185,89,110,168,179,219,211,136,200,14,236,24,80,131,241,218,27,224,181,253,77,235,245,38,159,17,105,244,22,171,153,201,127,192,210,216,12,193,186,167,150,156,19,34,221,188,138,214,228,219,187,208,79,137,21,180,13,140,30,39,242,226,202,121,160,116,98,147,86,174,20,177,175,249,111,81,169,70,26,252,225,161,25,3,151,120,33,230,4,32,197,184,94,189,132,119,65,2,239,103,18,9,88,231,229,133,74,113,207,223,176,85,55,220,234,122,143,10,205,126,198,157,117,44,145,13,172,154,206,199,128,15,173,144,71,190,1,141,75,16,127,137,218,211,79,41,51,101,136,217,221,59,45,2,239,177]

        self.inv_s_box = [0] * 256
        for i in range(256):
         self.inv_s_box[self.s_box[i]] = i

    def sub_bytes(self, state):
        for i in range(4):
            for j in range(4):
                state[i][j] = self.s_box[state[i][j]]

    def shift_rows(self, state):
        state[1] = state[1][1:] + state[1][:1]
        state[2] = state[2][2:] + state[2][:2]
        state[3] = state[3][3:] + state[3][:3]

    def xtime(self, a):
        return ((a << 1) ^ 0x1B) & 0xFF if a & 0x80 else a << 1

    def mix_columns(self, state):
        for i in range(4):
            t = state[0][i] ^ state[1][i] ^ state[2][i] ^ state[3][i]
            u = state[0][i]
            state[0][i] ^= t ^ self.xtime(state[0][i] ^ state[1][i])
            state[1][i] ^= t ^ self.xtime(state[1][i] ^ state[2][i])
            state[2][i] ^= t ^ self.xtime(state[2][i] ^ state[3][i])
            state[3][i] ^= t ^ self.xtime(state[3][i] ^ u)

    def add_round_key(self, state, round_key):
        for i in range(4):
            for j in range(4):
                state[i][j] ^= round_key[i][j]

    def key_expansion_256(self, key_bytes):
        words = [list(key_bytes[i : i + 4]) for i in range(0, 32, 4)]
        for i in range(8, 60):
            temp = words[i - 1][:]
            if i % 8 == 0:
                temp = temp[1:] + temp[:1]
                temp = [self.s_box[b] for b in temp]
                temp[0] ^= self.rcon[i // 8]
            elif i % 8 == 4:
                temp = [self.s_box[b] for b in temp]
            word = [words[i - 8][j] ^ temp[j] for j in range(4)]
            words.append(word)

        return [[[words[r * 4 + j][i] for j in range(4)] for i in range(4)] for r in range(15)]

    def encrypt_aes_256_ecb(self, data_bytes: bytes) -> bytes:
        if len(self.key) != 32:
            raise ValueError("La chiave per AES-256 deve essere di esattamente 32 byte!")

        data = data_bytes.ljust(16, b"\x00")[:16]

        state = [[data[i + 4 * j] for j in range(4)] for i in range(4)]
        round_keys = self.key_expansion_256(self.key)

        self.add_round_key(state, round_keys[0])

        for r in range(1, 14):
            self.sub_bytes(state)
            self.shift_rows(state)
            self.mix_columns(state)
            self.add_round_key(state, round_keys[r])

        self.sub_bytes(state)
        self.shift_rows(state)
        self.add_round_key(state, round_keys[14])

        output = bytearray(16)
        for i in range(4):
            for j in range(4):
                output[i + 4 * j] = state[i][j]

        return bytes(output)

    def inv_sub_bytes(self, state):
        for i in range(4):
            for j in range(4):
                state[i][j] = self.inv_s_box[state[i][j]]

    def inv_shift_rows(self, state):
        state[1] = state[1][-1:] + state[1][:-1]
        state[2] = state[2][-2:] + state[2][:-2]
        state[3] = state[3][-3:] + state[3][:-3]

    def multiply(self, a, b):
      p = 0
      for _ in range(8):
        if b & 1:
          p ^= a
        hi_bit_set = a & 0x80
        a = (a << 1) & 0xFF
        if hi_bit_set:
          a ^= 0x1B
        b >>= 1
      return p

    def inv_mix_columns(self, state):
      for i in range(4):
        s0, s1, s2, s3 = (
            state[0][i],
            state[1][i],
            state[2][i],
            state[3][i],
        )
        state[0][i] = (
            self.multiply(s0, 0x0E)
            ^ self.multiply(s1, 0x0B)
            ^ self.multiply(s2, 0x0D)
            ^ self.multiply(s3, 0x09)
        )
        state[1][i] = (
            self.multiply(s0, 0x09)
            ^ self.multiply(s1, 0x0E)
            ^ self.multiply(s2, 0x0B)
            ^ self.multiply(s3, 0x0D)
        )
        state[2][i] = (
            self.multiply(s0, 0x0D)
            ^ self.multiply(s1, 0x09)
            ^ self.multiply(s2, 0x0E)
            ^ self.multiply(s3, 0x0B)
        )
        state[3][i] = (
            self.multiply(s0, 0x0B)
            ^ self.multiply(s1, 0x0D)
            ^ self.multiply(s2, 0x09)
            ^ self.multiply(s3, 0x0E)
        )

    def decrypt_aes_256_ecb(self, cipher_bytes: bytes) -> bytes:
      """Decifra un singolo blocco di 16 byte cifrato in AES-256."""
      if len(cipher_bytes) != 16:
        raise ValueError(
            "Il blocco cifrato da decifrare deve essere esattamente di 16 byte!"
        )

      state = [[cipher_bytes[i + 4 * j] for j in range(4)] for i in range(4)]
      round_keys = self.key_expansion_256(self.key)

      # Inizio dal Round 14 (chiave finale)
      self.add_round_key(state, round_keys[14])
      self.inv_shift_rows(state)
      self.inv_sub_bytes(state)

      # Round da 13 a 1
      for r in range(13, 0, -1):
        self.add_round_key(state, round_keys[r])
        self.inv_mix_columns(state)
        self.inv_shift_rows(state)
        self.inv_sub_bytes(state)

      # Round 0 (Initial AddRoundKey)
      self.add_round_key(state, round_keys[0])

      output = bytearray(16)
      for i in range(4):
        for j in range(4):
          output[i + 4 * j] = state[i][j]

      return bytes(output)

#---------------------------------------------------------------------

    def encrypt_payload(self, raw_bytes: bytes):
        padded_16bytes = raw_bytes.ljust(16, b"\x00")

        return self.encrypt_aes_256_ecb(padded_16bytes)

    def encrypt_string(self, text: str) -> bytes:
        raw_bytes = text.encode("utf-8")

        # 2. Verifica che non superi la dimensione del blocco (16 byte)
        if len(raw_bytes) > 16:
            bytes1 = raw_bytes[0:16]
            bytes2 = raw_bytes[16:]

            encrypted_bytes1 = self.encrypt_payload(bytes1).hex()
            encrypted_bytes2 = self.encrypt_payload(bytes2).hex()

            return encrypted_bytes1 + encrypted_bytes2
        else:
            # 3. Richiama il tuo metodo esistente per il padding e la cifratura
            return self.encrypt_payload(raw_bytes).hex()

    def decrypt_string(self, cipher_hex: bytes) -> str:
        string_bytes = bytes.fromhex(cipher_hex)

        if len(string_bytes) > 16:
            decrypted_raw1 = self.decrypt_aes_256_ecb(string_bytes[0:16])
            decrypted_raw2 = self.decrypt_aes_256_ecb(string_bytes[16:])

            clean_bytes = decrypted_raw2.rstrip(b"\x00")

            return (decrypted_raw1 + clean_bytes).decode("utf-8")
        else:
            decrypted_raw = self.decrypt_aes_256_ecb(string_bytes)
            clean_bytes = decrypted_raw.rstrip(b"\x00")

            return clean_bytes.decode("utf-8")

encryptUtils = EncryptUtils()