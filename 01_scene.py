import time

from isaacsim import SimulationApp

started = time.perf_counter()

# 1. Isaac Sim 시작
simulation_app = SimulationApp({
    "headless": False,
    "multi_gpu": False,
    "active_gpu": 1,
    "physics_gpu": 1,
    "width": 960,
    "height": 540,
})

# Isaac Sim 관련 모듈은 SimulationApp 초기화 뒤에 가져옵니다.
import numpy as np
from pxr import UsdLux

from isaacsim.core.api import World
from isaacsim.core.api.objects import DynamicCuboid
from isaacsim.core.utils.viewports import set_camera_view

try:
    # 2. 시뮬레이션 세계 생성: 거리 단위는 미터
    world = World(
        stage_units_in_meters=1.0,
        physics_dt=1.0 / 60.0,
        rendering_dt=1.0 / 30.0,
    )

    # 3. 바닥 생성: z = 0
    world.scene.add_default_ground_plane()

    # 4. 장면 전체를 비추는 조명
    light = UsdLux.DomeLight.Define(world.stage, "/World/Light")
    light.CreateIntensityAttr(800.0)

    # 5. 한 변 10cm, 질량 100g인 큐브
    cube = world.scene.add(
        DynamicCuboid(
            prim_path="/World/Cube",
            name="cube",
            position=np.array([0.0, 0.0, 1.8]),
            size=0.1,
            mass=0.1,
            color=np.array([0.2, 0.6, 1.0]),
        )
    )

    # 6. 관찰용 뷰포트 카메라 배치
    set_camera_view(
        eye=np.array([1.8, 1.8, 1.3]),
        target=np.array([0.0, 0.0, 0.25]),
    )

    # 7. 물리 객체 초기화 및 시뮬레이션 시작
    world.reset()
    world.play()

    print(
        f"장면 준비 완료: {time.perf_counter() - started:.1f}초",
        flush=True,
    )

    step = 0

    # 8. 물리 계산과 화면 갱신 반복
    while simulation_app.is_running():
        world.step(render=True)

        if world.is_playing():
            if step % 60 == 0:
                position, orientation = cube.get_world_pose()
                print(
                    f"큐브 위치 [m]: "
                    f"x={position[0]:.3f}, "
                    f"y={position[1]:.3f}, "
                    f"z={position[2]:.3f}",
                    flush=True,
                )

            step += 1
        time.sleep(1)

finally:
    simulation_app.close()