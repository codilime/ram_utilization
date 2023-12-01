"""Tests for MemConsumer class"""
import gc
import sys
from datetime import datetime
import pytest
from memory_consumer.mem_consumer import MemConsumer, MemPattern, MemConsumerParams

gc.set_threshold(100, 10, 10)


@pytest.fixture(scope="module", name="memory_consumer")
def memory_consumer_setup():
    """creates a test MemConsumer for next tests"""
    time_slot_sec = 5
    mem_pattern = MemPattern(pattern_file_name="tests/patterns/s.csv", noise_percent=0)
    mc_params = MemConsumerParams(
        max_ram_mega=1000,
        time_slot_sec=time_slot_sec,
        linear_trend_slope=0.0,
        start_from_beginning=True,
        duration_sec=120,
    )
    mem_consumer = MemConsumer(mem_pattern, mc_params)
    return mem_consumer


def test_run_process(capsys, memory_consumer):
    """tests the whole process of changing memory allocation"""
    memory_consumer.run_process()
    captured = capsys.readouterr()
    all_outputs = captured.out.split("\n")[:-1]
    sys.stdout.write(captured.out)
    sys.stderr.write(captured.err)
    for idx, line in enumerate(all_outputs):
        value = memory_consumer.mem_pattern.get_value(
            date_time=datetime(
                year=2023,
                month=9,
                day=30,
                hour=9,
                minute=25,
                second=idx * memory_consumer.mc_params.time_slot_sec % 60,
            )
        )
        assert f"{value}%" in line
