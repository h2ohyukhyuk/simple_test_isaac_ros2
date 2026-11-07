# Isaac Sim Python 튜토리얼 설치 안내

Python 코드로 장면 생성, Franka 로봇 제어, Pick-and-Place 및 역기구학을 실습합니다.
이 문서는 예제와 버전을 맞추기 위해 **Isaac Sim 6.0.0.1**을 기준으로 합니다.
현재 예제 실행에는 Isaac Lab과 별도 ROS 2 설치가 필요하지 않습니다.

## 1. 준비 사항

- Ubuntu Linux와 NVIDIA RTX GPU
- 정상 작동하는 NVIDIA 드라이버 (`nvidia-smi`로 확인)
- Python **3.12** 및 해당 Python의 `venv` 모듈
- 모델을 처음 불러올 때 사용할 인터넷 연결

현재 실습 환경은 Ubuntu 22.04.5 LTS, RTX 3060 12GB 두 장입니다.
이는 실습 환경 기록이며 공식 최소 사양을 의미하지 않습니다.
Linux pip 패키지에는 GLIBC 2.35 이상이 필요합니다.

```bash
nvidia-smi
python3.12 --version
ldd --version
```

Python 3.12가 없는 경우 먼저 Python 3.12와 venv를 준비하세요.
Ubuntu 22.04의 기본 Python 3.10으로는 이 버전을 실행할 수 없습니다.

## 2. 가상환경 생성

```bash
mkdir -p ~/projects_sim/isaac
cd ~/projects_sim/isaac

python3.12 -m venv env_isaacsim
source env_isaacsim/bin/activate
python -m pip install --upgrade pip
```

가상환경은 생성한 경로에서 사용하세요. 폴더를 옮기면 활성화 스크립트와 실행 파일의 경로가 맞지 않을 수 있습니다.

## 3. Isaac Sim 설치

공식 설치 안내의 CUDA 12.8 PyTorch 패키지 경로를 사용하는 예입니다.
드라이버가 해당 CUDA 런타임을 지원하는지 확인하세요.

```bash
python -m pip install torch==2.11.0 --index-url https://download.pytorch.org/whl/cu128
python -m pip install "isaacsim[all,extscache]==6.0.0.1" --extra-index-url https://pypi.nvidia.com
```

설치 결과를 확인합니다.

```bash
python -m pip show isaacsim
python --version
```

처음 실행할 때 표시되는 NVIDIA 라이선스 내용을 확인하고 동의 절차를 진행합니다.

## 4. 예제 다운로드 및 실행

```bash
cd ~/projects_sim
git clone git@github.com:h2ohyukhyuk/simple_test_isaac_ros2.git
cd simple_test_isaac_ros2

source ~/projects_sim/isaac/env_isaacsim/bin/activate
python 00_empty.py
```

이미 저장소가 있다면 clone을 생략하고 해당 폴더에서 실행하세요.
SSH clone을 사용하려면 GitHub 계정에 SSH 공개 키가 등록되어 있어야 합니다.

| 파일 | 내용 |
|---|---|
| `00_empty.py` | Isaac Sim 창과 실행 루프 확인 |
| `01_scene.py` | 바닥·조명·물체와 물리 시뮬레이션 |
| `02_franka.py` | Franka 생성과 관절·그리퍼 제어 |
| `03_pick_place.py` | 큐브 집기와 이동 |
| `04_follow_target.py` | 역기구학으로 목표 위치 추적 |

예를 들어 세 번째 예제를 실행하려면 다음 명령을 사용합니다.

```bash
python 03_pick_place.py
```

초기화는 현재 실습 환경에서 약 1~2분 걸릴 수 있습니다.
첫 모델 로딩 시에는 추가 다운로드 시간이 필요할 수 있습니다.

## 5. PyCharm 설정

프로젝트 인터프리터를 다음 기존 가상환경으로 지정합니다.

```text
/home/j/projects_sim/isaac/env_isaacsim/bin/python
```

실행 설정의 Working directory는 프로젝트 폴더로 지정합니다.
다른 사용자 계정이나 경로에서는 실제 설치 경로에 맞게 변경하세요.

Isaac Sim 관련 import는 다음 순서를 유지해야 합니다.

```python
from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})

# SimulationApp 생성 이후에 import
from isaacsim.core.api import World
```

PyCharm의 import 정리 기능이 `isaacsim.core` 또는 `pxr` import를 초기화 코드 위로 이동하지 않도록 주의하세요.

## 6. GPU와 화면 출력

예제의 GPU 설정은 현재 실습 PC에서 화면을 출력하는 GPU 1에 맞춰져 있습니다.

```python
"headless": False,
"multi_gpu": False,
"active_gpu": 1,
"physics_gpu": 1,
```

다른 PC에서는 화면 출력이 가능한 GPU 번호로 변경하세요.
GPU가 한 장이면 일반적으로 번호는 `0`입니다.
`cannot present rendered content` 또는 `createSwapchain failed` 오류가 발생하면
선택한 GPU, 모니터 연결 및 실행 환경의 `DISPLAY`를 확인하세요.

```bash
echo "$DISPLAY"
nvidia-smi
```

현재 예제는 기존 Core API와 Franka 예제 확장을 사용합니다.
Isaac Sim 6.0에서는 deprecated 경고가 표시될 수 있으므로,
버전 업그레이드 시 API 변경 여부를 확인해야 합니다.

## 공식 문서

- [Isaac Sim 6.0 Python 설치](https://docs.isaacsim.omniverse.nvidia.com/6.0.0/installation/install_python.html)
- [Isaac Sim 하드웨어·소프트웨어 요구 사항](https://docs.isaacsim.omniverse.nvidia.com/6.0.0/installation/requirements.html)
- [Standalone Python 예제 목록](https://docs.isaacsim.omniverse.nvidia.com/6.0.0/py/docs/api/source/standalone_examples_list.html)
