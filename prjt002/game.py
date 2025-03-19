import tkinter as tk
import random
import time
import sys
import platform
import os  # 순위 저장을 위한 모듈 추가
import tkinter.simpledialog  # 이름 입력 대화 상자를 위한 모듈 추가
import openai  # OpenAI API 사용을 위한 모듈 추가

def check_environment():
    # Python 버전 확인
    python_version = sys.version_info
    if (python_version < (3, 6)):
        print(f"Error: Python 3.6 이상이 필요합니다. 현재 버전: {platform.python_version()}")
        sys.exit(1)

    # 운영 체제 확인
    os_name = platform.system()
    print(f"Operating System: {os_name}")
    print(f"Python Version: {platform.python_version()}")

    # tkinter 테스트
    try:
        root = tk.Tk()
        root.withdraw()  # 창 숨기기
        print("tkinter is properly installed.")
        root.destroy()
    except Exception as e:
        print("Error: tkinter가 설치되지 않았거나 제대로 작동하지 않습니다.")
        print(f"Details: {e}")
        sys.exit(1)

class AimTrainer:
    def __init__(self, root):
        self.root = root
        self.root.title("Aim Trainer")
        self.root.geometry("1024x768")  # 창 크기를 1024x768로 변경
        self.score = 0
        self.time_left = 30  # 게임 제한 시간 (초)
        self.target = None
        self.combo = 0  # 연속 히트 카운트
        self.high_scores_file = "high_scores.txt"  # 점수 저장 파일 경로

        # 점수 및 시간 표시
        self.score_label = tk.Label(root, text=f"Score: {self.score}", font=("Arial", 16))
        self.score_label.pack(pady=10)
        self.time_label = tk.Label(root, text=f"Time Left: {self.time_left}s", font=("Arial", 16))
        self.time_label.pack(pady=10)

        # 게임 시작 버튼
        self.start_button = tk.Button(root, text="Start Game", font=("Arial", 14), command=self.start_game)
        self.start_button.pack(pady=10)

        # 캔버스 생성
        self.canvas = tk.Canvas(root, width=1024, height=600, bg="white")  # 캔버스 크기 조정
        self.canvas.pack(pady=10)

        openai.api_key = "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"  # OpenAI API 키 설정

    def start_game(self):
        self.score = 0
        self.time_left = 30
        self.update_score()
        self.update_time()
        self.start_button.config(state=tk.DISABLED)
        self.spawn_target()
        self.countdown()

    def spawn_target(self):
        if self.target:
            self.canvas.delete(self.target)
        x = random.randint(50, 750)
        y = random.randint(50, 450)
        size = random.randint(15, 40)  # 공 크기 랜덤 (15~40)
        self.target_size = size  # 현재 공 크기 저장
        self.target = self.canvas.create_oval(x-size, y-size, x+size, y+size, fill="red", outline="")
        self.canvas.tag_bind(self.target, "<Button-1>", self.hit_target)

    def hit_target(self, event):
        base_score = 10  # 기본 점수
        size_bonus = max(0, 40 - self.target_size)  # 공 크기에 따른 보너스
        combo_bonus = self.combo * 2  # 연속 히트 보너스
        self.score += base_score + size_bonus + combo_bonus
        self.combo += 1  # 연속 히트 증가
        self.update_score()
        self.spawn_target()

    def update_score(self):
        self.score_label.config(text=f"Score: {self.score}")

    def update_time(self):
        self.time_label.config(text=f"Time Left: {self.time_left}s")

    def countdown(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.update_time()
            self.root.after(1000, self.countdown)
        else:
            self.combo = 0  # 시간 종료 시 콤보 초기화
            self.end_game()

    def end_game(self):
        self.canvas.delete(self.target)
        self.start_button.config(state=tk.NORMAL)
        self.combo = 0  # 게임 종료 시 콤보 초기화

        # 이름 입력 및 점수 저장
        name = self.get_player_name()
        self.save_score(name, self.score)

        # 순위 표시
        high_scores = self.load_high_scores()
        feedback = self.generate_feedback(name, self.score, high_scores)

        # 게임 결과를 tkinter 창에 표시
        self.canvas.delete("all")  # 캔버스 초기화
        message = f"Game Over!\nYour score: {self.score}\n\nHigh Scores:\n"
        for rank, (player, score) in enumerate(high_scores, start=1):
            message += f"{rank}. {player}: {score}\n"
        message += f"\nFeedback:\n{feedback}"
        self.canvas.create_text(
            512, 300,  # 캔버스 중앙에 텍스트 표시
            text=message,
            font=("Arial", 16),
            fill="black",
            justify="center"  # 텍스트 중앙 정렬
        )

    def generate_feedback(self, name, score, high_scores):
        # OpenAI API를 사용해 피드백 생성
        prompt = (
            f"플레이어 {name}님이 게임에서 {score}점을 기록했습니다. "
            f"다음은 상위 점수 목록입니다: {high_scores}. "
            "플레이어에게 동기부여가 되는 칭찬과 건설적인 피드백을 한국어로 제공해주세요."
        )
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=100
            )
            return response.choices[0].text.strip()
        except Exception as e:
            print(f"Error during OpenAI API call: {e}")  # 오류 메시지 출력
            return "현재 피드백을 생성할 수 없습니다. 나중에 다시 시도해주세요."

    def get_player_name(self):
        # 이름 입력 대화 상자
        name = tk.simpledialog.askstring("Name Entry", "Enter your name:")
        return name if name else "Anonymous"

    def save_score(self, name, score):
        # 점수를 파일에 저장
        with open(self.high_scores_file, "a") as file:
            file.write(f"{name},{score}\n")

    def load_high_scores(self):
        # 점수 파일 읽기 및 정렬
        if not os.path.exists(self.high_scores_file):
            return []
        with open(self.high_scores_file, "r") as file:
            scores = [line.strip().split(",") for line in file]
            scores = [(player, int(score)) for player, score in scores]
            scores.sort(key=lambda x: x[1], reverse=True)  # 점수 내림차순 정렬
        return scores[:10]  # 상위 10개만 반환

if __name__ == "__main__":
    check_environment()  # 환경 확인
    root = tk.Tk()
    game = AimTrainer(root)
    root.mainloop()
