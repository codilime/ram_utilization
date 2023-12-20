"""
Creates and runs MemConsumer with arguments.
"""
import os
from datetime import datetime
import argparse
from memory_consumer.mem_consumer import MemPattern, MemConsumerParams, MemConsumer


def main():
    """starts Memory consume app"""
    parser = argparse.ArgumentParser(description="Memory consumer")
    parser.add_argument(
        "-f",
        "--pattern_file",
        type=str,
        required=True,
        help="Csv file with a memory consumption pattern "
        "(time-stamped percent of maximal memory to be allocated).",
    )
    parser.add_argument(
        "-n",
        "--noise_percent",
        type=int,
        default=0,
        help="Noise in percent introduced to the values in memory consumption pattern. "
        "Default=%(default)s, no noise.",
    )
    parser.add_argument(
        "-m",
        "--max_ram_mega",
        type=int,
        default=10**3,
        help="Memory allocated when the memory consumption pattern value is 100 "
        "(default: %(default)s)."
        " Memory allocated for a pattern value = x is (x/100)*MAX_RAM_MEGA",
    )
    parser.add_argument(
        "-t",
        "--time_slot_sec",
        type=int,
        default=5,
        help="Period in seconds (default: %(default)s), the memory consumption is changed.",
    )
    parser.add_argument(
        "-s",
        "--slope_linear_trend",
        type=float,
        default=0.0,
        help="A slope of the linear trend, that is added to the pattern values. "
        "Slope value is expressed for the period of the memory consumption process. "
        "Default is %(default)s",
    )
    parser.add_argument(
        "-b",
        "--start_from_beginning",
        action="store_true",
        help="Start from the beginning of the memory consumption pattern. "
        "If set, the memory consumption will follow the pattern since its beginning "
        "no matter the time the app has started. "
        "If not set (default), the memory consumption will follow the pattern "
        "since the time the app has started.",
    )
    parser.add_argument(
        "-d",
        "--duration_sec",
        type=int,
        default=-1,
        help="Execution time of the memory consumer app in seconds. "
        "Default=%(default)s - which means app is working continuously until CTRL+C.",
    )
    args = parser.parse_args()

    ram_profile = MemPattern(args.pattern_file, args.noise_percent)

    # max_ram_mega can be set in env and has precedence over args.max_ram_mega

    max_ram_mega = int(os.getenv('MAX_RAM_MEGA', args.max_ram_mega))
    if max_ram_mega != args.max_ram_mega:
        print(f"-m, --max_ram_mega argument {args.max_ram_mega} "
              f"has been overwritten by variable MAX_RAM_MEGA={max_ram_mega}")
    if max_ram_mega < 100:
        parser.error("-m, --max_ram_mega argument >= 100")
    ram_consumer_params = MemConsumerParams(
        max_ram_mega,
        args.time_slot_sec,
        args.slope_linear_trend,
        args.start_from_beginning,
        args.duration_sec,
    )

    ram_consumer = MemConsumer(ram_profile, ram_consumer_params)
    print(ram_profile)
    print(ram_consumer)
    print(f'Start time: {datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")}')

    ram_consumer.run_process()


if __name__ == "__main__":
    main()
