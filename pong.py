import pygame
import random

pygame.init()

# Window Information
display_width = 800
display_height = 600
game_display = pygame.display.set_mode((display_width, display_height))

# Clock
game_clock = pygame.time.Clock()

# Load other things such as images and sound files here
# Use conver_alpha() for images with transparency
pong_paddle = pygame.image.load('pong_paddle.png')
pong_ball = pygame.image.load('pong_ball.png')
ghost_ball = pygame.image.load('ghost_ball.png')

paddle_width = 10
paddle_height = 200
paddle_gap = 50

ball_width = 10
ball_height = 10

# Max distance from centre of ball to centre of of paddle:
max_distance = paddle_height / 2 + ball_height / 2

menu_font = pygame.font.Font('freesansbold.ttf', 20)

white = (255, 255, 255)
black = (0, 0, 0)
red = (200, 0, 0)
bright_red = (250, 0, 0)
green = (0, 200, 0)
bright_green = (0, 250, 0)
blue = (0, 0, 200)
bright_blue = (0, 0, 250)


class MainRun:

    def __init__(self):

        self.win_screen = WinScreen()
        self.lose_screen = LoseScreen()
        self.pause_screen = PauseScreen()
        self.start_screen = StartScreen()
        self.mode_selection_screen = ModeSelectionScreen()
        self.difficulty_selection_screen = DifficultySelectionScreen()

        self.screen_names = {'win': self.win_screen,
                             'lose': self.lose_screen,
                             'pause': self.pause_screen,
                             'start': self.start_screen,
                             'mode': self.mode_selection_screen,
                             'diff': self.difficulty_selection_screen}

        self.single_player = SinglePlayer()
        self.play_ai = PlayComputer()
        self.two_player = TwoPlayer()

        self.current_game_mode = None
        self.current_difficulty = None

        self.call_title_screen(self.start_screen, None, False)

    def play_game(self):

        self.current_game_mode.set_vars(self.current_difficulty, self)

    def call_title_screen(self, screen_name, extra_text, display_things_or_not):

        print(2)

        selection = screen_name.draw_screen(extra_text, self.current_game_mode.ball, self.current_game_mode.user_paddle) \
            if display_things_or_not else screen_name.draw_screen(extra_text)

        if selection == 'restart':
            self.current_game_mode.set_vars(self.current_difficulty, self)
        elif selection == 'menu':
            self.call_mode_selection_screen(self.mode_selection_screen)
        elif selection == 'quit':
            pygame.quit()
            quit()
        elif selection == 'go':
            return
        else:
            raise NotImplementedError

    def call_mode_selection_screen(self, screen_name):

        print(3)

        selection = screen_name.draw_screen(None)

        if selection == 'sp':
            self.current_game_mode = self.single_player
        elif selection == 'ai':
            self.current_game_mode = self.play_ai
        elif selection == 'p2':
            self.current_game_mode = self.two_player
        else:
            raise NotImplementedError

        self.call_difficulty_selection_screen(self.difficulty_selection_screen)

    def call_difficulty_selection_screen(self, screen_name):

        print(4)

        selection = screen_name.draw_screen(None)
        self.current_difficulty = selection

        print('selection:', selection)

        self.play_game()


class GameModes:

    def set_vars(self, difficulty, controller):

        self.user_paddle = PlayerPaddle()
        self.ball = Ball()

        self.controller = controller

        self.y_change = 0
        self.up_pressed = False
        self.down_pressed = False

        self.user_score = 0

    def check_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.up_pressed = True
                elif event.key == pygame.K_DOWN:
                    self.down_pressed = True
                elif event.key == pygame.K_p:
                    try:
                        usr_txt = f"Your score is {self.user_score}"
                        ai_txt = f"The computer's score is {self.ai_score}"
                        self.controller.call_title_screen(
                            self.controller.pause_screen, [usr_txt, ai_txt], True)
                    except AttributeError:
                        try:
                            p1_txt = f"Player 1's score is {self.user_score}"
                            p2_txt = f"Player 2's score is {self.p2_score}"
                            self.controller.call_title_screen(
                                self.controller.pause_screen, [p1_txt, p2_txt], True)
                        except AttributeError:
                            usr_txt = f"Your score is {self.user_score}"
                            self.controller.call_title_screen(
                                self.controller.pause_screen, [usr_txt], True)

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.up_pressed = False
                elif event.key == pygame.K_DOWN:
                    self.down_pressed = False

    def move_user_paddle(self, distance):

        # If too far down and not going upwards:
        if self.user_paddle.y_pos >= self.user_paddle.y_max and distance > 0:
            self.user_paddle.out_of_bounds = True
        # If too far up and not going downwards:
        elif self.user_paddle.y_min >= self.user_paddle.y_pos and distance < 0:
            self.user_paddle.out_of_bounds = True
        else:
            self.user_paddle.out_of_bounds = False

        if not self.user_paddle.out_of_bounds:
            self.user_paddle.y_pos += distance

        self.user_paddle.display()

    def display_score(self, score, position):

        font = pygame.font.SysFont(None, 40)
        text = font.render(' '.join(['Score:', str(score)]), True, white)
        game_display.blit(text, position)

    # May remove restart method. It never gets called rn.

    # def restart(self):
    #
    #     self.user_paddle.__init__()
    #     self.ball.__init__()
    #
    #     self.ball.x_speed = abs(self.ball.x_speed)
    #
    #     self.play()


class SinglePlayer(GameModes):

    def set_vars(self, difficulty, controller):

        super().set_vars(difficulty, controller)

        if difficulty == 1:
            self.ball.x_speed = 10
        elif difficulty == 2:
            self.ball.x_speed = 12
        elif difficulty == 3:
            self.ball.x_speed = 15
        elif difficulty == 4:
            self.ball.x_speed = 20

        self.play()

    def play(self):

        while True:

            game_display.fill(black)

            self.check_events()

            if self.up_pressed is self.down_pressed:
                self.y_change = 0
            elif self.up_pressed:
                self.y_change = -5
            elif self.down_pressed:
                self.y_change = +5

            self.check_ball_safe()
            self.move_ball()
            self.move_user_paddle(self.y_change)
            self.display_score(self.user_score, (0, 0))

            pygame.display.update()
            game_clock.tick(60)

    def move_ball(self):

        # If too far right:
        if self.ball.x_pos >= self.ball.x_max:
            self.ball.x_speed *= -1
            self.ball.y_speed = random.randint(-6, 6)
            # self.ball.y_speed = 0
        # If too far left:
        elif self.ball.x_min >= self.ball.x_pos and not self.bypass:
            # To stop ball from disappearing off the screen when dying on hard mode. However, looks a little weird
            self.ball.x_pos = 0
            self.user_lose()

        # If too far down:
        if self.ball.y_pos >= self.ball.y_max:
            self.ball.y_speed = -abs(self.ball.y_speed)
        # If too far up:
        elif self.ball.y_min >= self.ball.y_pos:
            self.ball.y_speed = abs(self.ball.y_speed)

        self.ball.x_pos += self.ball.x_speed
        self.ball.y_pos += self.ball.y_speed

        if self.ball.x_pos >= self.user_paddle.x_pos + paddle_width + 10:
            self.bypass = False

        self.ball.display()

    def check_ball_safe(self):

        if self.user_paddle.x_pos + self.ball.x_speed / 2 <= self.ball.x_pos <= self.user_paddle.x_pos + paddle_width - self.ball.x_speed / 2:

            top_is_safe = self.ball.y_pos + ball_height >= self.user_paddle.y_pos
            bottom_is_safe = self.ball.y_pos <= self.user_paddle.y_pos + paddle_height

            if top_is_safe and bottom_is_safe and not self.bypass:

                centre_of_ball = self.ball.y_pos + ball_height / 2
                centre_of_paddle = self.user_paddle.y_pos + paddle_height / 2

                distance_hit = centre_of_paddle - centre_of_ball

                self.ball.x_speed = abs(self.ball.x_speed)
                self.ball.y_speed = distance_hit / \
                    max_distance * abs(self.ball.x_speed)
                print('ball y_speed:', self.ball.y_speed)
                print(self.bypass)
                self.bypass = True

                self.user_score += 1
                print('score =', self.user_score)

    def user_lose(self):
        usr_txt = f"Your score was {self.user_score}"
        self.controller.call_title_screen(
            self.controller.lose_screen, [usr_txt], True)


class PlayComputer(GameModes):

    def set_vars(self, difficulty, controller):

        super().set_vars(difficulty, controller)

        self.ai_paddle = AiPaddle()
        self.ghost_ball = GhostBall()

        self.ghost_ball_to_move = False

        self.ai_level = difficulty
        self.ghost_multiplier = difficulty / 2 + .5
        self.ball_x_speed = 9 + difficulty

        self.ball.x_speed = self.ball_x_speed
        self.ghost_ball.x_speed = 0

        self.ai_score = 0

        self.user_paddle.y_pos += random.choice((-2, -1, 1, 2))

        self.play()

    def play(self):

        while True:

            game_display.fill(black)

            self.check_events()

            if self.up_pressed is self.down_pressed:
                self.y_change = 0
            elif self.up_pressed:
                self.y_change = -5
            elif self.down_pressed:
                self.y_change = +5

            self.check_ball_safe()
            self.move_ball()
            self.move_ghost_ball()
            self.move_user_paddle(self.y_change)
            self.move_ai_paddle()
            self.display_score(self.user_score, (0, 0))
            self.display_score(self.ai_score, (display_width / 2, 0))

            if self.user_score >= 5:
                usr_txt = f"Your score was {self.user_score}"
                ai_txt = f"The computer's score was {self.ai_score}"
                self.controller.call_title_screen(
                    self.controller.win_screen, [usr_txt, ai_txt], False)
            elif self.ai_score >= 5:
                usr_txt = f"Your score was {self.user_score}"
                ai_txt = f"The computer's score was {self.ai_score}"
                self.controller.call_title_screen(
                    self.controller.lose_screen, [usr_txt, ai_txt], False)

            pygame.display.update()
            game_clock.tick(60)

    def reset(self):

        self.ball.x_pos = self.ghost_ball.x_pos = display_width / 2 - ball_width / 2
        self.ball.y_pos = self.ghost_ball.y_pos = display_height / 2 - ball_height / 2

        self.ball.x_speed = random.choice(
            (self.ball_x_speed, -self.ball_x_speed))
        self.ball.y_speed = 0

        self.user_paddle.y_pos = display_height * .5 - \
            paddle_height * .5 + random.choice((-2, -1, 1, 2))
        self.ai_paddle.y_pos = display_height * .5 - paddle_height * .5

    def move_ball(self):

        # If too far right:
        if self.ball.x_pos >= self.ball.x_max and not self.bypass:
            print('ai lose')
            self.ai_lose()
            self.reset()
        # If too far left:
        elif self.ball.x_min >= self.ball.x_pos and not self.bypass:
            print('user lose')
            self.user_lose()
            self.reset()

        # If too far down:
        if self.ball.y_pos >= self.ball.y_max:
            self.ball.y_speed = -abs(self.ball.y_speed)
        # If too far up:
        elif self.ball.y_min >= self.ball.y_pos:
            self.ball.y_speed = abs(self.ball.y_speed)

        self.ball.x_pos += self.ball.x_speed
        self.ball.y_pos += self.ball.y_speed

        if self.ball.x_pos >= self.user_paddle.x_pos + paddle_width + 50 >= self.user_paddle.x_pos + paddle_width + 10:
            self.bypass = False
        if self.ball.x_pos <= self.ai_paddle.x_pos - 50 <= self.ai_paddle.x_pos - 10:
            self.bypass = False

        self.ball.display()

    def move_ghost_ball(self):

        if self.ghost_ball_to_move:

            # If too far right or left:
            if self.ghost_ball.x_pos >= self.ghost_ball.x_max or self.ghost_ball.x_min >= self.ghost_ball.x_pos:
                self.ghost_ball_to_move = False
                self.ghost_ball.x_pos -= self.ghost_ball.x_speed
                self.ghost_ball.y_pos -= self.ghost_ball.y_speed
                self.ghost_ball.x_pos -= self.ghost_ball.x_speed
                self.ghost_ball.y_pos -= self.ghost_ball.y_speed
                # pass
            else:
                self.ghost_ball_to_move = True

            # If too far down:
            if self.ghost_ball.y_pos >= self.ghost_ball.y_max:
                self.ghost_ball.y_speed = -abs(self.ghost_ball.y_speed)
            # If too far up:
            elif self.ghost_ball.y_min >= self.ghost_ball.y_pos:
                self.ghost_ball.y_speed = abs(self.ghost_ball.y_speed)

            self.ghost_ball.x_pos += self.ghost_ball.x_speed
            self.ghost_ball.y_pos += self.ghost_ball.y_speed

        # self.ghost_ball.display()

    def check_ball_safe(self):

        if self.user_paddle.x_pos + self.ball.x_speed / 2 <= self.ball.x_pos <= self.user_paddle.x_pos + paddle_width - self.ball.x_speed / 2:

            top_is_safe = self.ball.y_pos + ball_height >= self.user_paddle.y_pos
            bottom_is_safe = self.ball.y_pos <= self.user_paddle.y_pos + paddle_height

            if top_is_safe and bottom_is_safe and not self.bypass:

                centre_of_ball = self.ball.y_pos + ball_height / 2
                centre_of_paddle = self.user_paddle.y_pos + paddle_height / 2

                distance_hit = centre_of_paddle - centre_of_ball

                self.ball.x_speed = abs(self.ball.x_speed)
                self.ball.y_speed = distance_hit / \
                    max_distance * abs(self.ball.x_speed)
                print('ball y_speed:', self.ball.y_speed)
                print('bypass?:', self.bypass)
                self.bypass = True

                self.controller.pause_screen.user_score = self.controller.lose_screen.user_score = self.user_score
                print('score =', self.user_score)

                self.ghost_ball_to_move = True
                self.ghost_ball.x_pos, self.ghost_ball.y_pos = self.ball.x_pos, self.ball.y_pos
                self.ghost_ball.x_speed, self.ghost_ball.y_speed = self.ball.x_speed * \
                    self.ghost_multiplier, self.ball.y_speed * self.ghost_multiplier

        elif self.ai_paddle.x_pos - self.ball.x_speed / 2 <= self.ball.x_pos <= self.ai_paddle.x_pos + paddle_width + self.ball.x_speed:

            top_is_safe = self.ball.y_pos + ball_height >= self.ai_paddle.y_pos
            bottom_is_safe = self.ball.y_pos <= self.ai_paddle.y_pos + paddle_height

            if top_is_safe and bottom_is_safe and not self.bypass:

                centre_of_ball = self.ball.y_pos + ball_height / 2
                centre_of_paddle = self.ai_paddle.y_pos + paddle_height / 2

                distance_hit = centre_of_paddle - centre_of_ball

                self.ball.x_speed = -abs(self.ball.x_speed)
                self.ball.y_speed = distance_hit / \
                    max_distance * -abs(self.ball.x_speed)
                print('ball y_speed:', self.ball.y_speed)
                print('bypass?:', self.bypass)
                self.bypass = True

                self.controller.pause_screen.ai_score = self.controller.lose_screen.ai_score = self.ai_score
                print('score =', self.ai_score)

                self.ghost_ball_to_move = True
                self.ghost_ball.x_pos, self.ghost_ball.y_pos = self.ball.x_pos, self.ball.y_pos
                self.ghost_ball.x_speed, self.ghost_ball.y_speed = self.ball.x_speed * \
                    self.ghost_multiplier, self.ball.y_speed * self.ghost_multiplier

    def move_ai_paddle(self):

        center_of_ghost_ball = self.ghost_ball.y_pos + ball_height / 2
        center_of_paddle = self.ai_paddle.y_pos + paddle_height / 2

        if center_of_ghost_ball > center_of_paddle + 20 * self.ai_level:
            # self.ai_paddle.y_pos += 3 + self.ai_level
            self.ai_paddle.y_pos += 4 + self.ai_level // 2
            # self.ai_paddle.y_pos += 5
        elif center_of_ghost_ball < center_of_paddle - 20 * self.ai_level:
            # self.ai_paddle.y_pos -= 3 + self.ai_level
            self.ai_paddle.y_pos -= 4 + self.ai_level // 2
            # self.ai_paddle.y_pos -= 5

        if self.ai_paddle.y_pos < self.ai_paddle.y_min:
            self.ai_paddle.y_pos = self.ai_paddle.y_min
        elif self.ai_paddle.y_pos > self.ai_paddle.y_max:
            self.ai_paddle.y_pos = self.ai_paddle.y_max

        self.ai_paddle.display()

    def user_lose(self):
        self.ai_score += 1

    def ai_lose(self):
        self.user_score += 1


class TwoPlayer(GameModes):

    def set_vars(self, difficulty, controller):

        super().set_vars(difficulty, controller)

        if difficulty == 1:
            self.ball.x_speed = 10
        elif difficulty == 2:
            self.ball.x_speed = 12
        elif difficulty == 3:
            self.ball.x_speed = 15
        elif difficulty == 4:
            self.ball.x_speed = 20

        self.p2_paddle = P2Paddle()

        self.p2_y_change = 0
        self.p2_up_pressed = False
        self.p2_down_pressed = False

        self.p2_score = 0

        self.play()

    def play(self):

        while True:

            game_display.fill(black)

            self.check_events()

            if self.up_pressed is self.down_pressed:
                self.y_change = 0
            elif self.up_pressed:
                self.y_change = -5
            elif self.down_pressed:
                self.y_change = +5

            if self.p2_up_pressed is self.p2_down_pressed:
                self.p2_y_change = 0
            elif self.p2_up_pressed:
                self.p2_y_change = -5
            elif self.p2_down_pressed:
                self.p2_y_change = +5

            self.check_ball_safe()
            self.move_ball()

            self.move_user_paddle(self.y_change)
            self.move_ai_paddle(self.p2_y_change)

            self.display_score(f'Player 1 score: {self.user_score}', (0, 0))
            self.display_score(
                f'Player 2 score: {self.p2_score}', (display_width / 2, 0))

            if self.user_score >= 5:
                usr_txt = f"Player 1's score was {self.user_score}"
                p2_txt = f"Plater 2's score was {self.p2_score}"
                self.controller.call_title_screen(
                    self.controller.win_screen, [usr_txt, p2_txt], False)
            elif self.p2_score >= 5:
                usr_txt = f"Player 1's score was {self.user_score}"
                p2_txt = f"Plater 2's score was {self.p2_score}"
                self.controller.call_title_screen(
                    self.controller.lose_screen, [usr_txt, p2_txt], False)

            pygame.display.update()
            game_clock.tick(60)

    def check_ball_safe(self):

        # if self.user_paddle.x_pos <= self.ball.x_pos <= self.user_paddle.x_pos + paddle_width:
        if self.user_paddle.x_pos + self.ball.x_speed / 2 <= self.ball.x_pos <= self.user_paddle.x_pos + paddle_width - self.ball.x_speed / 2:

            top_is_safe = self.ball.y_pos + ball_height >= self.user_paddle.y_pos
            bottom_is_safe = self.ball.y_pos <= self.user_paddle.y_pos + paddle_height

            if top_is_safe and bottom_is_safe and not self.bypass:

                centre_of_ball = self.ball.y_pos + ball_height / 2
                centre_of_paddle = self.user_paddle.y_pos + paddle_height / 2

                distance_hit = centre_of_paddle - centre_of_ball

                self.ball.x_speed = abs(self.ball.x_speed)
                self.ball.y_speed = distance_hit / \
                    max_distance * abs(self.ball.x_speed)
                print('ball y_speed:', self.ball.y_speed)
                print('bypass?:', self.bypass)
                self.bypass = True

                self.controller.pause_screen.user_score = self.controller.lose_screen.user_score = self.user_score
                print('score =', self.user_score)

        elif self.p2_paddle.x_pos - self.ball.x_speed / 2 <= self.ball.x_pos <= self.p2_paddle.x_pos + paddle_width + self.ball.x_speed:

            top_is_safe = self.ball.y_pos + ball_height >= self.p2_paddle.y_pos
            bottom_is_safe = self.ball.y_pos <= self.p2_paddle.y_pos + paddle_height

            if top_is_safe and bottom_is_safe and not self.bypass:

                centre_of_ball = self.ball.y_pos + ball_height / 2
                centre_of_paddle = self.p2_paddle.y_pos + paddle_height / 2

                distance_hit = centre_of_paddle - centre_of_ball

                self.ball.x_speed = -abs(self.ball.x_speed)
                self.ball.y_speed = distance_hit / \
                    max_distance * -abs(self.ball.x_speed)
                print('ball y_speed:', self.ball.y_speed)
                print('bypass?:', self.bypass)
                self.bypass = True

                self.controller.pause_screen.p2_score = self.controller.lose_screen.p2_score = self.p2_score
                print('score =', self.p2_score)

    def move_ball(self):

        # If too far right:
        if self.ball.x_pos >= self.ball.x_max and not self.bypass:
            print('p2 lose')
            self.p2_lose()
            self.reset()
        # If too far left:
        elif self.ball.x_min >= self.ball.x_pos and not self.bypass:
            print('user lose')
            self.user_lose()
            self.reset()

        # If too far down:
        if self.ball.y_pos >= self.ball.y_max:
            self.ball.y_speed = -abs(self.ball.y_speed)
        # If too far up:
        elif self.ball.y_min >= self.ball.y_pos:
            self.ball.y_speed = abs(self.ball.y_speed)

        self.ball.x_pos += self.ball.x_speed
        self.ball.y_pos += self.ball.y_speed

        if self.ball.x_pos >= self.user_paddle.x_pos + paddle_width + 50 >= self.user_paddle.x_pos + paddle_width + 10:
            self.bypass = False
        if self.ball.x_pos <= self.p2_paddle.x_pos - 50 <= self.p2_paddle.x_pos - 10:
            self.bypass = False

        self.ball.display()

    def check_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            elif event.type == pygame.KEYDOWN:

                # Player 1 keys:
                if event.key == pygame.K_UP:
                    self.up_pressed = True
                elif event.key == pygame.K_DOWN:
                    self.down_pressed = True

                # Player 2 keys:
                elif event.key == pygame.K_w:
                    self.p2_up_pressed = True
                elif event.key == pygame.K_s:
                    self.p2_down_pressed = True

                elif event.key == pygame.K_p:
                    p1_txt = f"Player 1's score is {self.user_score}"
                    p2_txt = f"Player 2's score is {self.p2_score}"
                    self.controller.call_title_screen(
                        self.controller.pause_screen, [p1_txt, p2_txt], True)

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.up_pressed = False
                elif event.key == pygame.K_DOWN:
                    self.down_pressed = False
                elif event.key == pygame.K_w:
                    self.p2_up_pressed = False
                elif event.key == pygame.K_s:
                    self.p2_down_pressed = False

    def move_ai_paddle(self, distance):

        # If too far down and not going upwards:
        if self.p2_paddle.y_pos >= self.p2_paddle.y_max and distance > 0:
            self.p2_paddle.out_of_bounds = True
        # If too far up and not going downwards:
        elif self.p2_paddle.y_min >= self.p2_paddle.y_pos and distance < 0:
            self.p2_paddle.out_of_bounds = True
        else:
            self.p2_paddle.out_of_bounds = False

        if not self.p2_paddle.out_of_bounds:
            self.p2_paddle.y_pos += distance

        self.p2_paddle.display()

    def reset(self):

        self.ball.x_pos = display_width / 2 - ball_width / 2
        self.ball.y_pos = display_height / 2 - ball_height / 2

        self.ball.x_speed = random.choice(
            (self.ball.x_speed, -self.ball.x_speed))
        self.ball.y_speed = 0

        self.user_paddle.y_pos = display_height * .5 - \
            paddle_height * .5 + random.choice((-2, -1, 1, 2))
        self.p2_paddle.y_pos = display_height * .5 - paddle_height * .5

    def user_lose(self):
        self.p2_score += 1

    def p2_lose(self):
        self.user_score += 1

    def display_score(self, score, position):

        font = pygame.font.SysFont(None, 40)
        text = font.render(score, True, white)
        game_display.blit(text, position)


class PaddleTemplate:

    def __init__(self):

        self.y_pos = display_height * .5 - paddle_height * .5

        self.y_min = 0
        self.y_max = display_height - paddle_height

        self.out_of_bounds = False

    def display(self):
        game_display.blit(pong_paddle, (self.x_pos, self.y_pos))


class PlayerPaddle(PaddleTemplate):

    def __init__(self):

        super().__init__()

        self.x_pos = paddle_gap

        self.display()


class AiPaddle(PaddleTemplate):

    def __init__(self):

        super().__init__()

        self.x_pos = display_width - paddle_width - paddle_gap

        self.display()


class P2Paddle(PaddleTemplate):

    def __init__(self):

        super().__init__()

        self.x_pos = display_width - paddle_width - paddle_gap

        self.display()


class BallTemplate:

    def __init__(self):

        self.x_pos = display_width / 2 - ball_width / 2
        self.y_pos = display_height / 2 - ball_height / 2

        self.x_min = 0
        self.x_max = display_width - ball_width

        self.y_min = 0
        self.y_max = display_height - ball_height

        self.y_speed = 0

        self.display()

    def display(self):
        game_display.blit(pong_ball, (self.x_pos, self.y_pos))


class Ball(BallTemplate):
    pass


class GhostBall(BallTemplate):

    def __init__(self):
        super().__init__()

        self.x_min = paddle_gap
        self.x_max = display_width - paddle_gap

    def display(self):
        game_display.blit(ghost_ball, (self.x_pos, self.y_pos))


class Screen:

    def __init__(self):

        self.paused = True

        self.small_button_length = 100
        self.small_button_height = 50

        self.med_button_length = 200
        self.med_button_height = 100

        self.p_key_allowed = True
        self.p_key_action = 'go_button'

    def display_button(self, button):

        pygame.draw.rect(*button)

    def get_text(self, txt_font, message, colour, bg_colour, txt_center):

        # This sets the font for the text
        font = pygame.font.Font(*txt_font)
        # This creates the text
        text = font.render(message, True, colour, bg_colour)
        # Creates a rectangle object for the text
        text_rect = text.get_rect()
        # This sets the text rectangle's centre
        text_rect.center = txt_center

        # This displays the text onto the text rectangle
        game_display.blit(text, text_rect)


class SelectionScreen(Screen):

    def __init__(self):
        super().__init__()

        self.information_box_length = 100
        self.information_box_height = 200

    def draw_screen(self, extra_text, *args):

        game_display.fill(black)

        for item in args:
            item.display()

        print(args)

        while self.paused:

            mouse = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_p) and self.p_key_allowed:
                        return self.button_actions[self.p_key_action]
                elif event.type == pygame.MOUSEBUTTONUP:
                    for button_name in self.button_names:
                        button_area = self.button_areas[button_name]
                        if button_area[0][0] < mouse[0] < button_area[0][1] and button_area[1][0] < mouse[1] < button_area[1][1]:
                            return self.button_actions[button_name]

            for button_name in self.button_names:
                button_area = self.button_areas[button_name]
                if button_area[0][0] < mouse[0] < button_area[0][1] and button_area[1][0] < mouse[1] < button_area[1][1]:
                    select_button = self.select_buttons[button_name]
                else:
                    select_button = self.unselect_buttons[button_name]
                self.display_button(select_button)

            self.write_text(extra_text)

            pygame.display.update()

            game_clock.tick(15)


class BasicTitleScreenTemplate(SelectionScreen):

    def __init__(self):
        super().__init__()

        self.create_item_info()

    def create_item_info(self):

        go_button_x = display_width * .175
        go_button_y = display_height * .7

        quit_button_x = display_width * .825 - self.small_button_length
        quit_button_y = display_height * .7

        self.go_button_center = (go_button_x + self.small_button_length / 2,
                                 go_button_y + self.small_button_height / 2)
        self.quit_button_center = (quit_button_x + self.small_button_length / 2,
                                   quit_button_y + self.small_button_height / 2)

        self.select_go_button = (game_display, bright_green, (go_button_x,
                                                              go_button_y, self.small_button_length, self.small_button_height))
        self.unselect_go_button = (game_display, green, (go_button_x,
                                                         go_button_y, self.small_button_length, self.small_button_height))

        self.select_quit_button = (game_display, bright_red, (quit_button_x,
                                                              quit_button_y, self.small_button_length, self.small_button_height))
        self.unselect_quit_button = (game_display, red, (quit_button_x,
                                                         quit_button_y, self.small_button_length, self.small_button_height))

        self.go_button_area = ((go_button_x, go_button_x + self.small_button_length),
                               (go_button_y, go_button_y + self.small_button_height))

        self.quit_button_area = ((quit_button_x, quit_button_x + self.small_button_length),
                                 (quit_button_y, quit_button_y + self.small_button_height))


class BasicTitleScreen(BasicTitleScreenTemplate):

    def __init__(self):
        super().__init__()

        self.add_item_info()

    def add_item_info(self):

        self.button_names = ['go_button', 'quit_button']

        self.button_areas = {'go_button': self.go_button_area,
                             'quit_button': self.quit_button_area}

        self.select_buttons = {'go_button': self.select_go_button,
                               'quit_button': self.select_quit_button}

        self.unselect_buttons = {'go_button': self.unselect_go_button,
                                 'quit_button': self.unselect_quit_button}

        self.button_centers = {'go_button': self.go_button_center,
                               'quit_button': self.quit_button_center}

        self.button_actions = {'go_button': 'menu',
                               'quit_button': 'quit'}


class ComplexTitleScreen(BasicTitleScreenTemplate):

    def __init__(self):
        super().__init__()

        self.add_item_info()

    def add_item_info(self):

        menu_button_x = display_width * .5 - self.small_button_length / 2
        menu_button_y = display_height * .7

        self.menu_button_center = (menu_button_x + self.small_button_length / 2,
                                   menu_button_y + self.small_button_height / 2)

        self.select_menu_button = (game_display, bright_blue, (menu_button_x,
                                                               menu_button_y, self.small_button_length, self.small_button_height))
        self.unselect_menu_button = (game_display, blue, (menu_button_x,
                                                          menu_button_y, self.small_button_length, self.small_button_height))

        self.menu_button_area = ((menu_button_x, menu_button_x + self.small_button_length),
                                 (menu_button_y, menu_button_y + self.small_button_height))

        self.button_names = ['go_button', 'menu_button', 'quit_button']

        self.button_areas = {'go_button': self.go_button_area,
                             'menu_button': self.menu_button_area,
                             'quit_button': self.quit_button_area}

        self.select_buttons = {'go_button': self.select_go_button,
                               'menu_button': self.select_menu_button,
                               'quit_button': self.select_quit_button}

        self.unselect_buttons = {'go_button': self.unselect_go_button,
                                 'menu_button': self.unselect_menu_button,
                                 'quit_button': self.unselect_quit_button}

        self.button_centers = {'go_button': self.go_button_center,
                               'menu_button': self.menu_button_center,
                               'quit_button': self.quit_button_center}

        self.button_actions = {'go_button': 'restart',
                               'menu_button': 'menu',
                               'quit_button': 'quit'}


class StartScreen(BasicTitleScreen):

    def __init__(self):
        super().__init__()

    def write_text(self, extra_text):
        self.get_text(('freesansbold.ttf', 20), 'Play!', black,
                      None, self.go_button_center)

        self.get_text(('freesansbold.ttf', 20), 'Quit.', black,
                      None, self.quit_button_center)

        self.get_text(('freesansbold.ttf', 100), 'Pong!', white,
                      black,  (display_width / 2, display_height * .4))


class WinScreen(ComplexTitleScreen):

    def __init__(self):
        super().__init__()

    def write_text(self, extra_text):
        self.get_text(('freesansbold.ttf', 20), 'Replay!', black,
                      None, self.go_button_center)

        self.get_text(('freesansbold.ttf', 20), 'Menu.', black,
                      None, self.menu_button_center)

        self.get_text(('freesansbold.ttf', 20), 'Quit.', black,
                      None, self.quit_button_center)

        self.get_text(('freesansbold.ttf', 100), 'You win!', white,
                      black,  (display_width / 2, display_height * (5 - len(extra_text)) / 10))

        for i, text in enumerate(extra_text):
            self.get_text(('freesansbold.ttf', 50), text, white,
                          black,  (display_width / 2, display_height * (7 - len(extra_text) + i) / 10))


class LoseScreen(ComplexTitleScreen):

    def __init__(self):
        super().__init__()

        self.user_score = 0

    def write_text(self, extra_text):
        self.get_text(('freesansbold.ttf', 20), 'Replay!', black,
                      None, self.go_button_center)

        self.get_text(('freesansbold.ttf', 20), 'Menu.', black,
                      None, self.menu_button_center)

        self.get_text(('freesansbold.ttf', 20), 'Quit.', black,
                      None, self.quit_button_center)

        self.get_text(('freesansbold.ttf', 100), 'You lose.', white,
                      black,  (display_width / 2, display_height * (5 - len(extra_text)) / 10))

        for i, text in enumerate(extra_text):
            self.get_text(('freesansbold.ttf', 50), text, white,
                          black,  (display_width / 2, display_height * (7 - len(extra_text) + i) / 10))


class PauseScreen(ComplexTitleScreen):

    def __init__(self):
        super().__init__()

        self.user_score = 0

        self.change_item_info()

    def change_item_info(self):

        self.button_actions = {'go_button': 'go',
                               'menu_button': 'menu',
                               'quit_button': 'quit'}

    def write_text(self, extra_text):
        self.get_text(('freesansbold.ttf', 20), 'Play!', black,
                      None, self.go_button_center)

        self.get_text(('freesansbold.ttf', 20), 'Menu.', black,
                      None, self.menu_button_center)

        self.get_text(('freesansbold.ttf', 20), 'Quit.', black,
                      None, self.quit_button_center)

        self.get_text(('freesansbold.ttf', 100), 'Paused!.', white,
                      black,  (display_width / 2, display_height * (5 - len(extra_text)) / 10))

        for i, text in enumerate(extra_text):
            self.get_text(('freesansbold.ttf', 50), text, white,
                          black,  (display_width / 2, display_height * (7 - len(extra_text) + i) / 10))


class ModeSelectionScreen(SelectionScreen):

    def __init__(self):
        super().__init__()

        self.p_key_allowed = False
        self.create_item_info()

    def create_item_info(self):

        sp_button_x = display_width * .1
        sp_button_y = display_height * .7

        ai_button_x = display_width * .5 - self.med_button_length / 2
        ai_button_y = display_height * .7

        p2_button_x = display_width * .9 - self.med_button_length
        p2_button_y = display_height * .7

        self.sp_button_center = (sp_button_x + self.med_button_length / 2,
                                 sp_button_y + self.small_button_height / 2)

        self.ai_button_center = (ai_button_x + self.med_button_length / 2,
                                 ai_button_y + self.small_button_height / 2)

        self.p2_button_center = (p2_button_x + self.med_button_length / 2,
                                 p2_button_y + self.small_button_height / 2)

        self.select_sp_button = (game_display, bright_green,
                                 (sp_button_x, sp_button_y,
                                  self.med_button_length, self.small_button_height))
        self.unselect_sp_button = (game_display, green,
                                   (sp_button_x, sp_button_y,
                                    self.med_button_length, self.small_button_height))

        self.select_ai_button = (game_display, bright_red,
                                 (ai_button_x, ai_button_y,
                                  self.med_button_length, self.small_button_height))
        self.unselect_ai_button = (game_display, red,
                                   (ai_button_x, ai_button_y,
                                    self.med_button_length, self.small_button_height))

        self.select_p2_button = (game_display, bright_blue,
                                 (p2_button_x, p2_button_y,
                                  self.med_button_length, self.small_button_height))
        self.unselect_p2_button = (game_display, blue,
                                   (p2_button_x, p2_button_y,
                                    self.med_button_length, self.small_button_height))

        self.sp_button_area = ((sp_button_x, sp_button_x + self.med_button_length),
                               (sp_button_y, sp_button_y + self.small_button_height))

        self.ai_button_area = ((ai_button_x, ai_button_x + self.med_button_length),
                               (ai_button_y, ai_button_y + self.small_button_height))

        self.p2_button_area = ((p2_button_x, p2_button_x + self.med_button_length),
                               (p2_button_y, p2_button_y + self.small_button_height))

        self.button_names = ['sp_button', 'ai_button', 'p2_button']

        self.button_areas = {'sp_button': self.sp_button_area,
                             'ai_button': self.ai_button_area,
                             'p2_button': self.p2_button_area}

        self.select_buttons = {'sp_button': self.select_sp_button,
                               'ai_button': self.select_ai_button,
                               'p2_button': self.select_p2_button}

        self.unselect_buttons = {'sp_button': self.unselect_sp_button,
                                 'ai_button': self.unselect_ai_button,
                                 'p2_button': self.unselect_p2_button}

        self.button_centers = {'sp_button': self.sp_button_center,
                               'ai_button': self.ai_button_center,
                               'p2_button': self.p2_button_center}

        self.button_actions = {'sp_button': 'sp',
                               'ai_button': 'ai',
                               'p2_button': 'p2'}

    def write_text(self, extra_text):
        self.get_text(('freesansbold.ttf', 100), 'Select the', white,
                      black,  (display_width / 2, display_height * .3))
        self.get_text(('freesansbold.ttf', 100), 'mode!', white,
                      black,  (display_width / 2, display_height * .5))

        self.get_text(('freesansbold.ttf', 20), 'Single Player!', black,
                      None, self.sp_button_center)

        self.get_text(('freesansbold.ttf', 20), 'Play the Computer!', black,
                      None, self.ai_button_center)

        self.get_text(('freesansbold.ttf', 20), 'Two Players!', black,
                      None, self.p2_button_center)


class DifficultySelectionScreen(SelectionScreen):

    def __init__(self):
        super().__init__()

        self.p_key_allowed = False
        self.create_item_info()

    def create_item_info(self):

        easy_button_x = display_width * .1
        easy_button_y = display_height * .7

        med_button_x = display_width * .5 - self.med_button_length / 2
        med_button_y = display_height * .7

        hard_button_x = display_width * .9 - self.med_button_length
        hard_button_y = display_height * .7

        extreme_button_x = display_width * .5 - self.med_button_length / 2
        extreme_button_y = display_height * .8

        self.easy_button_center = (easy_button_x + self.med_button_length / 2,
                                   easy_button_y + self.small_button_height / 2)

        self.med_button_center = (med_button_x + self.med_button_length / 2,
                                  med_button_y + self.small_button_height / 2)

        self.hard_button_center = (hard_button_x + self.med_button_length / 2,
                                   hard_button_y + self.small_button_height / 2)

        self.extreme_button_center = (extreme_button_x + self.med_button_length / 2,
                                      extreme_button_y + self.small_button_height / 2)

        self.select_easy_button = (game_display, bright_green,
                                   (easy_button_x, easy_button_y,
                                    self.med_button_length, self.small_button_height))
        self.unselect_easy_button = (game_display, green,
                                     (easy_button_x, easy_button_y,
                                      self.med_button_length, self.small_button_height))

        self.select_med_button = (game_display, bright_red,
                                  (med_button_x, med_button_y,
                                   self.med_button_length, self.small_button_height))
        self.unselect_med_button = (game_display, red,
                                    (med_button_x, med_button_y,
                                     self.med_button_length, self.small_button_height))

        self.select_hard_button = (game_display, bright_blue,
                                   (hard_button_x, hard_button_y,
                                    self.med_button_length, self.small_button_height))
        self.unselect_hard_button = (game_display, blue,
                                     (hard_button_x, hard_button_y,
                                      self.med_button_length, self.small_button_height))

        self.select_extreme_button = (game_display, white,
                                      (extreme_button_x, extreme_button_y,
                                       self.med_button_length, self.small_button_height))
        self.unselect_extreme_button = (game_display, white,
                                        (extreme_button_x, extreme_button_y,
                                         self.med_button_length, self.small_button_height))

        self.easy_button_area = ((easy_button_x, easy_button_x + self.med_button_length),
                                 (easy_button_y, easy_button_y + self.small_button_height))

        self.med_button_area = ((med_button_x, med_button_x + self.med_button_length),
                                (med_button_y, med_button_y + self.small_button_height))

        self.hard_button_area = ((hard_button_x, hard_button_x + self.med_button_length),
                                 (hard_button_y, hard_button_y + self.small_button_height))

        self.extreme_button_area = ((extreme_button_x, extreme_button_x + self.med_button_length),
                                    (extreme_button_y, extreme_button_y + self.small_button_height))

        self.button_names = ['easy_button', 'med_button',
                             'hard_button', 'extreme_button']

        self.button_areas = {'easy_button': self.easy_button_area,
                             'med_button': self.med_button_area,
                             'hard_button': self.hard_button_area,
                             'extreme_button': self.extreme_button_area}

        self.select_buttons = {'easy_button': self.select_easy_button,
                               'med_button': self.select_med_button,
                               'hard_button': self.select_hard_button,
                               'extreme_button': self.select_extreme_button}

        self.unselect_buttons = {'easy_button': self.unselect_easy_button,
                                 'med_button': self.unselect_med_button,
                                 'hard_button': self.unselect_hard_button,
                                 'extreme_button': self.unselect_extreme_button}

        self.button_centers = {'easy_button': self.easy_button_center,
                               'med_button': self.med_button_center,
                               'hard_button': self.hard_button_center,
                               'extreme_button': self.extreme_button_center}

        self.button_actions = {'easy_button': 1,
                               'med_button': 2,
                               'hard_button': 3,
                               'extreme_button': 4}

    def write_text(self, extra_text):
        self.get_text(('freesansbold.ttf', 100), 'Select the', white,
                      black,  (display_width / 2, display_height * .3))
        self.get_text(('freesansbold.ttf', 100), 'difficulty!', white,
                      black,  (display_width / 2, display_height * .5))

        self.get_text(('freesansbold.ttf', 20), 'Easy!', black,
                      None, self.easy_button_center)

        self.get_text(('freesansbold.ttf', 20), 'Medium', black,
                      None, self.med_button_center)

        self.get_text(('freesansbold.ttf', 20), 'Hard!', black,
                      None, self.hard_button_center)

        self.get_text(('freesansbold.ttf', 20), 'Extreme!', black,
                      None, self.extreme_button_center)


# Maybe have different controls and mouse control


# All player classes and object classes should be made outside of the main class and called inside the class
# The end of your code should look something like this
if __name__ == '__main__':
    # start = StartScreen()
    # start.draw_screen(None)

    run = MainRun()

    # test = ModeSelectionScreen()
    # test.draw_screen()


# for Pong AI:
'''
My favourite imperfect pong AI is brutally simple, yet lets one do some rather nice AI failure.

Invisible Ball AI

AI Setup: When the ball reflects off your paddle, you know where it is and how fast it is going. Spawn an invisible ball at that point but at a greater speed. It will wind up where the visible ball is going. Each frame, have the AI move towards the location of the invisible ball. Stop the invisible ball once it reaches the AI's side, so it is where the AI should move its paddle.

Results: The AI looks like it's trying to predict the path of the ball. Say the player has reflected the ball at a steep angle so that it will bounce off a wall. The AI will track the ball down a little ways, and then -- being slower than the ball -- will fail to track it back up fast enough. You have tricked the AI, and it looks fairly logical from a human point of view. You can see the computer trying to predict where the ball will go, and then -- oh, it missed, it was too slow, and you have won a point.

This is significantly better than inserting randomness, since it makes the AI look relatively intelligent. A worthy opponent. It also lets the AI play by the exact same rules as the human, which looks better to the player and makes your job easier.

Settings: You can also tweak the speed of the invisible ball, since that will determine how far ahead the AI will plan. The faster the invisible ball, the more time the paddle will have to move to block, and the better the player will have to aim.
'''
