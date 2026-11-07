from isaacsim import SimulationApp

simulation_app = SimulationApp({
    "headless": False,
    "multi_gpu": False,
    "active_gpu": 1,
    "physics_gpu": 1,
    "width": 960,
    "height": 540,
})

# SimulationApp 초기화 이후 import
import numpy as np
from pxr import UsdLux

from isaacsim.core.utils.extensions import enable_extension

enable_extension("isaacsim.robot.manipulators.examples")
simulation_app.update()

from isaacsim.core.api import World
from isaacsim.core.api.objects import VisualCuboid
from isaacsim.core.utils.rotations import euler_angles_to_quat
from isaacsim.core.utils.viewports import set_camera_view
from isaacsim.robot.manipulators.examples.franka import Franka
from isaacsim.robot.manipulators.examples.franka.kinematics_solver import (
    KinematicsSolver,
)

try:
    # 1. 장면 구성
    physics_dt = 1.0 / 60.0

    world = World(
        stage_units_in_meters=1.0,
        physics_dt=physics_dt,
        rendering_dt=physics_dt,
    )

    world.scene.add_default_ground_plane()

    light = UsdLux.DomeLight.Define(world.stage, "/World/Light")
    light.CreateIntensityAttr(800.0)

    robot = world.scene.add(
        Franka(
            prim_path="/World/Franka",
            name="franka",
            position=np.array([0.0, 0.0, 0.0]),
        )
    )

    # 시각적 표시용 물체: 중력과 충돌의 영향을 받지 않습니다.
    target = world.scene.add(
        VisualCuboid(
            prim_path="/World/Target",
            name="target",
            position=np.array([0.45, 0.0, 0.40]),
            size=0.035,
            color=np.array([1.0, 0.15, 0.15]),
        )
    )

    set_camera_view(
        eye=np.array([1.6, 1.6, 1.3]),
        target=np.array([0.35, 0.0, 0.4]),
    )

    world.reset()

    # 2. 역기구학 계산기와 관절 제어기
    ik_solver = KinematicsSolver(robot)
    controller = robot.get_articulation_controller()

    # IK 계산기에 로봇 베이스의 월드 좌표를 전달
    base_position, base_orientation = robot.get_world_pose()
    ik_solver.get_kinematics_solver().set_robot_base_pose(
        base_position,
        base_orientation,
    )

    # 손끝의 방향은 일정하게 유지합니다.
    # Euler 각도는 라디안, 변환 결과는 quaternion입니다.
    target_orientation = euler_angles_to_quat(
        np.array([0.0, np.pi, 0.0])
    )

    world.play()

    step = 0
    previous_success = None

    print("빨간 목표를 손끝이 따라갑니다.", flush=True)

    while simulation_app.is_running():
        if world.is_playing():
            # 시뮬레이션 시간: 실제 시계 시간과는 다를 수 있습니다.
            t = step * physics_dt

            # 약 12.6초 주기로 Y 방향 왕복
            target_position = np.array([
                0.45,
                0.15 * np.sin(0.5 * t),
                0.40,
            ])

            target.set_world_pose(position=target_position)

            # 3. 목표 손끝 위치·방향 → 관절 목표값
            action, success = (
                ik_solver.compute_inverse_kinematics(
                    target_position=target_position,
                    target_orientation=target_orientation,
                )
            )

            # 4. 해를 찾았을 때만 로봇에 명령 전달
            if success:
                controller.apply_action(action)

            if success != previous_success:
                print(
                    "IK 계산 성공" if success
                    else "IK 해를 찾지 못했습니다.",
                    flush=True,
                )
                previous_success = success

            step += 1

        world.step(render=True)

finally:
    simulation_app.close()