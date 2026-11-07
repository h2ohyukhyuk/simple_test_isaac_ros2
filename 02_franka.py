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

# 반드시 SimulationApp 생성 이후에 import합니다.
import numpy as np
from pxr import UsdLux

from isaacsim.core.utils.extensions import enable_extension

# 기존 Franka 예제 확장을 활성화합니다.
enable_extension("isaacsim.robot.manipulators.examples")
simulation_app.update()

from isaacsim.core.api import World
from isaacsim.core.utils.types import ArticulationAction
from isaacsim.core.utils.viewports import set_camera_view
from isaacsim.robot.manipulators.examples.franka import Franka

try:
    # 1. 물리 세계, 바닥, 조명
    world = World(
        stage_units_in_meters=1.0,
        physics_dt=1.0 / 60.0,
        rendering_dt=1.0 / 60.0,
    )

    world.scene.add_default_ground_plane()

    light = UsdLux.DomeLight.Define(world.stage, "/World/Light")
    light.CreateIntensityAttr(800.0)

    # 2. Franka 로봇 생성
    print("Franka 모델 불러오는 중...", flush=True)

    robot = world.scene.add(
        Franka(
            prim_path="/World/Franka",
            name="franka",
            position=np.array([0.0, 0.0, 0.0]),
            gripper_open_position=np.array([0.04, 0.04]),
            gripper_closed_position=np.array([0.0, 0.0]),
        )
    )

    set_camera_view(
        eye=np.array([2.0, 2.0, 1.5]),
        target=np.array([0.0, 0.0, 0.5]),
    )

    # 3. 관절 이름에서 인덱스를 찾습니다.
    arm_names = [f"panda_joint{i}" for i in range(1, 8)]
    finger_names = ["panda_finger_joint1", "panda_finger_joint2"]

    # 초기화해야 관절 정보를 읽을 수 있습니다.
    world.reset()

    arm_indices = np.array([
        robot.get_dof_index(name) for name in arm_names
    ])
    finger_indices = np.array([
        robot.get_dof_index(name) for name in finger_names
    ])

    print("관절 목록:", robot.dof_names, flush=True)
    print("현재 관절값:", robot.get_joint_positions(), flush=True)

    # 팔 관절은 라디안, 손가락 관절은 미터 단위입니다.
    pose_a = np.array([
        0.0, -0.5, 0.0, -2.0, 0.0, 1.5, 0.8
    ])
    pose_b = pose_a.copy()
    pose_b[0] = 0.6  # 첫 번째 관절을 약 34도 회전
    pose_b[5] = 3  # 첫 번째 관절을 약 34도 회전

    # 시작 자세만 즉시 배치합니다.
    initial_positions = robot.get_joint_positions().copy()
    initial_positions[arm_indices] = pose_a
    initial_positions[finger_indices] = [0.04, 0.04]

    robot.set_joints_default_state(positions=initial_positions)
    world.reset()

    controller = robot.get_articulation_controller()
    world.play()

    print(
        f"준비 완료: {time.perf_counter() - started:.1f}초",
        flush=True,
    )

    step = 0
    previous_phase = None

    while simulation_app.is_running():
        if world.is_playing():
            # 물리 시간 기준 4초마다 동작 전환
            phase = (step // 240) % 4

            if phase != previous_phase:
                if phase == 0:
                    arm_target = pose_a
                    finger_target = np.array([0.04, 0.04])
                    label = "자세 A / 그리퍼 열기"

                elif phase == 1:
                    arm_target = pose_b
                    finger_target = np.array([0.04, 0.04])
                    label = "자세 B로 이동"

                elif phase == 2:
                    arm_target = pose_b
                    finger_target = np.array([0.0, 0.0])
                    label = "그리퍼 닫기"

                else:
                    arm_target = pose_a
                    finger_target = np.array([0.0, 0.0])
                    label = "자세 A로 복귀"

                print(label, flush=True)
                previous_phase = phase

            # 목표 각도를 전달하면 관절 구동기가 팔을 움직입니다.
            controller.apply_action(
                ArticulationAction(
                    joint_positions=arm_target,
                    joint_indices=arm_indices,
                )
            )

            controller.apply_action(
                ArticulationAction(
                    joint_positions=finger_target,
                    joint_indices=finger_indices,
                )
            )

            step += 1

        world.step(render=True)

finally:
    simulation_app.close()