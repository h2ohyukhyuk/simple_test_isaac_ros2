# Isaac Sim Python 튜토리얼 설치 안내

Python 코드로 장면 생성, Franka 로봇 제어, Pick-and-Place 및 역기구학을 실습합니다.
이 문서는 예제와 버전을 맞추기 위해 **Isaac Sim 6.0.0.1**을 기준으로 합니다.
현재 예제 실행에는 Isaac Lab과 별도 ROS 2 설치가 필요하지 않습니다.

## 1. 준비 사항

- Ubuntu Linux와 NVIDIA RTX GPU
- 정상 작동하는 NVIDIA 드라이버 (`nvidia-smi`로 확인)
- `uv` (아래 단계에서 설치하며 Python 3.12도 준비할 수 있습니다)
- 모델을 처음 불러올 때 사용할 인터넷 연결

현재 실습 환경은 Ubuntu 22.04.5 LTS, RTX 3060 12GB 두 장입니다.
이는 실습 환경 기록이며 공식 최소 사양을 의미하지 않습니다.
Linux pip 패키지에는 GLIBC 2.35 이상이 필요합니다.

```bash
nvidia-smi
ldd --version
```

Isaac Sim 6.0에는 Python 3.12가 필요합니다. Ubuntu 22.04의 기본 Python 3.10과 별도로 준비합니다.

## 2. uv 설치 및 가상환경 생성

`uv`는 Python 버전, 가상환경과 패키지를 관리하는 도구입니다.
현재 실습 환경도 uv로 생성·설치된 환경입니다. 아래 명령은 새로 설치할 때의 안내이며, 과거 실행 명령을 복원한 기록은 아닙니다.

공식 설치 스크립트로 uv를 설치한 뒤 터미널을 새로 엽니다.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

새 터미널에서 다음을 실행합니다.

```bash
uv --version
uv python install 3.12
```

```bash
mkdir -p ~/venvs
cd ~/venvs

uv venv --python 3.12 --seed venv_isaacsim
source venv_isaacsim/bin/activate
```

가상환경은 생성한 경로에서 사용하세요. 폴더를 옮기면 활성화 스크립트와 실행 파일의 경로가 맞지 않을 수 있습니다.

## 3. Isaac Sim 설치

아래 명령은 Python 3.12 가상환경을 활성화한 상태에서 실행합니다.
이번에 설치를 확인한 환경은 `/home/j/venvs/venv-isaacsim`입니다.

```bash
source ~/venvs/venv-isaacsim/bin/activate
python --version
python -c "import sys; print(sys.executable)"
```

NVIDIA의 Isaac Sim 6.0 pip 설치 안내에 따라 CUDA 지원 PyTorch를 먼저 설치합니다.
이는 강화학습용 코드를 추가하는 단계가 아니라 Isaac Sim에서 사용하는 의존성을 준비하는 과정입니다.
아래 명령은 CUDA 12.8 빌드를 설치하며, 드라이버가 해당 CUDA 런타임을 지원해야 합니다.

```bash
uv pip install torch==2.11.0 --index-url https://download.pytorch.org/whl/cu128

uv pip install "isaacsim[all,extscache]==6.0.0.1" \
  --extra-index-url https://pypi.nvidia.com \
  --index-strategy unsafe-best-match
```

### 설치 중 발생한 의존성 오류

실제 설치에서는 `--index-strategy unsafe-best-match` 없이 실행했을 때 다음 오류로 중단되었습니다.

```text
No solution found when resolving dependencies
there is no version of mujoco-usd-converter==0.2.0
```

`uv`는 기본적으로 패키지를 처음 발견한 저장소의 버전만 고려합니다.
이번에는 NVIDIA 저장소에서 `mujoco-usd-converter`를 발견했지만 필요한 `0.2.0` 버전이 없어,
다른 저장소에 있는 후보를 검토하지 않고 의존성 해결에 실패했습니다.

`--index-strategy unsafe-best-match`는 NVIDIA 저장소와 기본 PyPI 양쪽의 후보를 비교하도록 합니다.
이 옵션은 패키지 저장소 간 우선순위 보호를 완화하므로, 여기서는 공식 NVIDIA 저장소와 PyPI를 사용하는 설치에 한정해 적용합니다.
이 옵션을 추가한 뒤 설치가 완료되었습니다. Python 버전 문제나 PyTorch 설치 실패는 아니었습니다.

### 설치 결과 확인

```bash
python -m pip show isaacsim torch
python --version
```

이번에 확인한 결과는 다음과 같습니다.

- Python: `3.12.15`
- Isaac Sim: `6.0.0.1`
- PyTorch: `2.11.0+cu128`
- 설치 위치: `/home/j/venvs/venv-isaacsim/lib/python3.12/site-packages`

단독 `pip` 명령 대신 `python -m pip`를 사용해 실행할 Python과 같은 환경을 확인합니다.
PyCharm 인터프리터도 `/home/j/venvs/venv-isaacsim/bin/python`으로 지정합니다.
이미 위 환경에 설치가 완료됐다면 다시 설치할 필요가 없습니다.
### 첫 실행 시 NVIDIA 라이선스 동의

설치 후 빈 장면 예제를 실행합니다.

```bash
/home/j/venvs/venv-isaacsim/bin/python \
  /home/j/projects_sim/simple_test_isaac_ros2/00_empty.py
```

첫 실행 시 터미널 또는 PyCharm 실행 콘솔에 다음 질문이 표시될 수 있습니다.

```text
By installing or using Omniverse Kit, I agree to the terms of NVIDIA OMNIVERSE LICENSE AGREEMENT (EULA)
in https://docs.omniverse.nvidia.com/platform/latest/common/NVIDIA_Omniverse_License_Agreement.html

Do you accept the EULA? (Yes/No):
```

[NVIDIA Omniverse 라이선스](https://docs.omniverse.nvidia.com/platform/latest/common/NVIDIA_Omniverse_License_Agreement.html)를 확인하고 동의한다면,
실행 콘솔에 `Yes`를 입력한 뒤 Enter를 누릅니다.
입력을 기다리는 동안에는 초기화가 진행되지 않으므로, 시뮬레이터 창이 열리지 않으면 콘솔의 질문을 확인하세요.

### 첫 실행은 충분히 기다리세요

첫 실행은 셰이더 컴파일, 확장 모듈 초기화 및 캐시 생성으로 오래 걸릴 수 있습니다.
창이 늦게 열리거나 잠시 “응답하지 않습니다”가 표시되더라도 바로 종료하지 말고,
콘솔 로그가 계속 진행되는지 확인하면서 인내심을 가지고 기다리세요.
환경에 따라 수 분 이상 걸릴 수 있습니다.

생성된 캐시를 재사용하므로 두 번째 실행부터는 일반적으로 시작 시간이 줄어듭니다.
다만 캐시를 삭제하거나 드라이버·Isaac Sim 버전을 변경한 경우,
또는 새로운 모델을 처음 불러오는 경우에는 다시 시간이 걸릴 수 있습니다.
명확한 오류가 반복되거나 로그 진행 없이 장시간 멈춘 경우에는 오류 내용을 확인하세요.


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

- [uv 공식 설치 안내](https://docs.astral.sh/uv/getting-started/installation/)
