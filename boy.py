from pico2d import *
from transitions import Machine


# AutoRun 상태 전용 클래스
class AutoRun:
    def __init__(self, boy):
        self.boy = boy
        self.start_time = 0

        self.speed = 450
        self.size = 160

    def enter(self):
        self.start_time = get_time()
        self.boy.frame = 0
        print('현재 상태: AUTORUN')

    def update(self, dt):
        boy = self.boy

        # 빠른 달리기 애니메이션
        boy.frame = (boy.frame + 16 * dt) % 8

        # 자동 이동
        boy.x += boy.face_dir * self.speed * dt

        # 확대된 캐릭터의 좌우 이동 범위
        left_limit = self.size / 2
        right_limit = 800 - self.size / 2

        # 오른쪽 끝에서 방향 반전
        if boy.x >= right_limit:
            boy.x = right_limit
            boy.face_dir = -1

        # 왼쪽 끝에서 방향 반전
        elif boy.x <= left_limit:
            boy.x = left_limit
            boy.face_dir = 1

    def draw(self):
        boy = self.boy

        sprite_y = 100 if boy.face_dir == 1 else 0

        boy.image.clip_draw(
            int(boy.frame) * 100,
            sprite_y,
            100, 100,
            boy.x, boy.y,
            self.size, self.size
        )


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0.0
        self.face_dir = 1

        self.image = load_image('animation_sheet.png')

        self.left_pressed = False
        self.right_pressed = False
        self.speed = 250

        self.idle_start_time = get_time()
        self.last_update_time = get_time()

        self.autorun = AutoRun(self)

        self.machine = Machine(
            model=self,
            states=['IDLE', 'SLEEP', 'RUN', 'AUTORUN'],
            initial='IDLE',
            transitions=[
                {
                    'trigger': 'go_sleep',
                    'source': 'IDLE',
                    'dest': 'SLEEP',
                    'after': 'enter_sleep'
                },
                {
                    'trigger': 'wake_up',
                    'source': 'SLEEP',
                    'dest': 'IDLE',
                    'after': 'enter_idle'
                },
                {
                    'trigger': 'start_run',
                    'source': ['IDLE', 'SLEEP', 'AUTORUN'],
                    'dest': 'RUN',
                    'after': 'enter_run'
                },
                {
                    'trigger': 'stop_run',
                    'source': 'RUN',
                    'dest': 'IDLE',
                    'after': 'enter_idle'
                },
                {
                    'trigger': 'start_autorun',
                    'source': 'IDLE',
                    'dest': 'AUTORUN',
                    'after': 'enter_autorun'
                },
                {
                    'trigger': 'stop_autorun',
                    'source': 'AUTORUN',
                    'dest': 'IDLE',
                    'after': 'enter_idle'
                }
            ],
            auto_transitions=False
        )

        print('현재 상태: IDLE')

    def enter_idle(self):
        self.frame = 0
        self.idle_start_time = get_time()
        print('현재 상태: IDLE')

    def enter_sleep(self):
        self.frame = 0
        print('현재 상태: SLEEP')

    def enter_run(self):
        self.frame = 0
        print('현재 상태: RUN')

    def enter_autorun(self):
        self.autorun.enter()

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:

            if event.key == SDLK_a:
                if self.state == 'IDLE':
                    self.start_autorun()

            elif event.key == SDLK_SPACE:
                if self.state == 'SLEEP':
                    self.wake_up()

            elif event.key == SDLK_RIGHT:
                self.right_pressed = True
                self.face_dir = 1

                if self.state != 'RUN':
                    self.start_run()

            elif event.key == SDLK_LEFT:
                self.left_pressed = True
                self.face_dir = -1

                if self.state != 'RUN':
                    self.start_run()

        elif event.type == SDL_KEYUP:

            if event.key == SDLK_RIGHT:
                self.right_pressed = False

            elif event.key == SDLK_LEFT:
                self.left_pressed = False

            if self.state == 'RUN':
                if self.right_pressed:
                    self.face_dir = 1

                elif self.left_pressed:
                    self.face_dir = -1

                else:
                    self.stop_run()

    def update(self):
        now = get_time()
        dt = max(0.0, min(now - self.last_update_time, 0.05))
        self.last_update_time = now

        if self.state == 'IDLE':
            self.frame = (self.frame + 8 * dt) % 8

            if now - self.idle_start_time >= 5.0:
                self.go_sleep()

        elif self.state == 'SLEEP':
            # 누운 상태에서 애니메이션 반복
            self.frame = (self.frame + 8 * dt) % 8

        elif self.state == 'RUN':
            self.frame = (self.frame + 12 * dt) % 8

            direction = (
                int(self.right_pressed)
                - int(self.left_pressed)
            )

            self.x += direction * self.speed * dt
            self.x = max(50, min(750, self.x))

        elif self.state == 'AUTORUN':

            # AutoRun 진입 후 5초가 지나면 IDLE로 복귀
            elapsed_time = now - self.autorun.start_time

            if elapsed_time >= 5.0:
                self.stop_autorun()
            else:
                self.autorun.update(dt)

    def draw(self):
        frame = int(self.frame)

        if self.state == 'AUTORUN':
            self.autorun.draw()
            return

        elif self.state == 'IDLE':
            sprite_y = 300 if self.face_dir == 1 else 200

            self.image.clip_draw(
                frame * 100,
                sprite_y,
                100, 100,
                self.x, self.y
            )

        elif self.state == 'SLEEP':
            if self.face_dir == -1:
                self.image.clip_composite_draw(
                    frame * 100,
                    200,
                    100, 100,
                    -3.141592 / 2,
                    '',
                    self.x + 25,
                    self.y - 25,
                    100, 100
                )
            else:
                self.image.clip_composite_draw(
                    frame * 100,
                    300,
                    100, 100,
                    3.141592 / 2,
                    '',
                    self.x - 25,
                    self.y - 25,
                    100, 100
                )

        elif self.state == 'RUN':
            sprite_y = 100 if self.face_dir == 1 else 0

            self.image.clip_draw(
                frame * 100,
                sprite_y,
                100, 100,
                self.x, self.y
            )