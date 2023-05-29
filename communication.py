from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import uvicorn
from starlette.responses import JSONResponse
import sys
sys.path.append('/home/dacapo/DacapoHW/pid')
import distpid
import height_control_pid as PID


app = FastAPI()


# CORS 정책 설정
origins = [
	"http://localhost:3000",
	"http://192.168.137.1:3000",
	"http://192.168.137.237:3000"
]

app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"]
) 


@app.get("/rpi/reset")
async def height_reset(): # 높이 조절을 위한 reset
	PID.reset()
	return {
		"status" : 200,
		"message" : "height Reset success"
	}

@app.get("/rpi/dist") 
async def Start_Distance(): #거리조절 시작
	#distpid.setgpio()
	distpid.dist_main()
	time.sleep(1)
	PID.reset()
	return {
		"status" : 200,
		"message" : "Distance Control Success"
	}

@app.get("/rpi/led") #다리에 네임팬 칠한거가 파란색 줄이랑 연결됨
async def poture_led(label: int):
	distpid.led(label)
	return {
		"status" : 200,
		"message" : "led on/off"
	}
	
@app.get("/rpi/posture")
async def vdt(label: int):
	#앞으로 갔다가 뒤로 보냄
	print("label: ",label)
	if label == 1: # 거북목 자세
		distpid.continue_posture()
		return {
			"status" : 200,
			"message" : "Continuous Posture Management"
		}
	elif label == 2:	# 비뚤어진 자세
		distpid.led(label)
		return {
			"status" : 200,
			"message" : "disterded posture"
		}
	 
#움직여야 할 실제 거리(cm)
@app.get("/rpi/height") 
async def Start_Height(real_h: float): 
	#PID.reset()
	if real_h>=0:
		result= PID.exe_main(real_h)
		if result == "re":
			return {
				"status" : 200,
				"message" : "replay"
			}
		elif result == "suc":
			return {
				"status": 200,
				"message" : "success"
			}
	elif real_h<0:
		return {
			"status" : 200,
			"message" : "Don't step down"
		}
# async def Height_adjustment():