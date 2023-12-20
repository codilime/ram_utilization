"""
Implements RamConsumer class able to consume RAM according to given time-dependent pattern.
"""
import gc
import os
from dataclasses import dataclass
from time import sleep
from datetime import datetime, timedelta
import psutil
from memory_consumer.mem_pattern import MemPattern

MEGA = 10**6
# assumed that one chunk is 1% of maximal memory to be allocated
MAX_NUMBER_OF_CHUNKS = 100
# assumed min sleep time after allocation change
SLEEP_TIME_AFTER_ALLOCATION = 0.3  # second
# if difference between memory allocated at os level and in the array
# in number of memory chunks
RESET_OF_ALLOCATION_THRESHOLD = 3
# experimentally selected thresholds for gc
# gc.set_threshold(300, 10, 10)


@dataclass(init=True, repr=True)
class MemConsumerParams:
    """Stores parameters for MemConsumer.

    Arguments:

    max_ram_mega : `int`, default=1000
        maximal amount of memory to be allocated
    time_slot_sec : `int`, default=5
        number of seconds the memory consumer is changing allocation
    linear_trend_slope : `float`, default=0.0
        linear trend slop with respect to pattern duration
    start_from_beginning : `bool`, default=False
        flag that if True forces to use RAM usage pattern from beginning,
        if False (default) RAM usage pattern is used from time of process start
    duration_sec : `int`, default=-1
        how long the process should run in seconds
    """

    max_ram_mega: int = 10**3
    time_slot_sec: int = 5
    linear_trend_slope: float = 0.0
    start_from_beginning: bool = False
    duration_sec: int = -1


class MemConsumer:
    """Implements memory consumer class.

    Parameters
    ----------
    mem_pattern : MemPattern
        memory usage pattern object
    mc_params : MemConsumerParams
        memory consumer parameters
    """

    def __init__(self, mem_pattern: MemPattern, mc_params: MemConsumerParams):
        # pattern instance generates time-dependent amounts of memory with some noise
        self.mem_pattern = mem_pattern
        self.mc_params = mc_params
        # memory array used to allocate memory
        self.__memory_arr = []
        # chunks size in MB
        self.chunk_size_mega = self.mc_params.max_ram_mega // MAX_NUMBER_OF_CHUNKS
        # initial memory allocated for the process
        # consumer corrects allocation subtracting the initial allocation
        proc = int(round(self.os_allocated_memory_mega(), 0))
        # initial memory allocated in number of chunks
        self.__correction = proc // self.chunk_size_mega
        # initial memory rest, taking into account chunk size
        self.__correction_rest = proc % self.chunk_size_mega

    def __str__(self):
        duration_str = (
            "infinite"
            if self.mc_params.duration_sec < 0
            else f"{self.mc_params.duration_sec}s"
        )
        return (
            f"MemConsumer: "
            f"maximum memory: {self.mc_params.max_ram_mega}MB, "
            f"allocation change interval: {self.mc_params.time_slot_sec}s, "
            f"memory chunk size: {self.chunk_size_mega}MB, "
            f"linear trend slope {self.mc_params.linear_trend_slope}, "
            f"start from pattern beginning: {self.mc_params.start_from_beginning}, "
            f"duration: {duration_str}\n"
            f"MemConsumer: initial allocation (minimum allocated memory): "
            f"{self.__correction * self.chunk_size_mega}MB, "
            f"correction rest: {self.__correction_rest}MB"
        )

    def memory_info(self) -> str:
        """Informs on the current allocation of memory in the system and for the process

        Returns
        -------
        str
            Formatted string with info about memory allocated for the process and other
            memory allocation related figures in the system.
        """
        sv_mem = psutil.virtual_memory()
        tot, avail, percent, used, free = list(sv_mem)[0:5]
        tot, avail, used, free = tot / MEGA, avail / MEGA, used / MEGA, free / MEGA
        proc = self.os_allocated_memory_mega()
        info = (
            f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, '
            f"process = {proc:.0f}MB, "
            f"total = {tot:.0f}MB, avail = {avail:.0f}MB, used = {used:.0f}MB, "
            f"free = {free:.0f}MB, percent = {percent:.1f}"
        )
        return info

    # @staticmethod
    def os_allocated_memory_mega(self) -> int:
        """Returns memory allocated for the process in MB, rounded to ten of MB."""
        process = psutil.Process(os.getpid())
        return int(round(process.memory_info()[1] // MEGA, 0))

    def mem_array_allocated_memory_mega(self) -> int:
        """Returns memory allocated for the process in internal memory array in MB."""
        mem_array_size_mega = (
            len(self.__memory_arr) + self.__correction
        ) * self.chunk_size_mega
        return int(mem_array_size_mega)

    def change_allocation(self, alloc_size: int):
        """Changes current memory allocation to required value.

        It adds or removes to memory array chunks in the form of bytearray
        to achieve required amount of allocated memory.
        The number of allocated memory chunks are corrected (correction and correction_rest)
        by the memory allocated for the process by the system at start time.

        Parameters
        ----------
        alloc_size : int :
            Required memory allocation in the number of chunks.
            One chunk is 1% of maximal memory to be allocated.
        """
        current_allocation = len(self.__memory_arr)
        if current_allocation < (alloc_size - self.__correction):
            for k in range(current_allocation, alloc_size - self.__correction):
                if k == 0:
                    self.__memory_arr.append(
                        bytearray(
                            (self.chunk_size_mega - self.__correction_rest) * MEGA
                        )
                    )
                else:
                    self.__memory_arr.append(bytearray(self.chunk_size_mega * MEGA))
        else:
            del self.__memory_arr[max(0, alloc_size - self.__correction) :]
        sleep(SLEEP_TIME_AFTER_ALLOCATION)
        # gc.collect()

    def get_trend_multiplier(self, step: int) -> float:
        """
        Computes trend multiplier depending on allocation step number

        Parameters
        ----------
        step: int :
            Allocation step number increased every allocation/de-allocation event.

        Returns
        -------
        float
            Multiplier by which pattern values are multiplied for consecutive
            steps of allocation/de-allocation process.
        """
        nb_of_steps_in_pattern = (
            self.mem_pattern.get_pattern_duration_in_seconds()
            // self.mc_params.time_slot_sec
        )
        return 1.0 + step * self.mc_params.linear_trend_slope / nb_of_steps_in_pattern

    def run_process(self):
        """Starts process of memory allocation.

        Allocation is changed in the infinite loop for a specified period of time.
        """
        # step is used for computing trend multiplier for consecutive allocation events
        step = 0
        steps_number = self.mc_params.duration_sec // self.mc_params.time_slot_sec
        # time_shift is computed to use RAM usage pattern from start
        # only if start_from_beginning flag is True
        time_shift = timedelta(seconds=0)
        if self.mc_params.start_from_beginning:
            time_shift = self.mem_pattern.get_time_shift_from_start(
                date_time=datetime.now()
            )
        try:
            while True:
                alloc_size = self.mem_pattern.get_value(
                    date_time=datetime.now() - time_shift
                )
                # if linear_trend_slope is defined - alloc_size is modified by trend multiplier
                if self.mc_params.linear_trend_slope > 0.0:
                    alloc_size = int(alloc_size * self.get_trend_multiplier(step))
                self.change_allocation(alloc_size)
                print(
                    f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, '
                    f"Allocated {alloc_size}% of {self.mc_params.max_ram_mega} MB, "
                    f"(in memory array) {self.mem_array_allocated_memory_mega()} MB, "
                    f"(in process) {self.os_allocated_memory_mega()} MB "
                    f"for {self.mc_params.time_slot_sec} sec"
                )
                # when system does not deallocate memory as required, the memory array is cleared
                # this is a king of reset
                if (
                    abs(
                        self.os_allocated_memory_mega()
                        - self.mem_array_allocated_memory_mega()
                    )
                    > RESET_OF_ALLOCATION_THRESHOLD * self.chunk_size_mega
                ):
                    del self.__memory_arr
                    self.__memory_arr = []
                    # gc.collect()

                sleep(self.mc_params.time_slot_sec - SLEEP_TIME_AFTER_ALLOCATION)
                # gc.collect()

                # finish work when steps_number reached
                # infinite loop when steps_number < 0, default if duration_sec is not specified
                if 0 < steps_number <= step:
                    return 0
                step += 1
        except KeyboardInterrupt:
            return 0
