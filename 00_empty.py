import time

from isaacsim import SimulationApp

started = time.perf_counter()
print("Isaac Sim 초기화 시작", flush=True)

simulation_app = SimulationApp({
    "headless": False,
    "multi_gpu": False,
    "active_gpu": 1,
    "physics_gpu": 1,
    "width": 960,
    "height": 540,
})


print(
    f"초기화 완료: {time.perf_counter() - started:.1f}초",
    flush=True,
)


try:
    while simulation_app.is_running():
        simulation_app.update()
finally:
    simulation_app.close()