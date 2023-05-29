import time
import RPi.GPIO as GPIO
from gpiozero import Robot


# PID 제어 상수
KP = 0.6  # 비례 제어 상수
KI = 0  # 적분 제어 상수
KD = 0  # 미분 제어 상수

# PID 제어 변수
setpoint = 25  # 목표 위치
error_prior = 0  # 이전 오차
integral = 0  # 누적 오차


# 초음파 센서에 연결된 GPIO 핀 번호
trig1 = 4 # peple distance
echo1 = 17
led_pin=26


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(trig1, GPIO.OUT)
GPIO.setup(echo1, GPIO.IN)
GPIO.setup(led_pin, GPIO.OUT)

# DC 모터 설정
motor_set1 = Robot(left=(18, 23), right=(24, 25))  # 첫 번째 세트의 모터 GPIO 핀 번호에 맞게 설정
motor_set2 = Robot(left=(12, 16), right=(20, 21))  # 두 번째 세트의 모터 GPIO 핀 번호에 맞게 설정


def led(label):
    if label == 2:
        for _ in range(5):
            GPIO.output(26, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(26, GPIO.LOW)
            time.sleep(0.5)
    return

	
	
# 거북목일 경우 앞으로 갔다가 다시 뒤로 감
def continue_posture() :
    print("Forward")
    motor_set1.forward(speed=0.5)
    motor_set2.forward(speed=0.5)
    time.sleep(0.8)
    motor_set1.stop()
    motor_set2.stop()
    #time.sleep(1)
    print("Backward")
    motor_set1.backward(speed=0.5)
    motor_set2.backward(speed=0.5)
    time.sleep(0.8)
    motor_set1.stop()
    motor_set2.stop()

# 초음파 거리 측정 함수
def sensor(TRIG, ECHO):
    global start_time, end_time
    
    GPIO.output(TRIG, False)
    time.sleep(0.1)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)        # 10uS의 펄스 발생을 위한 딜레이
    GPIO.output(TRIG, False)
    
    while GPIO.input(ECHO)==0:
        start_time = time.time()     # Echo핀 상승 시간값 저장
    while GPIO.input(ECHO)==1:
        end_time = time.time()      # Echo핀 하강 시간값 저장
        
    check_time = end_time - start_time
    
    distance = check_time * 34300 / 2

    return distance

def calculate_second(output):
    # 거리 계산을 위한 상수 설정
    circumference = 20  # 모터 바퀴의 둘레 (예시 값, 실제 값에 맞게 변경 필요)
    _rpm = 77/60 #초당 회전수 약 1.28바퀴 돈다
    wheel_rotation = output / circumference #output=이동할거
    time_to_move = wheel_rotation / _rpm * 2

    # 이동할 거리 계산
    #distance = output * (circumference * steps_per_revolution)

    return time_to_move

# PID 제어 함수
def calculate_pid(distance):
    global integral, error_prior
    # 오차 계산
    error = setpoint - distance
    print("setpont: ",setpoint,", distance: ", distance)
    
    if abs(error)>0.5:
        # PID 제어 계산
        proportional = KP * error
        integral += error
        derivative = error - error_prior
        
        output = proportional + (KI * integral) + (KD * derivative)
        
        # 오차 및 출력 값 업데이트
        error_prior = error
        #print("error_prior: ",error_prior)
        return output
    else :
        return 0

def dist_main():
    try:
        #setgpio()
        
        while True:
            distance = sensor(trig1, echo1) # 초음파 센서로부터 거리 측정
            print("Distance:", distance, "cm")
            if distance < 100: # PID 제어 계산
                output = calculate_pid(distance)
                if output>0:
                    print("backward")
                    # 이동할 거리 계산
                    second_to_move = calculate_second(output)
                    # 모터 이동
                    motor_set1.backward(speed=1)  # 왼쪽 모터
                    motor_set2.backward(speed=1)  # 오른쪽 모터
                    # 이동 완료까지 대기
                    time.sleep(second_to_move)  # 이동 속도에 맞게 대기
                    # 모터 정지
                    motor_set1.stop()
                    motor_set2.stop()
            
                elif output<0:
                    print("forward")
                    # 이동할 거리 계산
                    second_to_move = calculate_second(output)
                    # 모터 이동
                    motor_set1.forward(speed=1)  # 왼쪽 모터
                    motor_set2.forward(speed=1)  # 오른쪽 모터
                    
                    # 이동 완료까지 대기
                    time.sleep(abs(second_to_move))  # 이동 속도에 맞게 대기
                    # 모터 정지
                    motor_set1.stop()
                    motor_set2.stop()
                
                elif output == 0:
                    print("거리조절완료")
                    return True
                    break
    except KeyboardInterrupt:
        pass