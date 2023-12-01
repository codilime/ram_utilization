"""Tests for MemConsumer class"""
import gc
import random
from time import sleep
import pytest
from memory_consumer.mem_consumer import MemConsumer, MemPattern, MemConsumerParams

gc.set_threshold(100, 10, 10)


@pytest.fixture(scope="module", name="memory_consumer")
def memory_consumer_setup():
    """creates a test MemConsumer for next tests"""
    max_ram_mega = 1000
    mem_profile = MemPattern(
        pattern_file_name="tests/patterns/ms.csv", noise_percent=15
    )
    mc_params = MemConsumerParams(max_ram_mega=max_ram_mega, time_slot_sec=2)
    mem_cons = MemConsumer(mem_pattern=mem_profile, mc_params=mc_params)
    print(mem_cons)
    return mem_cons


@pytest.mark.parametrize(
    "memory_percent_to_allocate", [random.randint(20, 120) for _ in range(10)]
)
def test_change_allocation(memory_percent_to_allocate, memory_consumer):
    """tests change_allocation, major method of MemConsumer, for randomly generated percents
    of max_memory to be allocated"""
    toleration = 2
    memory_consumer.change_allocation(memory_percent_to_allocate)
    chunk_size = memory_consumer.chunk_size_mega
    gc.collect()
    sleep(0.1)
    os_mega = memory_consumer.os_allocated_memory_mega()
    mem_array_mega = memory_consumer.mem_array_allocated_memory_mega()
    assert (memory_percent_to_allocate - toleration) * chunk_size <= os_mega
    assert (memory_percent_to_allocate + toleration) * chunk_size >= os_mega
    assert (memory_percent_to_allocate - toleration) * chunk_size <= mem_array_mega
    assert (memory_percent_to_allocate + toleration) * chunk_size >= mem_array_mega
    assert abs(mem_array_mega - os_mega) < toleration * chunk_size
    # len(gc.get_objects())


def __get_test_mem_consumer(
    pattern_file_name, noise_percent, time_slot_sec, linear_trend_slope, duration_min=-1
) -> MemConsumer:
    mem_profile = MemPattern(
        pattern_file_name=pattern_file_name, noise_percent=noise_percent
    )
    mc_params = MemConsumerParams(
        max_ram_mega=100,
        time_slot_sec=time_slot_sec,
        linear_trend_slope=linear_trend_slope,
        duration_sec=duration_min,
    )
    return MemConsumer(mem_profile, mc_params)


@pytest.mark.parametrize("step", [random.randint(1, 12000) for _ in range(20)])
def test_get_trend_multiplier_from_ms_profile(step):
    """tests trend multiplier (the pattern value is multiplied by) dependent of allocation step
    for ms (minute,second) pattern"""
    linear_trend_slope = 0.1
    mem_consumer = __get_test_mem_consumer(
        pattern_file_name="tests/patterns/ms.csv",
        noise_percent=15,
        time_slot_sec=5,
        linear_trend_slope=linear_trend_slope,
    )
    trend_multiplier = mem_consumer.get_trend_multiplier(step)
    trend_multiplier_should_be = 1.0 + linear_trend_slope * step / (
        60 * 60 / mem_consumer.mc_params.time_slot_sec
    )
    assert trend_multiplier == trend_multiplier_should_be


@pytest.mark.parametrize("step", [random.randint(1, 12000) for _ in range(50)])
def test_get_trend_multiplier_from_s_profile(step):
    """tests trend multiplier (the pattern value is multiplied by) dependent of allocation step
    for s (second) pattern"""
    linear_trend_slope = 0.15
    mem_consumer = __get_test_mem_consumer(
        pattern_file_name="tests/patterns/s.csv",
        noise_percent=15,
        time_slot_sec=2,
        linear_trend_slope=linear_trend_slope,
    )
    trend_multiplier = mem_consumer.get_trend_multiplier(step)
    trend_multiplier_should_be = 1.0 + linear_trend_slope * step / (
        60 / mem_consumer.mc_params.time_slot_sec
    )
    assert trend_multiplier == trend_multiplier_should_be


@pytest.mark.parametrize("step", [random.randint(1, 12000) for _ in range(50)])
def test_get_trend_multiplier_from_m_profile(step):
    """tests trend multiplier (the pattern value is multiplied by) dependent of allocation step
    for m (minute) pattern"""
    linear_trend_slope = 0.05
    mem_consumer = __get_test_mem_consumer(
        pattern_file_name="tests/patterns/m.csv",
        noise_percent=15,
        time_slot_sec=5,
        linear_trend_slope=linear_trend_slope,
    )
    trend_multiplier = mem_consumer.get_trend_multiplier(step)
    trend_multiplier_should_be = 1.0 + linear_trend_slope * step / (
        60 * 60 / mem_consumer.mc_params.time_slot_sec
    )
    assert trend_multiplier == trend_multiplier_should_be


@pytest.mark.parametrize("step", [random.randint(1, 12000) for _ in range(50)])
def test_get_trend_multiplier_from_dhm_profile(step):
    """tests trend multiplier (the pattern value is multiplied by) dependent of allocation step
    for dhm (day,hour,minute) pattern"""
    linear_trend_slope = -0.05
    mem_consumer = __get_test_mem_consumer(
        pattern_file_name="tests/patterns/dhm.csv",
        noise_percent=15,
        time_slot_sec=5,
        linear_trend_slope=linear_trend_slope,
    )
    trend_multiplier = mem_consumer.get_trend_multiplier(step)
    trend_multiplier_should_be = 1.0 + linear_trend_slope * step / (
        7 * 24 * 60 * 60 / mem_consumer.mc_params.time_slot_sec
    )
    assert trend_multiplier == trend_multiplier_should_be
