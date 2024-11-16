import numpy as np
import json
import argparse

def walsh_codes(n):
    if n == 1:
        return np.array([[1]])
    else:
        w = walsh_codes(n // 2)
        return np.block([[w, w], [w, -w]])

def encode_data(data, walsh, bit_size=8):
    encoded_signal = []
    for char in data:
        binary_representation = format(ord(char), f'0{bit_size}b')
        for bit in binary_representation:
            encoded_signal.append(walsh if bit == '1' else -walsh)
    
    return np.array(encoded_signal)

def decode_signal(received_signals, station_codes, bit_size=8):

    decoded_bits = []
    for signal in received_signals:
        decoded_bit = []
        for walsh in station_codes.values():
            dot_product = np.dot(signal, walsh)
            decoded_bit.append('1' if dot_product > 0 else '0')
        decoded_bits.append(decoded_bit)

        print(f'Transmitted signal: {signal}\nRecieved bits: {decoded_bit}\n')

    decoded_words = {}
    for station, s in zip(station_codes.keys(), np.block(decoded_bits).T):
        chars = []
        for i in range(len(s) // bit_size):
            char_value = int(''.join(s[i * bit_size:(i + 1) * bit_size]), 2)
            chars.append(chr(char_value))
        decoded_words[station] = ''.join(chars)  
    
    return decoded_words
        

def main(config):
    # bit_size = 8
    # stations = {
    #     "A": "GOD",
    #     "B": "CAT",
    #     "C": "HAM",
    #     "D": "SUN"
    # }

    stations = config['stations']
    bit_size = config['bit_size']

    w_codes = walsh_codes(bit_size)
    station_codes = {station: w_codes[index] for index, station in zip(np.random.permutation(len(stations)), stations.keys())}

    print('Walsh codes:')
    print('\n'.join(f"{station} : {code.tolist()}" for station, code in station_codes.items()))
    print('\n')

    encoded_signals = {station: encode_data(message, station_codes[station], bit_size) for station, message in stations.items()}
    transmitted_signal = np.sum(list(encoded_signals.values()), axis=0)

    decoded_messages = decode_signal(transmitted_signal, station_codes, bit_size) 
    print('Decoded Messages:')
    for station, message in decoded_messages.items():
        print(f"{station}: {message}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', type=str)
    args = parser.parse_args()

    with open(args.config_file, 'r') as config_file:
        config = json.load(config_file)
    main(config)