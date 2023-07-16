import SoapySDR
from SoapySDR import *
import numpy


def print_devices(devices):
    dev_cnt = len(devices)
    print(f"Found {dev_cnt} device(s).")
    for dev_num in range(0, dev_cnt):
        print(f"Device number {dev_num}: ", end="")
        print(devices[dev_num])


def user_select_device(devices_cnt):
    dev_num = int(input("Select device number: "))
    is_num_correct = (dev_num >= 0) and (dev_num < devices_cnt)

    while not is_num_correct:
        print("Wrong device number! Try again...")
        dev_num = int(input("Select device number: "))
        is_num_correct = (dev_num >= 0) and (dev_num < devices_cnt)

    return dev_num


def print_supported_samplerates(samplerates):
    for sr_num in range(0, len(samplerates)):
        print(f"Samplerate number {sr_num}: {samplerates[sr_num]} Samples/Sec")


def user_select_samplerate(samplerates_cnt):
    sr_num = int(input("Select samplerate number: "))
    is_sr_correct = (sr_num >= 0) and (sr_num < samplerates_cnt)

    while not is_sr_correct:
        print("Wrong samplerate number! Try again...")
        sr_num = int(input("Select samplerate number: "))
        is_sr_correct = (sr_num >= 0) and (sr_num < samplerates_cnt)

    return sr_num


def get_iq_data(sdr, samples_cnt):
    rx_stream = sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)
    sdr.activateStream(rx_stream)
    tmp_buf_size = sdr.getStreamMTU(rx_stream)
    tmp_buf = numpy.array([0] * tmp_buf_size, numpy.complex64)
    final_buf = numpy.array([], numpy.complex64)

    readed_samples = 0
    while readed_samples < samples_cnt:
        sr = sdr.readStream(rx_stream, [tmp_buf], len(tmp_buf))
        if sr.ret > 0:
            final_buf = numpy.concatenate((final_buf, tmp_buf[:sr.ret]))
            readed_samples = readed_samples + sr.ret
        else:
            print(sr.ret)

    sdr.deactivateStream(rx_stream)
    sdr.closeStream(rx_stream)
    return final_buf[:samples_cnt]


def main():
    devices = SoapySDR.Device.enumerate()
    dev_cnt = len(devices)
    if dev_cnt <= 0:
        print("No device found! Quit...")
        quit()

    print_devices(devices)
    dev_num = user_select_device(dev_cnt)
    sdr = SoapySDR.Device(devices[dev_num])

    samplerates = sdr.listSampleRates(SOAPY_SDR_RX, 0)
    print_supported_samplerates(samplerates)
    samplerates_cnt = len(samplerates)
    if samplerates_cnt <= 0:
        print("Samplerates problem...! Quit...")
        quit()

    sr_num = user_select_samplerate(samplerates_cnt)
    sdr.setSampleRate(SOAPY_SDR_RX, 0, samplerates[sr_num])

    freq = int(input("Enter frequency in Hz: "))
    sdr.setFrequency(SOAPY_SDR_RX, 0, freq)
    SoapySDR.setLogLevel(SOAPY_SDR_CRITICAL)
    samples_cnt = int(input("Input count of samples: "))
    iq_array = get_iq_data(sdr, samples_cnt)

    file_name = input("Enter the file name: ")
    numpy.save(file_name, iq_array)
    print("Done!")


if __name__ == "__main__":
    main()
