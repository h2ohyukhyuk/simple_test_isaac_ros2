import time

from isaacsim import SimulationApp

started = time.perf_counter()

simulation_app = SimulationApp({
    "headless": False,
    "multi_gpu": False,
    "active_gpu": 1,
    "physics_gpu": 1,
    "width": 960,
    "height": 540,
})

# SimulationApp 생성 이후에 import
import numpy as np
from pxr import UsdLux

from isaacsim.core.utils.extensions import enable_extension

enable_extension("isaacsim.robot.manipulators.examples")
simulation_app.update()

from isaacsim.core.api import World
from isaacsim.core.api.objects import DynamicCuboid
from isaacsim.core.utils.viewports import set_camera_view
from isaacsim.robot.manipulators.examples.franka import Franka
from isaacsim.robot.manipulators.examples.franka.controllers import (
    PickPlaceController,
)

try:
    # 1. 세계, 바닥, 조명
    world = World(
        stage_units_in_meters=1.0,
        physics_dt=1.0 / 60.0,
        rendering_dt=1.0 / 60.0,
    )

    world.scene.add_default_ground_plane()

    light = UsdLux.DomeLight.Define(world.stage, "/World/Light")
    light.CreateIntensityAttr(800.0)

    # 2. 로봇 생성
    robot = world.scene.add(
        Franka(
            prim_path="/World/Franka",
            name="franka",
            position=np.array([0.0, 0.0, 0.0]),
        )
    )

    # 3. 집을 큐브: 한 변 5.15cm
    cube_size = 0.0515

    cube = world.scene.add(
        DynamicCuboid(
            prim_path="/World/Cube",
            name="cube",
            position=np.array([0.45, 0.20, cube_size / 2]),
            size=cube_size,
            mass=0.05,
            color=np.array([0.2, 0.6, 1.0]),
        )
    )

    # 내려놓을 큐브 중심의 목표 위치
    target_position = np.array([
        0.45, -0.20, cube_size / 2
    ])

    set_camera_view(
        eye=np.array([1.6, 1.6, 1.3]),
        target=np.array([0.35, 0.0, 0.3]),
    )

    # 4. 물리 객체 초기화
    world.reset()

    # 리셋 시 그리퍼가 열린 상태로 시작
    robot.gripper.set_default_state(
        robot.gripper.joint_opened_positions
    )
    world.reset()

    # 5. 집기 제어기 생성
    pick_place = PickPlaceController(
        name="pick_place_controller",
        gripper=robot.gripper,
        robot_articulation=robot,
    )

    articulation_controller = robot.get_articulation_controller()

    world.play()

    print(
        f"장면 준비 완료: {time.perf_counter() - started:.1f}초",
        flush=True,
    )
    print("큐브를 집어 반대편으로 옮깁니다.", flush=True)

    step = 0
    completion_reported = False

    while simulation_app.is_running():
        if world.is_playing():
            # 시작 후 1초 동안 큐브가 안정되도록 기다립니다.
            if step >= 60 and not pick_place.is_done():
                cube_position, _ = cube.get_world_pose()

                # 손끝 목표를 관절 명령으로 변환
                action = pick_place.forward(
                    picking_position=cube_position,
                    placing_position=target_position,
                    current_joint_positions=robot.get_joint_positions(),
                    end_effector_offset=np.array([0.0, 0.0, 0.0]),
                )

                articulation_controller.apply_action(action)

            elif pick_place.is_done() and not completion_reported:
                print(
                    "집기·이동·놓기 제어 순서가 완료되었습니다.",
                    flush=True,
                )
                completion_reported = True

            step += 1

        world.step(render=True)

finally:
    simulation_app.close()